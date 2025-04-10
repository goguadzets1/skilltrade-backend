from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from app.core.supabase import supabase_client
from app.models.models import ProfileUpdate
from app.utils.helpers import fetch_rating_for_user

router = APIRouter()

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    async with supabase_client() as client:
        profile = await client.get("/profiles", params={"select": "*", "id": f"eq.{user_id}"})
        data = profile.json()
        if not data:
            return {}
        rating = await fetch_rating_for_user(user_id)
        return {**data[0], "rating": rating}

@router.put("/profile")
async def update_profile(payload: ProfileUpdate):
    async with supabase_client() as client:
        # First, update the profile (basic details)
        res = await client.post(
            "/profiles?on_conflict=id",
            json=payload.dict(),
            headers={"Prefer": "resolution=merge-duplicates"}
        )
        if res.status_code not in (200, 201):
            raise HTTPException(status_code=400, detail=res.text)

        # Clear existing skills first
        await client.delete("/profile_skills_have", params={"profile_id": payload.id})
        await client.delete("/profile_skills_want", params={"profile_id": payload.id})

        # Insert new skills into profile_skills_have
        for skill_id in payload.skills_have:
            await client.post("/profile_skills_have", json={"profile_id": payload.id, "skill_id": skill_id})

        # Insert new skills into profile_skills_want
        for skill_id in payload.skills_want:
            await client.post("/profile_skills_want", json={"profile_id": payload.id, "skill_id": skill_id})

        return {"message": "Profile upserted and skills updated"}




@router.options("/profile", include_in_schema=False)
async def options_profile(request: Request):
    return JSONResponse(content={}, status_code=200)