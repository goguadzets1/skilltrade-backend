from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Rating(BaseModel):
    from_user: str
    to_user: str
    stars: int
    feedback: Optional[str] = ""

class SkillCreate(BaseModel):
    name: str

class ProfileUpdate(BaseModel):
    id: str
    full_name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    skills_have: List[str] = []
    skills_want: List[str] = []

class RatingCreate(BaseModel):
    from_user: str   
    to_user: str
    stars: int
    feedback: Optional[str] = None

class MatchHistoryCreate(BaseModel):
    user_id: str
    matched_user_id: str
    session_notes: Optional[str] = None

class MatchHistoryEntry(BaseModel):
    id: str
    user_id: str
    matched_user_id: str
    matched_on: datetime
    session_notes: Optional[str]
    created_at: datetime

class ChatCreate(BaseModel):
    user1_id: str
    user2_id: str

class MessageCreate(BaseModel):
    chat_id: str
    sender_id: str
    receiver_id: str
    content: str