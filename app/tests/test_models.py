import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError  
from models.topic import Topic,Tag, Category

pytestmark = pytest.mark.asyncio

async def test_topic_creation(db_session: AsyncSession):
    """
    Test For Topic Model Creation. Checks if a Topic can be created and saved correctly.
    """
    
    topic = Topic(
        title="test model",
        text="This is a test model text.",
        author_id=123
    )
   
    db_session.add(topic)
    await db_session.commit()
    await db_session.refresh(topic)
    
 
    assert topic.id is not None
    assert topic.title == "test model"
    assert topic.author_id == 123
    assert topic.created_at is not None  


async def test_topic_validation_nullable(db_session: AsyncSession):
    """
    Validation Test: Non-nullable Fields.
    """
    
   
    topic_no_title = Topic(
        title=None,  
        text="Text without title",
        author_id=123
    )
    
    db_session.add(topic_no_title)
    
   
    with pytest.raises(IntegrityError):
        await db_session.commit()


async def test_topic_relationships(db_session: AsyncSession):
    """
    Test For Topic Model Relationships. Checks if the relationships with Category and Tags work correctly.
    """
    category = Category(name="Test Category")
    tag1 = Tag(name="Tag 1")
    tag2 = Tag(name="Tag 2")

    db_session.add_all([category, tag1, tag2])
    await db_session.commit() 
    
    topic = Topic(
        title="Topic with Relationships",
        text="...",
        author_id=456,
        category=category,  
        tags=[tag1, tag2]    
    )
    
    db_session.add(topic)
    await db_session.commit()
    await db_session.refresh(topic)
    
 
    assert topic.category_id == category.id
    assert topic.category.name == "Test Category"

    await db_session.refresh(topic, ["tags"])
    assert len(topic.tags) == 2
    tag_names = {tag.name for tag in topic.tags}
    
    assert "Tag 1" in tag_names
    assert "Tag 2" in tag_names