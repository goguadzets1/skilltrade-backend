from fastapi import APIRouter, HTTPException
from app.models.models import MatchHistoryCreate
from app.core.supabase import supabase_client
import uuid
from datetime import datetime

router = APIRouter()

@router.get("/match/{user_id}")
async def get_match_history(user_id: str):
    async with supabase_client() as client:
        res = await client.post("/rpc/raw_sql", json={
            "query": f"""
                select
                    mh.*,
                    mp.full_name as matched_user_name,
                    mp.avatar_url as matched_user_avatar,
                    r.stars as existing_rating,
                    r.feedback as existing_feedback
                from match_history mh
                left join profiles mp on mh.matched_user_id = mp.id
                left join ratings r on r.from_user = '{user_id}' and r.to_user = mh.matched_user_id
                where mh.user_id = '{user_id}'
                order by mh.matched_on desc
            """
        })

        if res.status_code != 200:
            print("❌ Error fetching match history:", res.text)
            raise HTTPException(status_code=500, detail="Failed to load match history")

        return res.json()


@router.post("/recalculate-matches/{user_id}")
async def recalculate_matches(user_id: str):
    async with supabase_client() as client:
        try:
            # Fetch other user IDs
            res = await client.get("/profiles", params={"select": "id"})
            others = [p["id"] for p in res.json() if p["id"] != user_id]

            # Fetch this user's skills
            skills_res = await client.get("/profile_skills_have", params={"profile_id": f"eq.{user_id}"})
            skills_have = set([s["skill_id"] for s in skills_res.json()])
            skills_res = await client.get("/profile_skills_want", params={"profile_id": f"eq.{user_id}"})
            skills_want = set([s["skill_id"] for s in skills_res.json()])

            # Clear old matches involving this user
            await client.delete("/match_history", params={"user_id": user_id})
            await client.delete("/match_history", params={"matched_user_id": user_id})

            for other_id in others:
                res_have = await client.get("/profile_skills_have", params={"profile_id": f"eq.{other_id}"})
                other_have = set([s["skill_id"] for s in res_have.json()])
                res_want = await client.get("/profile_skills_want", params={"profile_id": f"eq.{other_id}"})
                other_want = set([s["skill_id"] for s in res_want.json()])

                match_skills_1 = skills_have & other_want
                match_skills_2 = skills_want & other_have

                if match_skills_1 or match_skills_2:
                    timestamp = datetime.utcnow().isoformat()
                    await client.post("/match_history", json={
                        "id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "matched_user_id": other_id,
                        "matched_on": timestamp,
                        "created_at": timestamp
                    })
                    await client.post("/match_history", json={
                        "id": str(uuid.uuid4()),
                        "user_id": other_id,
                        "matched_user_id": user_id,
                        "matched_on": timestamp,
                        "created_at": timestamp
                    })

            return {"message": "Matches recalculated"}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Match recalculation failed: {e}")