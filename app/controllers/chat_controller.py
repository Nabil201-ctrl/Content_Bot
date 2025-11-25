# controllers/chat_controller.py
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
import asyncio
import logging

from ..services import ai_client, scraper

logger = logging.getLogger(__name__)

async def handle_chat(db, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Enhanced chat handler with complete conversation logging"""
    
    try:
        # Find or create session
        session, session_id = await _get_or_create_session(db, session_id)
        
        # Save user message with metadata
        await _save_user_message(db, session["_id"], message)
        
        # Get comprehensive trends
        try:
            trends = await asyncio.wait_for(
                scraper.fetch_trending_formats(), 
                timeout=8.0
            )
        except asyncio.TimeoutError:
            logger.warning("Trend analysis timeout")
            trends = []
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            trends = []
        
        # Get conversation context
        context = session.get("messages", [])
        
        # Generate AI response
        ai_resp = await ai_client.generate_reply(
            message=message, 
            context=context, 
            trends=trends
        )
        
        # Save assistant message with full response data
        await _save_assistant_message(db, session["_id"], ai_resp)
        
        # Log detailed interaction for analytics
        await _log_detailed_interaction(db, session_id, message, ai_resp, trends)
        
        return {
            "session_id": str(session_id),
            "reply": ai_resp.get("reply"),
            "suggestions": ai_resp.get("suggestions", []),
            "trends": trends[:5],
            "should_suggest": ai_resp.get("should_suggest", False),
            "analytics": {
                "message_length": len(message),
                "has_suggestions": len(ai_resp.get("suggestions", [])) > 0,
                "trends_available": len(trends) > 0,
                "platforms_suggested": list(set(
                    suggestion.get("platform", "unknown") 
                    for suggestion in ai_resp.get("suggestions", [])
                ))
            }
        }
        
    except Exception as e:
        logger.error(f"Chat handling error: {e}")
        return _get_error_response(session_id)

async def _get_or_create_session(db, session_id: Optional[str] = None):
    """Get existing session or create new one with enhanced schema"""
    if session_id and ObjectId.is_valid(session_id):
        session_obj_id = ObjectId(session_id)
        session = await db.chats.find_one({"_id": session_obj_id})
        if session:
            return session, session_id
    
    # Create new session with enhanced schema
    session_doc = {
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "messages": [],
        "interaction_count": 0,
        "platform_requests": {},
        "suggestion_stats": {
            "total_suggestions": 0,
            "platforms_used": [],
            "last_suggestion_date": None
        },
        "user_preferences": {
            "preferred_platforms": [],
            "content_types": []
        }
    }
    res = await db.chats.insert_one(session_doc)
    session_id = str(res.inserted_id)
    session = await db.chats.find_one({"_id": res.inserted_id})
    
    return session, session_id

async def _save_user_message(db, session_id: ObjectId, message: str):
    """Save user message with enhanced metadata"""
    user_msg = {
        "role": "user", 
        "text": message, 
        "created_at": datetime.utcnow(),
        "message_id": f"user_{datetime.utcnow().timestamp()}",
        "metadata": {
            "length": len(message),
            "contains_platform_request": any(keyword in message.lower() for keyword in 
                                           ['linkedin', 'twitter', 'instagram', 'facebook', 'post']),
            "timestamp": datetime.utcnow()
        }
    }
    
    await db.chats.update_one(
        {"_id": session_id}, 
        {
            "$push": {"messages": user_msg}, 
            "$set": {"updated_at": datetime.utcnow()},
            "$inc": {"interaction_count": 1}
        }
    )

async def _save_assistant_message(db, session_id: ObjectId, ai_response: Dict[str, Any]):
    """Save assistant message with full response data"""
    assistant_msg = {
        "role": "assistant", 
        "text": ai_response.get("reply", ""), 
        "created_at": datetime.utcnow(),
        "message_id": f"assistant_{datetime.utcnow().timestamp()}",
        "response_data": {
            "suggestions": ai_response.get("suggestions", []),
            "should_suggest": ai_response.get("should_suggest", False),
            "trends_used": len(ai_response.get("suggestions", [])) > 0
        }
    }
    
    update_operation = {
        "$push": {"messages": assistant_msg}, 
        "$set": {"updated_at": datetime.utcnow()}
    }
    
    # Update suggestion statistics if suggestions were provided
    if ai_response.get("suggestions"):
        platforms = list(set(
            suggestion.get("platform", "unknown") 
            for suggestion in ai_response.get("suggestions", [])
        ))
        
        update_operation["$inc"] = {
            "suggestion_stats.total_suggestions": len(ai_response.get("suggestions", [])),
            **{f"platform_requests.{platform}": 1 for platform in platforms}
        }
        
        update_operation["$addToSet"] = {
            "suggestion_stats.platforms_used": {"$each": platforms}
        }
        
        update_operation["$set"] = {
            **update_operation.get("$set", {}),
            "suggestion_stats.last_suggestion_date": datetime.utcnow()
        }
    
    await db.chats.update_one({"_id": session_id}, update_operation)

async def _log_detailed_interaction(db, session_id: str, user_message: str, ai_response: Dict[str, Any], trends: List[Dict[str, Any]]):
    """Log detailed interaction for analytics and improvement"""
    analytics_doc = {
        "session_id": session_id,
        "timestamp": datetime.utcnow(),
        "user_message": {
            "content": user_message[:500],  # Store first 500 chars
            "length": len(user_message),
            "platform_requests": _extract_platform_requests(user_message)
        },
        "ai_response": {
            "suggestion_count": len(ai_response.get("suggestions", [])),
            "platforms_suggested": list(set(
                suggestion.get("platform", "unknown") 
                for suggestion in ai_response.get("suggestions", [])
            )),
            "content_types": list(set(
                suggestion.get("type", "unknown") 
                for suggestion in ai_response.get("suggestions", [])
            ))
        },
        "trends_used": {
            "count": len(trends),
            "platforms": list(set(trend.get("platform", "general") for trend in trends))
        },
        "engagement_metrics": {
            "has_visual_recommendations": any(
                suggestion.get("visual_recommendation") 
                for suggestion in ai_response.get("suggestions", [])
            ),
            "has_performance_predictions": any(
                suggestion.get("performance_prediction") 
                for suggestion in ai_response.get("suggestions", [])
            )
        }
    }
    
    try:
        await db.interaction_analytics.insert_one(analytics_doc)
    except Exception as e:
        logger.warning(f"Failed to log interaction: {e}")

def _extract_platform_requests(message: str) -> List[str]:
    """Extract platform requests from user message"""
    platforms = []
    message_lower = message.lower()
    
    if any(keyword in message_lower for keyword in ['linkedin', 'professional']):
        platforms.append('linkedin')
    if any(keyword in message_lower for keyword in ['twitter', 'tweet', 'x post', 'x.com']):
        platforms.append('twitter')
    if any(keyword in message_lower for keyword in ['instagram', 'ig', 'insta']):
        platforms.append('instagram')
    if any(keyword in message_lower for keyword in ['facebook', 'fb']):
        platforms.append('facebook')
    
    return platforms

def _get_error_response(session_id: Optional[str] = None) -> Dict[str, Any]:
    """Get comprehensive error response"""
    return {
        "session_id": session_id or "error",
        "reply": "I apologize, but I'm experiencing technical difficulties right now. Please try again in a moment, or rephrase your request.",
        "suggestions": [],
        "trends": [],
        "should_suggest": False,
        "error": True
    }

# Additional function to get chat history with analytics
async def get_chat_analytics(db, session_id: str) -> Dict[str, Any]:
    """Get analytics for a chat session"""
    if not ObjectId.is_valid(session_id):
        return {"error": "Invalid session ID"}
    
    session = await db.chats.find_one({"_id": ObjectId(session_id)})
    if not session:
        return {"error": "Session not found"}
    
    # Get interaction analytics for this session
    try:
        analytics_list = await db.interaction_analytics.find({"session_id": session_id}).sort("timestamp", -1).limit(50).to_list(length=50)
    except Exception:
        analytics_list = []
    
    return {
        "session_info": {
            "session_id": session_id,
            "created_at": session.get("created_at"),
            "interaction_count": session.get("interaction_count", 0),
            "total_suggestions": session.get("suggestion_stats", {}).get("total_suggestions", 0)
        },
        "platform_usage": session.get("platform_requests", {}),
        "recent_interactions": analytics_list
    }