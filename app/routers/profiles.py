from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from app.core.supabase import supabase_client
from app.models.models import ProfileUpdate
from app.utils.helpers import fetch_rating_for_user

DEFAULT_AVATAR_URL = "https://klxqydplupzqzgkmpnrz.supabase.co/storage/v1/object/public/avatars//default-avatar.jpg"


router = APIRouter()

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    async with supabase_client() as client:
        # Fetch profile
        profile_res = await client.get("/profiles", params={"select": "*", "id": f"eq.{user_id}"})
        data = profile_res.json()
        if not data:
            return {}

        user_profile = data[0]
        avatar_url = user_profile.get("avatar_url") or DEFAULT_AVATAR_URL

        rating = await fetch_rating_for_user(user_id)

        have_res = await client.get("/profile_skills_have", params={"profile_id": f"eq.{user_id}"})
        skills_have = [entry["skill_id"] for entry in have_res.json()]

        want_res = await client.get("/profile_skills_want", params={"profile_id": f"eq.{user_id}"})
        skills_want = [entry["skill_id"] for entry in want_res.json()]

        return {
            **user_profile,
            "avatar_url": avatar_url,
            "skills_have": skills_have,
            "skills_want": skills_want,
            "rating": rating
        }



@router.put("/profile")
async def update_profile(payload: ProfileUpdate):
    async with supabase_client() as client:
        profile_data = payload.dict()

        # Extract skill info separately
        skills_have = profile_data.pop("skills_have", [])
        skills_want = profile_data.pop("skills_want", [])

        if profile_data.get("avatar_url") == "":
            profile_data["avatar_url"] = DEFAULT_AVATAR_URL

        # Upsert profile (only valid columns)
        res = await client.post(
            "/profiles?on_conflict=id",
            json=profile_data,
            headers={"Prefer": "resolution=merge-duplicates"}
        )
        if res.status_code not in (200, 201):
            raise HTTPException(status_code=400, detail=res.text)

        # Clear existing skill mappings
        await client.delete("/profile_skills_have", params={"profile_id": payload.id})
        await client.delete("/profile_skills_want", params={"profile_id": payload.id})

        # Insert new skill mappings
        for skill_id in skills_have:
            await client.post("/profile_skills_have", json={"profile_id": payload.id, "skill_id": skill_id})
        for skill_id in skills_want:
            await client.post("/profile_skills_want", json={"profile_id": payload.id, "skill_id": skill_id})

        return {"message": "Profile upserted and skills updated"}






@router.options("/profile", include_in_schema=False)
async def options_profile(request: Request):
    return JSONResponse(content={}, status_code=200)