from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class TopicBase(BaseModel):
    """Base schema with shared fields."""
    title: str = Field(..., min_length=1, max_length=255, description="Topic title")
    text: str = Field(..., min_length=1, description="Topic body text")

    model_config = {
        "from_attributes": True
    }


class TopicCreate(TopicBase):
    """
    Schema for creating a new topic.
    Includes validation for required fields.
    """
    
    @field_validator("title")
    @classmethod 
    def validate_title(cls, v: str) -> str:
        """Ensure title is not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()

    @field_validator("text")
    @classmethod 
    def validate_text(cls, v: str) -> str:
        """Ensure text is not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


class TopicUpdate(BaseModel):
    """Schema for updating a topic."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    text: Optional[str] = Field(None, min_length=1)

class TagResponse(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }
    
class TopicResponse(TopicBase):
    """
    Schema for topic responses.
    Includes all fields from the database model.
    """
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    category_id: Optional[int] = None
    tags: list[TagResponse] = []
    
    model_config = {
        "from_attributes": True
    }
    

class TopicListResponse(BaseModel):
    """Schema for paginated topic list."""
    topics: list[TopicResponse]
    total: int
    page: int
    page_size: int
    
    model_config = {
        "from_attributes": True
    }