import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from crud import topic as topic_crud
from models.topic import Topic
from schemas.topic import TopicCreate, TopicUpdate

pytestmark = pytest.mark.asyncio

async def test_create_topic(db_session: AsyncSession):
    """
    create a new topic. Checks if the topic is created and saved correctly.
    """

    topic_in = TopicCreate(title="Test CRUD", text="Text for CRUD")
    author_id = 99 
    
    created_topic = await topic_crud.create_topic(
        db=db_session, topic_in=topic_in, author_id=author_id
    )

    assert created_topic is not None
    assert created_topic.id is not None
    assert created_topic.title == "Test CRUD"
    assert created_topic.author_id == 99

    saved_topic = await db_session.get(Topic, created_topic.id)
    assert saved_topic is not None
    assert saved_topic.title == "Test CRUD"


async def test_get_topic_by_id(db_session: AsyncSession):
    """
    Test: Get a topic by ID.
    """
    topic_in = TopicCreate(title="Topic for Search", text="...")
    created_topic = await topic_crud.create_topic(db=db_session, topic_in=topic_in, author_id=1)
    
    found_topic = await topic_crud.get_topic_by_id(db=db_session, topic_id=created_topic.id)
    
    assert found_topic is not None
    assert found_topic.id == created_topic.id
    assert found_topic.title == "Topic for Search"


async def test_get_topics_and_count(db_session: AsyncSession):
    """
    Test: Get a list of topics and their count.
    """
    await topic_crud.create_topic(db=db_session, topic_in=TopicCreate(title="Topic 1", text="..."), author_id=1)
    await topic_crud.create_topic(db=db_session, topic_in=TopicCreate(title="Topic 2", text="..."), author_id=2)
    topics_list = await topic_crud.get_topics(db=db_session, skip=0, limit=10)
    
    topic_titles = [topic.title for topic in topics_list]
    assert len(topics_list) == 2
    topic1 = topics_list[0].title
    topic2 = topics_list[1].title

    assert topic1 in topic_titles
    assert topic2 in topic_titles
    count = await topic_crud.get_topics_count(db=db_session)
    
    assert count == 2


async def test_update_topic(db_session: AsyncSession):
    """
    Test: Update a topic.
    """
    created_topic = await topic_crud.create_topic(db=db_session, topic_in=TopicCreate(title="Old Title", text="Old Text"), author_id=1)
    update_data = TopicUpdate(title="New Title")
    
    updated_topic = await topic_crud.update_topic(
        db=db_session, topic=created_topic, topic_update=update_data
    )

    assert updated_topic.title == "New Title"
    assert updated_topic.text == "Old Text"

    saved_topic = await db_session.get(Topic, created_topic.id)
    assert saved_topic.title == "New Title"


async def test_delete_topic(db_session: AsyncSession):
    """
    Test: Delete a topic.
    """
    created_topic = await topic_crud.create_topic(db=db_session, topic_in=TopicCreate(title="To Delete", text="..."), author_id=1)
    topic_id = created_topic.id
    
    await topic_crud.delete_topic(db=db_session, topic=created_topic)
    
    deleted_topic = await db_session.get(Topic, topic_id)
    assert deleted_topic is None