from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class TopicBase(BaseModel):
    """Base schema with shared fields."""
    title: str = Field(..., min_length=1, max_length=255, description="Topic title")
    text: str = Field(..., min_length=1, description="Topic body text")


class TopicCreate(TopicBase):
    """
    Schema for creating a new topic.
    Includes validation for required fields.
    """
    
    @validator("title")
    def validate_title(cls, v):
        """Ensure title is not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()
    
    @validator("text")
    def validate_text(cls, v):
        """Ensure text is not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


class TopicUpdate(BaseModel):
    """Schema for updating a topic."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    text: Optional[str] = Field(None, min_length=1)


class TopicResponse(TopicBase):
    """
    Schema for topic responses.
    Includes all fields from the database model.
    """
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    view_count: int
    
    class Config:
        ''' ORM mode to work with SQLAlchemy models'''
        from_attributes = True


class TopicListResponse(BaseModel):
    """Schema for paginated topic list."""
    topics: list[TopicResponse]
    total: int
    page: int
    page_size: int