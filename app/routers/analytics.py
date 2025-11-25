# routers/analytics.py
from fastapi import APIRouter, Request, HTTPException
from typing import Optional
from ..controllers.chat_controller import get_chat_analytics

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/session/{session_id}")
async def get_session_analytics(request: Request, session_id: str):
    db = request.app.state.db
    return await get_chat_analytics(db, session_id)

@router.get("/trends/instagram")
async def get_instagram_trends(request: Request):
    db = request.app.state.db
    try:
        from ..services.scraper import fetch_instagram_trends
        trends = await fetch_instagram_trends()
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Instagram trends: {str(e)}")