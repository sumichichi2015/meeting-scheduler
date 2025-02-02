from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Meeting(BaseModel):
    name: str
    organizer: str
    dates: List[str]
    start_time: str
    end_time: str

class Participant(BaseModel):
    name: str
    comment: Optional[str] = None
    availability: Dict[str, str]

class MeetingResponse(Meeting):
    id: str
    participants: List[Participant] = []

meetings: Dict[str, MeetingResponse] = {}

@app.post("/meetings", response_model=MeetingResponse)
async def create_meeting(meeting: Meeting):
    meeting_id = str(uuid.uuid4())
    meeting_data = MeetingResponse(
        id=meeting_id,
        name=meeting.name,
        organizer=meeting.organizer,
        dates=meeting.dates,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        participants=[]
    )
    meetings[meeting_id] = meeting_data
    return meeting_data

@app.get("/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: str):
    if meeting_id not in meetings:
        raise HTTPException(status_code=404, detail="会議が見つかりません")
    return meetings[meeting_id]

@app.post("/meetings/{meeting_id}/participants", response_model=Participant)
async def add_participant(meeting_id: str, participant: Participant):
    if meeting_id not in meetings:
        raise HTTPException(status_code=404, detail="会議が見つかりません")
    
    # 同じ名前の参加者がいないかチェック
    for existing_participant in meetings[meeting_id].participants:
        if existing_participant.name == participant.name:
            raise HTTPException(status_code=400, detail="同じ名前の参加者が既に存在します")
    
    meetings[meeting_id].participants.append(participant)
    return participant
