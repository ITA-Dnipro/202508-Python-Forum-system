from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from core.security import get_current_user_id
from schemas.topic import TopicCreate, TopicResponse, TopicListResponse
from crud import topic as topic_crud

# Create router
router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_in: TopicCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Create a new topic.
    
    **Required fields:**
    - title: Topic title (1-255 characters)
    - text: Topic body text (at least 1 character)
    
    **Authentication:**
    - Requires Bearer token in format: "user_<id>"
    - Example: Authorization: Bearer user_123
    
    **Returns:**
    - Created topic with ID and timestamps
    """
    # Create topic via CRUD
    topic = await topic_crud.create_topic(
        db=db,
        topic_in=topic_in,
        author_id=current_user_id
    )
    
    return topic


@router.get("/", response_model=TopicListResponse)
async def list_topics(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a paginated list of topics.
    
    **Query parameters:**
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    """
    # Validate pagination
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")
    
    # Calculate offset
    skip = (page - 1) * page_size
    
    # Get topics and total count
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
    Get a specific topic by ID.
    """
    topic = await topic_crud.get_topic_by_id(db=db, topic_id=topic_id)
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with id {topic_id} not found"
        )
    
    return topic