from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from core.security import get_current_user_id
from schemas.topic import TopicCreate, TopicUpdate, TopicResponse, TopicListResponse
from crud import topic as topic_crud


router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_in: TopicCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Create a new topic.
    """
    topic = await topic_crud.create_topic(
        db=db,
        topic_in=topic_in,
        author_id=current_user_id
    )
    
    created_topic = await topic_crud.get_topic_by_id(db=db, topic_id=topic.id)
    
    return created_topic


@router.get("/", response_model=TopicListResponse)
async def list_topics(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a paginated list of topics.
    """
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")
    
    skip = (page - 1) * page_size
    
    topics = await topic_crud.get_topics(db=db, skip=skip, limit=page_size)
    total = await topic_crud.get_topics_count(db=db)
    
    return TopicListResponse(
        topics=topics,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a topic by ID.
    """
    topic = await topic_crud.get_topic_by_id(db=db, topic_id=topic_id)
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with id {topic_id} not found"
        )
    
    return topic


@router.patch("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: int,
    topic_in: TopicUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Update a topic (only author).
    Allows partial updates (e.g., only 'title').
    """
    
    topic = await topic_crud.get_topic_by_id(db=db, topic_id=topic_id)
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with id {topic_id} not found"
        )
        
    if topic.author_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this topic"
        )
        
 
    updated_topic = await topic_crud.update_topic(
        db=db, 
        topic=topic, 
        topic_update=topic_in
    )
    
    return updated_topic


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Видалити тему (тільки автор).
    """
    
    topic = await topic_crud.get_topic_by_id(db=db, topic_id=topic_id)
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with id {topic_id} not found"
        )
        
    if topic.author_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this topic"
        )
        
    await topic_crud.delete_topic(db=db, topic=topic)
    
    return None