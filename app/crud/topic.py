from typing import List, Optional
from sqlalchemy import or_, select, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from models.topic import Topic, Tag
from schemas.topic import TopicCreate, TopicUpdate


async def create_topic(
    db: AsyncSession,
    topic_in: TopicCreate,
    author_id: int
) -> Topic:
    """
    Create a new topic in the database.
    
    Args:
        db: Database session
        topic_in: Topic creation data
        author_id: ID of the user creating the topic
    
    Returns:
        Created Topic model instance
    """
    
    db_topic = Topic(
        title=topic_in.title,
        text=topic_in.text,
        author_id=author_id
    )
    
    db.add(db_topic)
    await db.commit()
    await db.refresh(db_topic)
    
    return db_topic


def _get_topics_query(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    author_id: Optional[int] = None,
    tag_ids: Optional[List[int]] = None
):
    """Constructs a base SQLAlchemy query with filters applied."""
    query = select(Topic)

    
    if category_id:
        query = query.where(Topic.category_id == category_id)

    
    if author_id:
        query = query.where(Topic.author_id == author_id)

    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Topic.title.ilike(search_term),
                Topic.text.ilike(search_term)
            )
        )

    if tag_ids:
        query = query.where(Topic.tags.any(Tag.id.in_(tag_ids)))

    return query


async def get_topics(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    author_id: Optional[int] = None,
    tag_ids: Optional[List[int]] = None
) -> List[Topic]:
    """Get a filtered and paginated list of topics."""
    
    query = _get_topics_query(search, category_id, author_id, tag_ids)
    
    query = query.order_by(Topic.created_at.desc()) \
        .options(
            selectinload(Topic.tags),
            joinedload(Topic.category)
        ) \
        .offset(skip) \
        .limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def get_topics_count(
    db: AsyncSession,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    author_id: Optional[int] = None,
    tag_ids: Optional[List[int]] = None
) -> int:
    """
    Get the total number of topics matching the filters.
    """
    base_query = _get_topics_query(search, category_id, author_id, tag_ids)
    count_query = select(func.count()).select_from(base_query.subquery())
    
    result = await db.execute(count_query)
    return result.scalar_one()


async def get_topic_by_id(db: AsyncSession, topic_id: int) -> Optional[Topic]:
    """Get a topic by ID with its tags and category."""
    result = await db.execute(
        select(Topic)
        .where(Topic.id == topic_id)
        .options(
            selectinload(Topic.tags),
            joinedload(Topic.category) 
        )
    )
    return result.scalar_one_or_none()



async def update_topic(
    db: AsyncSession,
    topic: Topic,
    topic_update: TopicUpdate
) -> Topic:
    """Update a topic."""
    update_data = topic_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(topic, field, value)
    
    await db.commit()
    await db.refresh(topic)
    return topic


async def delete_topic(db: AsyncSession, topic: Topic) -> None:
    """Delete a topic."""
    await db.delete(topic)
    await db.commit()