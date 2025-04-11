from fastapi import APIRouter, HTTPException
from app.core.supabase import supabase_client
from app.models.models import ChatCreate, MessageCreate
from datetime import datetime
import uuid
import json
router = APIRouter()

@router.post("/chats")
async def create_chat(payload: ChatCreate):
    async with supabase_client() as client:
        # Check if users are matched
        match_check = await client.get("/match_history", params={
            "user_id": f"eq.{payload.user1_id}",
            "matched_user_id": f"eq.{payload.user2_id}"
        })
        if match_check.status_code != 200 or not match_check.json():
            raise HTTPException(status_code=403, detail="Users must be matched to start chat")

        # Check if chat already exists
        existing = await client.get("/chats", params={
            "or": f"(user1_id.eq.{payload.user1_id},user2_id.eq.{payload.user2_id}),(user1_id.eq.{payload.user2_id},user2_id.eq.{payload.user1_id})"
        })
        if existing.status_code == 200 and existing.json():
            return existing.json()[0]  # Return existing chat

        # Create new chat
        chat_data = {
            "id": str(uuid.uuid4()),
            "user1_id": payload.user1_id,
            "user2_id": payload.user2_id,
            "created_at": datetime.utcnow().isoformat()
        }
        res = await client.post("/chats", json=chat_data)

        if res.status_code not in (200, 201):
            raise HTTPException(status_code=400, detail="Chat creation failed")
        
        # Return the chat ID to the frontend for redirection
        return {"chat_id": chat_data["id"], "user1_id": payload.user1_id, "user2_id": payload.user2_id}



@router.post("/send_message")
async def send_message(payload: MessageCreate):
    async with supabase_client() as client:
        # Create the message
        data = {
            "chat_id": payload.chat_id,
            "sender_id": payload.sender_id,
            "receiver_id": payload.receiver_id,
            "content": payload.content,
            "created_at": datetime.utcnow().isoformat(),
        }

        res = await client.post("/messages", json=data)
        if res.status_code not in (200, 201):
            raise HTTPException(status_code=400, detail="Failed to send message")
        return {"message": "Message sent successfully"}


@router.get("/get_user_chats/{user_id}")
async def get_user_chats(user_id: str):
    async with supabase_client() as client:
        res = await client.post("/rpc/get_user_chats", json={"user_id": user_id})
        print(res.json())
        if res.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch user chats")

        return res.json()


@router.get("/get_chat_messages/{chat_id}")
async def get_chat_messages(chat_id: str):
    async with supabase_client() as client:
        res = await client.get("/messages", params={
            "chat_id": f"eq.{chat_id}",
            "order": "sent_at.asc"  # Use sent_at instead of timestamp if it's available
        })

        if res.status_code != 200:
            raise HTTPException(status_code=500, detail="Could not fetch messages")

        messages = res.json()
        print(res.json())
        if not messages:
            return {"message": "No messages found for this chat."}

        return messages
