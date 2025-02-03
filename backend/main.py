from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI()

# CORS設定の更新
origins = [
    "https://sumichichi2015.github.io",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:3002"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データモデル
class Meeting(BaseModel):
    name: str
    organizer: str
    dates: List[str]
    start_time: str
    end_time: str
    created_at: Optional[str] = None

class Participant(BaseModel):
    name: str
    availability: dict
    comment: Optional[str] = None

# インメモリストレージ（本番環境では適切なデータベースに置き換え）
meetings = {}

@app.post("/meetings")
async def create_meeting(meeting: Meeting):
    try:
        meeting_id = str(uuid.uuid4())
        meeting_data = meeting.dict()
        meeting_data["id"] = meeting_id
        meeting_data["participants"] = []
        
        if not meeting_data.get("created_at"):
            meeting_data["created_at"] = datetime.now().isoformat()
        
        meetings[meeting_id] = meeting_data
        
        return {
            "id": meeting_id,
            "name": meeting_data["name"],
            "organizer": meeting_data["organizer"],
            "dates": meeting_data["dates"],
            "start_time": meeting_data["start_time"],
            "end_time": meeting_data["end_time"],
            "created_at": meeting_data["created_at"],
            "participants": []
        }
    except Exception as e:
        print(f"Error creating meeting: {str(e)}")
        raise HTTPException(status_code=500, detail="会議の作成に失敗しました")

@app.get("/meetings/{meeting_id}")
async def get_meeting(meeting_id: str):
    try:
        if meeting_id not in meetings:
            raise HTTPException(status_code=404, detail="会議が見つかりません")
        
        return meetings[meeting_id]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Error getting meeting: {str(e)}")
        raise HTTPException(status_code=500, detail="会議情報の取得に失敗しました")

@app.post("/meetings/{meeting_id}/participants")
async def add_participant(meeting_id: str, participant: Participant):
    try:
        if meeting_id not in meetings:
            raise HTTPException(status_code=404, detail="会議が見つかりません")
        
        participant_data = participant.dict()
        participant_data["registered_at"] = datetime.now().isoformat()
        
        meetings[meeting_id]["participants"].append(participant_data)
        
        return meetings[meeting_id]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Error adding participant: {str(e)}")
        raise HTTPException(status_code=500, detail="参加者の登録に失敗しました")
