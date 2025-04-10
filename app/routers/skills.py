from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from app.core.supabase import supabase_client
from app.models.models import SkillCreate

router = APIRouter()

@router.get("/skills")
async def get_skills():
    async with supabase_client() as client:
        res = await client.get("/skills")
        try:
            return res.json()
        except Exception:
            return JSONResponse(content={"error": "Failed to parse skills response"}, status_code=500)

@router.post("/skills")
async def add_skill(skill: SkillCreate):
    async with supabase_client() as client:
        res = await client.post("/skills?on_conflict=name", json=skill.dict())

        if res.status_code not in (200, 201):
            raise HTTPException(status_code=400, detail=res.text)

        try:
            return res.json()
        except Exception:
            return JSONResponse(
                content={"message": "Skill inserted/updated, but no response body"},
                status_code=res.status_code
            )

@router.options("/skills", include_in_schema=False)
async def options_skills(request: Request):
    return JSONResponse(content={}, status_code=200)
