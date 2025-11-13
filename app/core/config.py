from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Community Forum API"
    DEBUG: bool = True


    POSTGRESQL_USER: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_DB: str
    POSTGRESQL_PORT: str = "5432"
    POSTGRESQL_SERVER: str
    
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    @property
    def DATABASE_URL(self) -> str:
        """Async SQLAlchemy database URL"""
        return (
           f"postgresql+asyncpg://{self.POSTGRESQL_USER}:{self.POSTGRESQL_PASSWORD}@{self.POSTGRESQL_SERVER}:{self.POSTGRESQL_PORT}/{self.POSTGRESQL_DB}"
        )

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
