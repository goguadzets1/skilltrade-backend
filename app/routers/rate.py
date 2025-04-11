from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.core.supabase import supabase_client
from app.models.models import RatingCreate

router = APIRouter()

@router.post("/rating")
async def submit_rating(payload: RatingCreate):
    async with supabase_client() as client:
        res = await client.post(
            "/ratings?on_conflict=from_user,to_user",
            json=payload.dict(),
            headers={"Prefer": "resolution=merge-duplicates"}
        )
        if res.status_code not in (200, 201):
            raise HTTPException(status_code=400, detail=res.text)
        return {"message": "Rating submitted"}


@router.get("/rating/{user_id}")
async def get_rating(user_id: str):
    async with supabase_client() as client:
        # Fetch profile
        profile_res = await client.get("/profiles", params={"id": f"eq.{user_id}"})
        profile_data = profile_res.json()[0] if profile_res.status_code == 200 and profile_res.json() else {}

        # Fetch skills_have
        have_res = await client.get("/profile_skills_have", params={"profile_id": f"eq.{user_id}"})
        want_res = await client.get("/profile_skills_want", params={"profile_id": f"eq.{user_id}"})
        profile_data["skills_have"] = [row["skill_id"] for row in have_res.json()] if have_res.status_code == 200 else []
        profile_data["skills_want"] = [row["skill_id"] for row in want_res.json()] if want_res.status_code == 200 else []

        # Fetch all skills (for frontend dropdown matching)
        skills_res = await client.get("/skills")
        skills = skills_res.json() if skills_res.status_code == 200 else []

        # Fetch ratings via RPC
        rpc_res = await client.post("/rpc/get_user_ratings_with_email", json={"user_id": user_id})
        if rpc_res.status_code != 200:
            raise HTTPException(status_code=rpc_res.status_code, detail="Failed to fetch ratings")

        ratings = rpc_res.json()
        stars = [r["stars"] for r in ratings]
        average = round(sum(stars) / len(stars), 2) if stars else 0

        return {
            **profile_data,
            "skills": skills,  # 👈 Add full skill list
            "average": average,
            "count": len(ratings),
            "entries": ratings
        }



@router.options("/rating", include_in_schema=False)
async def options_rate(request: Request):
    return JSONResponse(content={}, status_code=200)
