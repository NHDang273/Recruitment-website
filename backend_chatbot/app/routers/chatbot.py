from fastapi import APIRouter, HTTPException
from app.services.chatbot_service import process_message

router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot"]
)

@router.post("/message")
async def chat_with_bot(user_message: str):
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    bot_response = process_message(user_message)
    return {"user_message": user_message, "bot_response": bot_response}
