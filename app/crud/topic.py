from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from models.topic import Topic
from schemas.topic import TopicCreate, TopicUpdate
from crud.tags import get_or_create_tags_by_name


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
    tags_objects = await get_or_create_tags_by_name(
        db=db, 
        tag_names=topic_in.tags
    )
    
    db_topic = Topic(
        title=topic_in.title,
        text=topic_in.text,
        author_id=author_id,
        category_id=topic_in.category_id, 
        tags=tags_objects
    )
    
    db.add(db_topic)
    await db.commit()
    await db.refresh(db_topic)
    
    return db_topic


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


async def get_topics(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20
) -> list[Topic]:
    """Get a paginated list of topics with their tags and categories."""
    result = await db.execute(
        select(Topic)
        .order_by(Topic.created_at.desc())
        .options(
            
            selectinload(Topic.tags),
            joinedload(Topic.category)
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_topics_count(db: AsyncSession) -> int:
    """
    Get the total number of topics. For pagination purposes.
    """
    
    result = await db.execute(
        select(func.count(Topic.id))
    )
    
    return result.scalar_one()


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