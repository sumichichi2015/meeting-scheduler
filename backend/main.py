from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from database import db
import uuid

app = FastAPI()

origins = [
    "https://sumichichi2015.github.io",  # GitHub Pages
    "http://localhost:5173",  # 開発環境
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Meeting(BaseModel):
    name: str
    description: Optional[str] = None
    organizer: str
    dates: List[str]
    time_slots: Dict[str, List[str]]

@app.post("/meetings")
async def create_meeting(meeting: Meeting):
    meeting_id = str(uuid.uuid4())
    meeting_data = meeting.dict()
    meeting_data["participants"] = []
    db.create_meeting(meeting_id, meeting_data)
    return {"id": meeting_id, **meeting_data}

@app.get("/meetings/{meeting_id}")
async def get_meeting(meeting_id: str):
    meeting = db.get_meeting(meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="会議が見つかりません")
    return meeting

class Participant(BaseModel):
    name: str
    availability: Dict[str, Dict[str, str]]

@app.post("/meetings/{meeting_id}/participants")
async def add_participant(meeting_id: str, participant: Participant):
    meeting = db.get_meeting(meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="会議が見つかりません")
    
    meeting["participants"].append(participant.dict())
    db.update_meeting(meeting_id, meeting)
    return meeting
