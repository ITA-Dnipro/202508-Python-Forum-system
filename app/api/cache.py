from schemas.topic import TopicListResponse
from db.redis_session import redis_client

CACHE_TTL = 300 

async def get_topics_from_cache(
    page: int, 
    page_size: int, 
    search: str | None
) -> TopicListResponse | None:
    """
    Пробує знайти список тем у Redis.
    Повертає об'єкт Pydantic або None.
    """
    key = f"topics:list:{page}:{page_size}:{search}"
    
    data = await redis_client.get(key)
    
    if data:
        return TopicListResponse.model_validate_json(data)
    
    return None

async def set_topics_cache(
    page: int, 
    page_size: int, 
    search: str | None, 
    data: TopicListResponse
):
    """Зберігає список тем у Redis."""
    key = f"topics:list:{page}:{page_size}:{search}"
    
    await redis_client.set(key, data.model_dump_json(), ex=CACHE_TTL)

async def clear_topics_cache():
    """
    Видаляє весь кеш тем. Викликається при створенні нової теми.
    """
    keys = await redis_client.keys("topics:list:*")
    if keys:
        await redis_client.delete(*keys)