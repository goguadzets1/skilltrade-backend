from fastapi import APIRouter
from fastapi.responses import JSONResponse
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

@router.options("/skills", include_in_schema=False)
async def options_skills(request: Request):
    return JSONResponse(content={}, status_code=200)
