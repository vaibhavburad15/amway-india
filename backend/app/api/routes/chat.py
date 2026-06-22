"""
Chat / RAG chatbot routes.
"""
from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.ai.rag_service import answer_question
from app.api.deps import get_current_user
from app.db.mongodb import get_database
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat_message(payload: ChatRequest, user=Depends(get_current_user)):
    """Send a message to the AI chatbot. Uses RAG to ground in product DB."""
    session_id = payload.session_id or str(uuid.uuid4())

    # Generate answer
    result = await answer_question(payload.message)

    # Persist chat history (anonymous if no user)
    db = get_database()
    user_id = user["_id"] if user else None
    await db.chat_history.update_one(
        {"session_id": session_id},
        {
            "$setOnInsert": {
                "session_id": session_id,
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc),
            },
            "$push": {
                "messages": {
                    "$each": [
                        {
                            "role": "user",
                            "content": payload.message,
                            "timestamp": datetime.now(timezone.utc),
                        },
                        {
                            "role": "assistant",
                            "content": result["answer"],
                            "timestamp": datetime.now(timezone.utc),
                            "sources": result["sources"],
                        },
                    ]
                }
            },
        },
        upsert=True,
    )

    return ChatResponse(
        answer=result["answer"],
        session_id=session_id,
        sources=result["sources"],
    )


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    db = get_database()
    history = await db.chat_history.find_one({"session_id": session_id})
    if not history:
        return {"messages": [], "session_id": session_id}
    history["_id"] = str(history["_id"])
    return history
