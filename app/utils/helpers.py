from app.core.supabase import supabase_client

def flatten_ids(data: list, field="skill_id") -> list:
    return [row[field] for row in data if field in row]

async def fetch_rating_for_user(user_id: str):
    async with supabase_client() as client:
        res = await client.get("/ratings", params={"select": "stars", "to_user": f"eq.{user_id}"})
        ratings = res.json()
        if not ratings:
            return {"average": 0, "count": 0}
        stars = [r["stars"] for r in ratings]
        return {"average": sum(stars) / len(stars), "count": len(stars)}
