from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
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
        query = (
            "rpc:get_user_ratings_with_email" 
        )
        res = await client.get(f"/{query}", params={"user_id": user_id})
        if res.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch ratings")

        ratings = res.json()
        if not ratings:
            return {"average": 0, "count": 0, "entries": []}

        stars = [r["stars"] for r in ratings]
        return {
            "average": round(sum(stars) / len(stars), 2),
            "count": len(stars),
            "entries": ratings  # full list for frontend
        }

@router.options("/rate", include_in_schema=False)
async def options_rate(request: Request):
    return JSONResponse(content={}, status_code=200)
