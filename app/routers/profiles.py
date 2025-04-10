from fastapi import APIRouter, HTTPException
from app.core.supabase import supabase_client
from app.models.models import ProfileUpdate

router = APIRouter()

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    async with supabase_client() as client:
        profile = await client.get("/profiles", params={"select": "*", "id": f"eq.{user_id}"})
        rating = await client.get(f"http://localhost:8000/rating/{user_id}")
        return {**profile.json()[0], "rating": rating.json()}

@router.put("/profile")
async def update_profile(payload: ProfileUpdate):
    async with supabase_client() as client:
        res = await client.post("/profiles", json=payload.dict())
        if res.status_code not in (200, 201):
            raise HTTPException(status_code=400, detail=res.text)
        return {"message": "Profile updated"}
