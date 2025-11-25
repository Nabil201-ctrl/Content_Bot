# services/scraper.py
import asyncio
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
import json
import re

logger = logging.getLogger(__name__)

class InstagramScraper:
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(hours=2)
    
    async def scrape_instagram_trends(self) -> List[Dict[str, Any]]:
        """Scrape Instagram trending content formats and patterns"""
        cache_key = "instagram_trends"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            trends = await asyncio.gather(
                self._scrape_instagram_hashtags(),
                self._scrape_instagram_content_patterns(),
                self._analyze_instagram_formats(),
                return_exceptions=True
            )
            
            valid_trends = []
            for trend in trends:
                if not isinstance(trend, Exception) and trend:
                    valid_trends.extend(trend)
            
            # Add Instagram-specific insights
            instagram_insights = [
                {
                    "platform": "instagram",
                    "formats": ["reels", "carousel", "single_image", "stories"],
                    "engagement": "very_high",
                    "visual_requirements": "High-quality images/videos essential",
                    "hashtag_strategy": "5-10 relevant hashtags",
                    "best_practices": [
                        "Use vertical format for Reels",
                        "Engaging first frame for videos",
                        "Personal captions work best",
                        "Consistent posting schedule"
                    ]
                }
            ]
            valid_trends.extend(instagram_insights)
            
            self._set_cached(cache_key, valid_trends)
            return valid_trends
            
        except Exception as e:
            logger.error(f"Instagram scraping error: {e}")
            return self._get_instagram_fallback_trends()
    
    async def _scrape_instagram_hashtags(self) -> List[Dict[str, Any]]:
        """Scrape popular Instagram hashtags and trends"""
        trends = []
        try:
            # Using Instagram-like sources for trend data
            urls = [
                "https://www.displaypurposes.com/",  # Hashtag analytics
                "https://top-hashtags.com/instagram/",
            ]
            
            async with httpx.AsyncClient() as client:
                for url in urls:
                    try:
                        response = await client.get(url, timeout=10.0)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, "html.parser")
                            
                            # Extract hashtag patterns (simplified)
                            hashtags = []
                            hashtag_elements = soup.find_all(text=re.compile(r'#\w+'))
                            for element in hashtag_elements[:20]:
                                hashtags.extend(re.findall(r'#\w+', element))
                            
                            if hashtags:
                                trends.append({
                                    "type": "hashtag_trends",
                                    "source": url,
                                    "popular_hashtags": list(set(hashtags))[:10],
                                    "content_categories": self._categorize_hashtags(hashtags)
                                })
                                
                    except Exception as e:
                        logger.debug(f"Failed to scrape {url}: {e}")
                        continue
            
            return trends
            
        except Exception as e:
            logger.error(f"Hashtag scraping error: {e}")
            return []
    
    async def _scrape_instagram_content_patterns(self) -> List[Dict[str, Any]]:
        """Analyze Instagram content patterns"""
        try:
            # Mock data - in production, use Instagram API or web scraping
            content_patterns = [
                {
                    "type": "content_analysis",
                    "platform": "instagram",
                    "trending_formats": ["Reels (short videos)", "Carousel posts", "Before/After content"],
                    "high_performance_content": [
                        "Tutorials and how-tos",
                        "Personal stories with lessons",
                        "Behind-the-scenes content",
                        "User-generated content features"
                    ],
                    "engagement_metrics": {
                        "reels_engagement": "3-5x higher than photos",
                        "carousel_swipes": "Increased dwell time",
                        "story_completion": "70-80% for engaging content"
                    }
                }
            ]
            return content_patterns
            
        except Exception as e:
            logger.error(f"Content pattern analysis error: {e}")
            return []
    
    async def _analyze_instagram_formats(self) -> List[Dict[str, Any]]:
        """Analyze which Instagram formats perform best"""
        try:
            format_analysis = [
                {
                    "platform": "instagram",
                    "format": "reels",
                    "engagement_score": 95,
                    "best_for": ["Tutorials", "Trending audio", "Quick tips", "Entertainment"],
                    "visual_requirement": "Video required",
                    "optimal_length": "15-30 seconds",
                    "success_factors": ["Engaging first 3 seconds", "Trending audio", "Clear value proposition"]
                },
                {
                    "platform": "instagram",
                    "format": "carousel",
                    "engagement_score": 85,
                    "best_for": ["Step-by-step guides", "Multiple tips", "Storytelling", "Before/after"],
                    "visual_requirement": "Multiple images/videos",
                    "optimal_length": "5-10 slides",
                    "success_factors": ["Strong first slide", "Progressive value", "Clear call-to-action"]
                },
                {
                    "platform": "instagram",
                    "format": "single_image",
                    "engagement_score": 70,
                    "best_for": ["Beautiful photography", "Quick updates", "Inspirational quotes"],
                    "visual_requirement": "High-quality image essential",
                    "optimal_length": "N/A",
                    "success_factors": ["Exceptional image quality", "Compelling caption", "Strategic hashtags"]
                }
            ]
            return format_analysis
            
        except Exception as e:
            logger.error(f"Format analysis error: {e}")
            return []
    
    def _categorize_hashtags(self, hashtags: List[str]) -> Dict[str, List[str]]:
        """Categorize hashtags by content type"""
        categories = {
            "lifestyle": ["lifestyle", "life", "daily", "motivation", "inspiration"],
            "travel": ["travel", "wanderlust", "adventure", "explore"],
            "food": ["food", "foodie", "recipe", "cooking"],
            "fashion": ["fashion", "style", "outfit", "beauty"],
            "tech": ["tech", "technology", "innovation", "gadgets"],
            "business": ["business", "entrepreneur", "startup", "marketing"]
        }
        
        categorized = {}
        for category, keywords in categories.items():
            category_tags = [tag for tag in hashtags if any(keyword in tag.lower() for keyword in keywords)]
            if category_tags:
                categorized[category] = category_tags[:5]
        
        return categorized
    
    def _get_instagram_fallback_trends(self) -> List[Dict[str, Any]]:
        """Fallback Instagram trends"""
        return [
            {
                "platform": "instagram",
                "formats": ["reels", "carousel", "single_image"],
                "engagement": "high",
                "visual_requirements": "High-quality visuals mandatory",
                "current_trends": [
                    "Short-form video content (Reels)",
                    "Authentic behind-the-scenes",
                    "Educational carousels",
                    "Personal storytelling"
                ],
                "best_practices": [
                    "Use trending audio for Reels",
                    "Post during peak hours (7-9 PM)",
                    "Engage with comments within 1 hour",
                    "Use a mix of content formats"
                ]
            }
        ]
    
    def _get_cached(self, key: str) -> Any:
        """Get cached data if valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.cache_duration:
                return data
        return None
    
    def _set_cached(self, key: str, data: Any):
        """Set cached data with timestamp"""
        self.cache[key] = (data, datetime.now())

class TrendAnalyzer:
    def __init__(self):
        self.instagram_scraper = InstagramScraper()
        self.cache = {}
        self.cache_duration = timedelta(hours=1)
    
    async def fetch_trending_formats(self) -> List[Dict[str, Any]]:
        """Fetch comprehensive trending formats across all platforms"""
        cache_key = "all_trends"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            # Gather trends from all platforms
            trends = await asyncio.gather(
                self.instagram_scraper.scrape_instagram_trends(),
                self._analyze_linkedin_trends(),
                self._analyze_twitter_trends(),
                self._analyze_general_trends(),
                return_exceptions=True
            )
            
            # Combine all trends
            all_trends = []
            for trend_list in trends:
                if not isinstance(trend_list, Exception) and trend_list:
                    all_trends.extend(trend_list)
            
            self._set_cached(cache_key, all_trends)
            return all_trends
            
        except Exception as e:
            logger.error(f"Comprehensive trend analysis error: {e}")
            return self._get_fallback_trends()
    
    async def _analyze_linkedin_trends(self) -> List[Dict[str, Any]]:
        """Analyze LinkedIn trends"""
        return [
            {
                "platform": "linkedin",
                "formats": ["article", "text_post", "carousel", "video"],
                "engagement": "medium",
                "best_practices": ["Professional tone", "Data-driven insights", "Career-focused content"],
                "optimal_timing": "Tuesday-Thursday, 9-11 AM"
            }
        ]
    
    async def _analyze_twitter_trends(self) -> List[Dict[str, Any]]:
        """Analyze Twitter trends"""
        return [
            {
                "platform": "twitter",
                "formats": ["thread", "poll", "quick_tweet", "video"],
                "engagement": "high",
                "best_practices": ["Concise messaging", "Timely content", "Engagement hooks"],
                "optimal_timing": "Throughout the day, peak at 12-3 PM"
            }
        ]
    
    async def _analyze_general_trends(self) -> List[Dict[str, Any]]:
        """Analyze general social media trends"""
        return [
            {
                "platform": "general",
                "formats": ["video", "interactive", "storytelling"],
                "engagement": "high",
                "current_trends": ["Short-form video", "Authentic content", "Educational value"],
                "audience_preferences": ["Mobile-optimized", "Quick to consume", "Emotionally engaging"]
            }
        ]
    
    def _get_fallback_trends(self) -> List[Dict[str, Any]]:
        """Comprehensive fallback trends"""
        return [
            {
                "platform": "instagram",
                "formats": ["reels", "carousel", "single_image"],
                "engagement": "very_high",
                "visual_requirements": "High-quality images/videos essential",
                "recommendation": "Always use visuals on Instagram"
            },
            {
                "platform": "linkedin",
                "formats": ["text", "article", "carousel"],
                "engagement": "medium",
                "visual_requirements": "Recommended but not mandatory",
                "recommendation": "Add professional images when possible"
            },
            {
                "platform": "twitter",
                "formats": ["text", "thread", "poll"],
                "engagement": "high",
                "visual_requirements": "Optional but increases engagement",
                "recommendation": "Use images/GIFs for important tweets"
            }
        ]
    
    def _get_cached(self, key: str) -> Any:
        """Get cached data if valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.cache_duration:
                return data
        return None
    
    def _set_cached(self, key: str, data: Any):
        """Set cached data with timestamp"""
        self.cache[key] = (data, datetime.now())

# Global instances
trend_analyzer = TrendAnalyzer()
instagram_scraper = InstagramScraper()

async def fetch_trending_formats() -> List[Dict[str, Any]]:
    return await trend_analyzer.fetch_trending_formats()

async def fetch_instagram_trends() -> List[Dict[str, Any]]:
    return await instagram_scraper.scrape_instagram_trends()