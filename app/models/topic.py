from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from db.session import Base


class Topic(Base):
    """
    Topic model for discussion threads.
    
    Fields:
    - id: Primary key
    - title: Topic title (required, max 255 chars)
    - text: Topic body/description (required)
    - author_id: User who created the topic
    - created_at: Timestamp of creation
    - updated_at: Timestamp of last update
    - view_count: Number of views (for future use)
    """
    __tablename__ = "topics"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Required fields
    title = Column(String(255), nullable=False, index=True)
    text = Column(Text, nullable=False)
    
    # Author (foreign key to User service in production)
    author_id = Column(Integer, nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<Topic(id={self.id}, title='{self.title[:50]}...')>"