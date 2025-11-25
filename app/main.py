# app/main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db import connect_to_mongo, close_mongo_connection
from .routers import content_router, chat_router

logger = logging.getLogger("uvicorn.error")

def create_app():
    app = FastAPI(title="Content Bot API")

    @app.on_event("startup")
    async def startup_event():
        await connect_to_mongo(app)
        logger.info("Connected to MongoDB")

    @app.on_event("shutdown")
    async def shutdown_event():
        await close_mongo_connection(app)
        logger.info("MongoDB connection closed")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers - use the router objects directly
    app.include_router(content_router)
    app.include_router(chat_router)

    # Add health check endpoint
    @app.get("/")
    async def root():
        return {"message": "Content Bot API is running"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app

app = create_app()