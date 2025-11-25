# services/ai_client.py
import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import logging
import re
import json

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found, using mock responses")
            self.client = None
            self.model = None
            return
        
        try:
            genai.configure(api_key=api_key)
            # Try to get the correct model name/initialization
            try:
                self.model = genai.GenerativeModel('gemini-pro')
                self.client = genai
            except (AttributeError, TypeError):
                # Fallback if GenerativeModel not available
                logger.warning("GenerativeModel not available, using mock responses")
                self.client = None
                self.model = None
        except Exception as e:
            logger.warning(f"Gemini initialization failed: {e}, using mock responses")
            self.client = None
            self.model = None

    async def generate_reply(self, message: str, context: List[Dict[str, Any]] = None, trends: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate AI response with platform-specific post generation"""
        
        # Check if user is requesting specific platform post
        platform_request = self._detect_platform_request(message)
        
        if platform_request:
            return await self._generate_platform_specific_post(message, platform_request, context, trends)
        
        if not self.client:
            return self._mock_response(message, trends)
        
        try:
            prompt = self._build_conversation_prompt(message, context, trends, is_general=True)
            response = self.model.generate_content(prompt)
            
            return self._parse_ai_response(response.text, message)
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._mock_response(message, trends)
    
    def _detect_platform_request(self, message: str) -> Optional[str]:
        """Detect if user is requesting a specific platform post"""
        message_lower = message.lower()
        
        platform_keywords = {
            'linkedin': ['linkedin', 'linkedin post', 'professional post'],
            'twitter': ['twitter', 'tweet', 'x post', 'x.com'],
            'instagram': ['instagram', 'ig post', 'insta post'],
            'facebook': ['facebook', 'fb post']
        }
        
        for platform, keywords in platform_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return platform
        
        return None
    
    async def _generate_platform_specific_post(self, message: str, platform: str, context: List[Dict[str, Any]] = None, trends: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate content for specific platform request"""
        
        if not self.client:
            return self._mock_platform_response(message, platform)
        
        try:
            prompt = self._build_platform_specific_prompt(message, platform, context, trends)
            response = self.model.generate_content(prompt)
            
            return self._parse_platform_response(response.text, platform, message)
            
        except Exception as e:
            logger.error(f"Platform-specific generation error: {e}")
            return self._mock_platform_response(message, platform)
    
    def _build_conversation_prompt(self, message: str, context: List[Dict[str, Any]] = None, trends: List[Dict[str, Any]] = None, is_general: bool = True) -> str:
        """Build prompt for general conversation"""
        
        context_text = self._build_context_text(context)
        trends_text = self._build_trends_text(trends)
        
        if is_general:
            return f"""
            You are a social media content strategist. The user is sharing about their day. Your role:
            1. Provide empathetic, engaging responses about their day
            2. Listen carefully to their content and mood
            3. Only suggest social media posts if it feels natural
            4. If they explicitly ask for posts (like "give me a LinkedIn post"), generate specific content
            
            Current trends and insights:
            {trends_text}
            
            Conversation history:
            {context_text}
            
            User's message: {message}
            
            Respond in this JSON format:
            {{
                "reply": "your engaging response here",
                "suggestions": [
                    {{
                        "platform": "platform_name",
                        "type": "text|image|video|carousel",
                        "content": "post content",
                        "hashtags": ["#tag1", "#tag2"],
                        "why_effective": "why this would work well",
                        "visual_recommendation": "whether image/video is needed and why",
                        "best_time": "when to post",
                        "engagement_tips": ["tip1", "tip2"]
                    }}
                ],
                "should_suggest": true/false
            }}
            """
        else:
            return self._build_platform_specific_prompt(message, "general", context, trends)
    
    def _build_platform_specific_prompt(self, message: str, platform: str, context: List[Dict[str, Any]] = None, trends: List[Dict[str, Any]] = None) -> str:
        """Build prompt for platform-specific post generation"""
        
        context_text = self._build_context_text(context)
        trends_text = self._build_trends_text(trends)
        
        platform_guides = {
            "linkedin": {
                "tone": "professional, insightful, value-driven",
                "content_types": "industry insights, career achievements, professional learnings",
                "best_practices": "Use professional language, include data/insights, ask thoughtful questions"
            },
            "twitter": {
                "tone": "concise, engaging, conversational",
                "content_types": "quick thoughts, news reactions, engaging questions, thread stories",
                "best_practices": "Keep it under 280 characters, use 1-2 relevant hashtags, engage with replies"
            },
            "instagram": {
                "tone": "visual, personal, authentic, engaging",
                "content_types": "personal stories, behind-the-scenes, visual content, reels",
                "best_practices": "High-quality visuals essential, use 5-10 relevant hashtags, engaging captions"
            }
        }
        
        guide = platform_guides.get(platform, platform_guides["linkedin"])
        
        return f"""
        Generate a {platform} post based on the user's request and conversation history.
        
        Platform: {platform}
        Tone: {guide['tone']}
        Content Types: {guide['content_types']}
        Best Practices: {guide['best_practices']}
        
        Current Trends:
        {trends_text}
        
        Conversation Context:
        {context_text}
        
        User's Request: {message}
        
        Provide a comprehensive post recommendation in this exact JSON format:
        {{
            "reply": "I've created a {platform} post for you based on your content. Here's why this approach works well:",
            "suggestions": [
                {{
                    "platform": "{platform}",
                    "type": "recommended_content_type",
                    "content": "the actual post content ready to copy-paste",
                    "hashtags": ["#relevant", "#hashtags"],
                    "why_effective": "detailed explanation of why this post will perform well",
                    "visual_recommendation": "specific advice on images/videos needed and why",
                    "best_time": "optimal posting time with reasoning",
                    "engagement_tips": ["specific tip 1", "specific tip 2", "specific tip 3"],
                    "performance_prediction": "what kind of engagement to expect"
                }}
            ],
            "should_suggest": true
        }}
        """
    
    def _build_context_text(self, context: List[Dict[str, Any]] = None) -> str:
        """Build context from conversation history"""
        if not context:
            return "No previous conversation."
        
        context_text = ""
        for msg in context[-8:]:  # Last 8 messages
            role = "User" if msg.get("role") == "user" else "Assistant"
            context_text += f"{role}: {msg.get('text', '')}\n"
        
        return context_text
    
    def _build_trends_text(self, trends: List[Dict[str, Any]] = None) -> str:
        """Build trends context text"""
        if not trends:
            return "No current trend data available."
        
        trends_text = "Current Social Media Insights:\n"
        for trend in trends[:5]:
            platform = trend.get("platform", "General")
            formats = trend.get("formats", [])
            engagement = trend.get("engagement", "medium")
            
            trends_text += f"- {platform}: {', '.join(formats)} (engagement: {engagement})\n"
        
        return trends_text
    
    def _parse_ai_response(self, response_text: str, original_message: str) -> Dict[str, Any]:
        """Parse AI response with error handling"""
        try:
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback to text response
                return {
                    "reply": response_text[:500],
                    "suggestions": self._generate_fallback_suggestions(original_message),
                    "should_suggest": True
                }
        except json.JSONDecodeError:
            logger.warning("Failed to parse AI response as JSON")
            return {
                "reply": response_text[:500],
                "suggestions": self._generate_fallback_suggestions(original_message),
                "should_suggest": True
            }
    
    def _parse_platform_response(self, response_text: str, platform: str, original_message: str) -> Dict[str, Any]:
        """Parse platform-specific response"""
        parsed = self._parse_ai_response(response_text, original_message)
        
        # Ensure platform consistency
        if parsed.get("suggestions"):
            for suggestion in parsed["suggestions"]:
                suggestion["platform"] = platform
        
        return parsed
    
    def _mock_response(self, message: str, trends: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enhanced mock response"""
        reply = f"I understand you're sharing about your day! '{message[:100]}...' "
        reply += "That sounds interesting! When you're ready for social media posts, just ask me for specific platforms like 'Give me a LinkedIn post' or 'Create an Instagram post'."
        
        return {
            "reply": reply,
            "suggestions": [],
            "should_suggest": False
        }
    
    def _mock_platform_response(self, message: str, platform: str) -> Dict[str, Any]:
        """Mock platform-specific response"""
        platform_names = {
            "linkedin": "LinkedIn",
            "twitter": "Twitter/X",
            "instagram": "Instagram"
        }
        
        platform_name = platform_names.get(platform, platform)
        
        return {
            "reply": f"I've created a {platform_name} post for you based on your content. Here's a tailored suggestion:",
            "suggestions": [
                {
                    "platform": platform,
                    "type": "image" if platform == "instagram" else "text",
                    "content": f"Based on your day: {message[:100]}... #PersonalUpdate #DailyReflection",
                    "hashtags": ["#PersonalUpdate", "#DailyReflection"],
                    "why_effective": f"This format works well on {platform_name} because it's authentic and relatable",
                    "visual_recommendation": "Add a personal photo or relevant image to increase engagement by 50%",
                    "best_time": "Weekdays 1-3 PM",
                    "engagement_tips": ["Ask a question to encourage comments", "Respond to all comments quickly"],
                    "performance_prediction": "Expected good engagement with 5-10+ comments"
                }
            ],
            "should_suggest": True
        }
    
    def _generate_fallback_suggestions(self, message: str) -> List[Dict[str, Any]]:
        """Generate intelligent fallback suggestions"""
        # Analyze message content for better suggestions
        message_lower = message.lower()
        
        suggestions = []
        
        # LinkedIn for professional content
        if any(word in message_lower for word in ['work', 'career', 'project', 'business']):
            suggestions.append({
                "platform": "linkedin",
                "type": "text",
                "content": f"Professional insight: {message[:120]}... #CareerGrowth",
                "hashtags": ["#CareerGrowth", "#ProfessionalUpdate"],
                "why_effective": "LinkedIn audiences value professional insights and career stories",
                "visual_recommendation": "Add a professional headshot or work-related image",
                "best_time": "Tuesday-Thursday, 9-11 AM",
                "engagement_tips": ["Share a key learning", "Tag relevant companies or people"],
                "performance_prediction": "Good for professional networking"
            })
        
        # Instagram for personal content
        if any(word in message_lower for word in ['fun', 'happy', 'friends', 'family', 'travel']):
            suggestions.append({
                "platform": "instagram",
                "type": "image",
                "content": f"📸 {message[:100]}... ✨",
                "hashtags": ["#LifeMoments", "#DailyJoy", "#Personal"],
                "why_effective": "Instagram thrives on personal, visual storytelling",
                "visual_recommendation": "ESSENTIAL: High-quality photo showing the moment",
                "best_time": "Evenings and weekends",
                "engagement_tips": ["Use 5-10 relevant hashtags", "Post Stories about this too"],
                "performance_prediction": "High engagement potential with good visuals"
            })
        
        # Twitter for quick updates
        suggestions.append({
            "platform": "twitter",
            "type": "text",
            "content": f"{message[:140]}",
            "hashtags": ["#Update"],
            "why_effective": "Quick, real-time updates perform well on Twitter",
            "visual_recommendation": "Optional: Add a relevant image or GIF",
            "best_time": "Throughout the day",
            "engagement_tips": ["Keep it concise", "Engage with replies quickly"],
            "performance_prediction": "Good for quick engagement"
        })
        
        return suggestions

# Singleton instance
ai_client = GeminiClient()

async def generate_reply(message: str, context: List[Dict[str, Any]] = None, trends: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    return await ai_client.generate_reply(message, context, trends)