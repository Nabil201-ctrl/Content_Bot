from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..controllers.chat_controller import handle_chat

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


@router.post("/chat")
async def chat_endpoint(request: Request, body: ChatRequest):
    db = request.app.state.db
    if not body.message:
        raise HTTPException(status_code=400, detail="message is required")
    
    # If DB is available, use it; otherwise return mock response
    if not db:
        from ..services.ai_client import ai_client
        resp = await ai_client.generate_reply(body.message, context=[], trends=[])
        return {
            "session_id": "test-session",
            "reply": resp.get("reply"),
            "suggestions": resp.get("suggestions", []),
            "trends": [],
            "should_suggest": resp.get("should_suggest", False)
        }
    
    resp = await handle_chat(db, body.message, session_id=body.session_id)
    return resp


@router.get("/chat/history")
async def chat_history(request: Request, session_id: Optional[str] = None):
    db = request.app.state.db
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    if session_id:
        return {"history": await db.chats.find_one({"_id": session_id})}
    # return last N sessions (simple)
    cursor = db.chats.find().sort("updated_at", -1).limit(20)
    items = []
    async for doc in cursor:
        # return minimal view
        items.append({"session_id": str(doc.get("_id")), "messages": doc.get("messages", [])})
    return {"history": items}
