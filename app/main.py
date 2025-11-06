from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.config import settings
from api.topics import router as topics_router
from db.session import get_db


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A simplified forum/community microservice for educational purposes",
    version="1.0.0",
    docs_url="/docs",  
    redoc_url="/redoc"  
)

app.include_router(topics_router, prefix="/api/v1", tags=["topics"])

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Community Forum API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }
