# app/services/__init__.py
from .ai_client import generate_reply
from .scraper import fetch_trending_formats, fetch_instagram_trends

__all__ = ["generate_reply", "fetch_trending_formats", "fetch_instagram_trends"]