from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.core.supabase import supabase_client
from app.utils.helpers import fetch_rating_for_user
from app.models.models import ProfileUpdate

DEFAULT_AVATAR_URL = "https://klxqydplupzqzgkmpnrz.supabase.co/storage/v1/object/public/avatars/default-avatar.jpg"

router = APIRouter()

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    async with supabase_client() as client:
        # Fetch profile info
        profile_res = await client.get("/profiles", params={"id": f"eq.{user_id}"})
        profile_data = profile_res.json()[0] if profile_res.status_code == 200 and profile_res.json() else {}

        # Fetch skills_have and skills_want from join tables
        have_res = await client.get("/profile_skills_have", params={"select": "skill_id", "profile_id": f"eq.{user_id}"})
        want_res = await client.get("/profile_skills_want", params={"select": "skill_id", "profile_id": f"eq.{user_id}"})

        skills_have = [entry["skill_id"] for entry in have_res.json()] if have_res.status_code == 200 else []
        skills_want = [entry["skill_id"] for entry in want_res.json()] if want_res.status_code == 200 else []

        # Fetch rating
        from app.utils.helpers import fetch_rating_for_user
        rating = await fetch_rating_for_user(user_id)

        return {
            **profile_data,
            "skills_have": skills_have,
            "skills_want": skills_want,
            "rating": rating
        }


@router.put("/profile")
async def update_profile(payload: ProfileUpdate):
    async with supabase_client() as client:
        profile_data = {
            "id": payload.id,
            "full_name": payload.full_name,
            "bio": payload.bio,
            "avatar_url": payload.avatar_url or DEFAULT_AVATAR_URL
        }

        res = await client.post(
            "/profiles?on_conflict=id",
            json=profile_data,
            headers={"Prefer": "resolution=merge-duplicates"}
        )
        if res.status_code not in (200, 201):
            raise HTTPException(status_code=400, detail=res.text)

        await client.delete("/profile_skills_have", params={"profile_id": payload.id})
        await client.delete("/profile_skills_want", params={"profile_id": payload.id})

        for skill_id in payload.skills_have:
            await client.post("/profile_skills_have", json={"profile_id": payload.id, "skill_id": skill_id})
        for skill_id in payload.skills_want:
            await client.post("/profile_skills_want", json={"profile_id": payload.id, "skill_id": skill_id})

        return {"message": "Profile upserted and skills updated"}



@router.options("/profile", include_in_schema=False)
async def options_profile(request: Request):
    return JSONResponse(content={}, status_code=200)
