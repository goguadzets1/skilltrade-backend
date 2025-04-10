from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from app.core.supabase import supabase_client
from app.models.models import Rating

router = APIRouter()

@router.post("/rate")
async def rate_user(payload: Rating):
    async with supabase_client() as client:
        res = await client.post("/ratings", json=payload.dict())
        if res.status_code != 201:
            raise HTTPException(status_code=400, detail=res.text)
        return {"message": "Rating submitted"}

@router.get("/rating/{user_id}")
async def get_rating(user_id: str):
    async with supabase_client() as client:
        res = await client.get("/ratings", params={"select": "stars", "to_user": f"eq.{user_id}"})
        ratings = res.json()
        if not ratings:
            return {"average": 0, "count": 0}
        stars = [r["stars"] for r in ratings]
        return {"average": sum(stars) / len(stars), "count": len(stars)}

@router.options("/rate", include_in_schema=False)
async def options_rate(request: Request):
    return JSONResponse(content={}, status_code=200)
