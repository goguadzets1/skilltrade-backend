from fastapi import APIRouter
from app.core.supabase import supabase_client
from app.models.models import SkillCreate

router = APIRouter()

@router.get("/skills")
async def get_skills():
    async with supabase_client() as client:
        res = await client.get("/skills")
        return res.json()

@router.post("/skills")
async def add_skill(skill: SkillCreate):
    async with supabase_client() as client:
        res = await client.post("/skills", json=skill.dict())
        return res.json()
