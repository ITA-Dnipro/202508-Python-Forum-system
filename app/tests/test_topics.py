import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from main import app
from db.session import Base, get_db
from models.topic import Topic, Tag

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """Creates the database schema before each test and drops it after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides a clean database session for each test."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Creates a test HTTP client with the fake database."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_current_user():
    """Mocks the current authenticated user to have user ID 1."""
    from core.security import get_current_user_id
    
    async def override_get_current_user():
        return 1
    
    app.dependency_overrides[get_current_user_id] = override_get_current_user
    
    yield
    
    app.dependency_overrides.clear()

pytestmark = pytest.mark.asyncio

async def test_create_topic(client: AsyncClient, mock_current_user):
    """Tests the creation of a topic."""
    
    response = await client.post("/api/v1/topics/", json={
        "title": "My Topic",
        "text": "Topic text"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Topic"
    assert data["author_id"] == 1


async def test_list_topics(client: AsyncClient, mock_current_user):
    """Tests retrieving a list of topics."""

    
    await client.post("/api/v1/topics/", json={
        "title": "Topic 1",
        "text": "Topic text 1"
    })
    response = await client.get("/api/v1/topics/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["topics"]) == 1
    assert data["total"] == 1


async def test_get_topic(client: AsyncClient, mock_current_user):
    """Tests retrieving a single topic by ID."""

    create_response = await client.post("/api/v1/topics/", json={
        "title": "Test Topic",
        "text": "Test text"
    })
    topic_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/topics/{topic_id}")
    
    assert response.status_code == 200
    assert response.json()["title"] == "Test Topic"

async def test_get_topic_not_found(client: AsyncClient):
    """Tests 404 for a non-existing topic."""

    response = await client.get("/api/v1/topics/99999")
    
    assert response.status_code == 404


async def test_update_topic(client: AsyncClient, mock_current_user):
    """Tests updating a topic by the author."""

    create_response = await client.post("/api/v1/topics/", json={
        "title": "Old Title",
        "text": "Old text"
    })
    topic_id = create_response.json()["id"]

    response = await client.patch(f"/api/v1/topics/{topic_id}", json={
        "title": "New Title"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["text"] == "Old text" 


async def test_delete_topic(client: AsyncClient, mock_current_user):
    """Tests deleting a topic by the author."""

    create_response = await client.post("/api/v1/topics/", json={
        "title": "Topic to Delete",
        "text": "Text"
    })
    topic_id = create_response.json()["id"]
    
    response = await client.delete(f"/api/v1/topics/{topic_id}")
    
    assert response.status_code == 204

    get_response = await client.get(f"/api/v1/topics/{topic_id}")
    assert get_response.status_code == 404
