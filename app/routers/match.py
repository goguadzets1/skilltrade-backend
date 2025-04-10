from fastapi import APIRouter, Query
from app.core.supabase import supabase_client
from app.utils.helpers import flatten_ids

router = APIRouter()

@router.get("/match")
async def match_users(user_id: str):
    async with supabase_client() as client:
        want = await client.get("/profile_skills_want", params={"select": "skill_id", "profile_id": f"eq.{user_id}"})
        want_ids = flatten_ids(want.json())

        have_all = await client.get("/profile_skills_have", params={"select": "profile_id,skill_id"})
        have_data = have_all.json()

        # Match logic
        match_scores = {}
        for row in have_data:
            pid = row['profile_id']
            if pid == user_id:
                continue
            if row['skill_id'] in want_ids:
                match_scores[pid] = match_scores.get(pid, 0) + 1

        profiles = await client.get("/profiles")
        profile_map = {p['id']: p for p in profiles.json()}

        return [
            {
                "id": pid,
                "full_name": profile_map[pid]["full_name"],
                "bio": profile_map[pid].get("bio", ""),
                "matched_skills": score
            }
            for pid, score in match_scores.items() if pid in profile_map
        ]
