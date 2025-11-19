import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from models.topic import Topic, Tag


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

async def test_create_topic_validation_error(client: AsyncClient, mock_current_user):
    """Tests the creation of a topic with validation errors."""
    response = await client.post("/api/v1/topics/", json={
        "title": "",
        "text": "Topic text"
    })
    assert response.status_code == 422
    
async def test_unauthenticated_create_topic(client:AsyncClient):
    """Tests the creation of a topic without authentication."""
    response = await client.post("/api/v1/topics/", json={
        "title": "My Topic",
        "text": "Topic text"
    })
    assert response.status_code == 401
    
    
    
    
    
    
