from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
import fcntl
import uuid
from datetime import datetime, timedelta
import random
import string

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データディレクトリの設定
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# モデル定義
class Meeting(BaseModel):
    id: Optional[str] = None
    name: str
    organizer: str
    dates: List[str]
    time_slots: Dict[str, List[str]]
    participants: List[Dict] = []

class Participant(BaseModel):
    name: str
    availability: Dict[str, Dict[str, str]]
    comment: Optional[str] = None

def generate_meeting_id() -> str:
    """安全な会議IDを生成"""
    return str(uuid.uuid4())

def save_meeting(meeting_id: str, data: dict):
    """会議データを保存"""
    filepath = os.path.join(DATA_DIR, f"{meeting_id}.json")
    with open(filepath, "w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX)  # 排他ロック（書き込み用）
            json.dump(data, f, ensure_ascii=False, indent=2)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)  # ロック解除

def load_meeting(meeting_id: str) -> Optional[dict]:
    """会議データを読み込み"""
    filepath = os.path.join(DATA_DIR, f"{meeting_id}.json")
    try:
        with open(filepath, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)  # 共有ロック（読み取り用）
            data = json.load(f)
            fcntl.flock(f, fcntl.LOCK_UN)  # ロック解除
            return data
    except FileNotFoundError:
        return None

@app.post("/meetings")
async def create_meeting(meeting: Meeting):
    """会議を作成"""
    # UUIDベースの会議ID生成
    meeting_id = generate_meeting_id()
    meeting.id = meeting_id
    
    # 会議データを保存
    meeting_data = meeting.dict()
    meeting_data["created_at"] = datetime.now().isoformat()
    meeting_data["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
    save_meeting(meeting_id, meeting_data)
    
    return {
        "meeting_id": meeting_id,
        "join_url": f"/meetings/{meeting_id}"  # フロントエンドで使用するURL
    }

@app.get("/meetings/{meeting_id}")
async def get_meeting(meeting_id: str):
    """会議情報を取得"""
    meeting_data = load_meeting(meeting_id)
    if meeting_data is None:
        raise HTTPException(status_code=404, detail="会議が見つかりません")
    return meeting_data

@app.post("/meetings/{meeting_id}/participants")
async def add_participant(meeting_id: str, participant: Participant):
    """参加者を追加"""
    meeting_data = load_meeting(meeting_id)
    if meeting_data is None:
        raise HTTPException(status_code=404, detail="会議が見つかりません")
    
    # 参加者数の制限（15名まで）
    if len(meeting_data["participants"]) >= 15:
        raise HTTPException(status_code=400, detail="参加者数が上限に達しました")
    
    # 参加者を追加
    meeting_data["participants"].append({
        "name": participant.name,
        "availability": participant.availability,
        "comment": participant.comment,
        "joined_at": datetime.now().isoformat()
    })
    save_meeting(meeting_id, meeting_data)
    
    return {"status": "success"}

@app.get("/meetings/{meeting_id}/participants")
async def get_participants(meeting_id: str):
    """参加者一覧を取得"""
    meeting_data = load_meeting(meeting_id)
    if meeting_data is None:
        raise HTTPException(status_code=404, detail="会議が見つかりません")
    return {"participants": meeting_data["participants"]}
