from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Query
from typing import List, Optional
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
    The authenticated user becomes the author.
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
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by title or text"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    tags: Optional[List[int]] = Query(None, description="Filter by tag IDs (e.g. ?tags=1&tags=2)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a paginated list of topics with optional filtering.
    """
    
    skip = (page - 1) * page_size
    
    topics = await topic_crud.get_topics(
        db=db, 
        skip=skip, 
        limit=page_size,
        search=search,
        category_id=category_id,
        author_id=author_id,
        tag_ids=tags
    )
    
    total = await topic_crud.get_topics_count(
        db=db,
        search=search,
        category_id=category_id,
        author_id=author_id,
        tag_ids=tags
    )
    
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
    Delete a topic (only author).
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