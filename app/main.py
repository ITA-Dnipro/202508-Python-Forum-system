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
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
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


@app.get("/health", tags=["Health Check"])
async def db_check(db: AsyncSession = Depends(get_db)):
    """
    Перевіряє, чи сервіс живий і чи має з'єднання з базою даних.
    """
    try:
        # Виконуємо найпростіший SQL-запит, щоб перевірити з'єднання
        await db.execute(text("SELECT 1"))
        
        # Якщо запит пройшов успішно, повертаємо "ok"
        return {"status": "ok", "message": "Database connection is successful!"}
    
    except Exception as e:
        # Якщо щось пішло не так, повертаємо помилку 500
        # Це допоможе нам побачити, в чому саме проблема
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )