from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from app.core.supabase import supabase_client
from app.models.models import SkillCreate

router = APIRouter()

@router.get("/skills")
async def get_skills(user_id: str = None):
    async with supabase_client() as client:
        # Always fetch all skills
        res_all = await client.get("/skills")
        try:
            all_skills = res_all.json()
        except Exception:
            return JSONResponse(content={"error": "Failed to parse skills"}, status_code=500)

        # If no user_id, return just the full list
        if not user_id:
            return {"all": all_skills}

        # Fetch user's skills_have and skills_want
        res_have = await client.get("/profile_skills_have", params={"profile_id": f"eq.{user_id}"})
        res_want = await client.get("/profile_skills_want", params={"profile_id": f"eq.{user_id}"})

        try:
            have = [entry["skill_id"] for entry in res_have.json()]
            want = [entry["skill_id"] for entry in res_want.json()]
        except Exception:
            have, want = [], []

        return {
            "all": all_skills,
            "skills_have": have,
            "skills_want": want
        }


@router.post("/skills")
async def add_skill(skill: SkillCreate):
    async with supabase_client() as client:
        res = await client.post(
            "/skills?on_conflict=name",
            json=skill.dict(),
            headers={"Prefer": "resolution=merge-duplicates"}
        )
        if res.status_code not in (200, 201):
            raise HTTPException(status_code=400, detail=res.text)
        try:
            return res.json()
        except Exception:
            return {"message": "Skill added or already exists"}


@router.options("/skills", include_in_schema=False)
async def options_skills(request: Request):
    return JSONResponse(content={}, status_code=200)
