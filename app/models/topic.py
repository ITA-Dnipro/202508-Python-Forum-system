from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from db.session import Base
from sqlalchemy.orm import relationship 
from sqlalchemy import Table, ForeignKey



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
    - category_id: Optional category for the topic
    - category: Relationship to Category model
    - tags: Many-to-many relationship with Tag model
    """
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    text = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    category = relationship("Category", back_populates="topics")
    tags = relationship("Tag", secondary="topic_tags", back_populates="topics")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Topic(id={self.id}, title='{self.title[:50]}...')>"

class Tag(Base):
    """
    Tag model for topic tagging.
    
    Fields:
    - id: Primary key
    - name: Tag name (required, max 50 chars)
    """
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    topics = relationship("Topic", secondary="topic_tags", back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"
    
    

topic_tags = Table(
    "topic_tags",
    Base.metadata,
    Column("topic_id", Integer, ForeignKey("topics.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"))
)
class Category(Base):
    """
    Category model for topic categorization.
    
    Fields:
    - id: Primary key
    - name: Category name (required, max 100 chars)
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    topics = relationship("Topic", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"