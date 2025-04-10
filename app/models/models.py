from pydantic import BaseModel
from typing import List, Optional

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

class MatchResult(BaseModel):
    id: str
    full_name: str
    bio: Optional[str]
    matched_skills: int
