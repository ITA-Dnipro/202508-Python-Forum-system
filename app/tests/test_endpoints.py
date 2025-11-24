import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from models.topic import Topic, Tag, Category


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
    
    

async def test_filter_by_search(client: AsyncClient, mock_current_user):
    """
    If the search filter works?
    """
   
    await client.post("/api/v1/topics/", json={"title": "Apple Pie", "text": "..."})
    await client.post("/api/v1/topics/", json={"title": "Banana Bread", "text": "..."})

    response = await client.get("/api/v1/topics/?search=Apple")
    
    data = response.json()
    assert data["total"] == 1
    assert data["topics"][0]["title"] == "Apple Pie"


async def test_filter_by_category(client: AsyncClient, db_session, mock_current_user):
    """
    If the category filter works?
    """
    cat = Category(name="News")
    db_session.add(cat)
    await db_session.commit()
    await db_session.refresh(cat) 

    await client.post("/api/v1/topics/", json={
        "title": "Topic In Category", 
        "text": "...", 
        "category_id": cat.id
    })
    
    await client.post("/api/v1/topics/", json={
        "title": "Topic No Category", 
        "text": "..."
    })

    response = await client.get(f"/api/v1/topics/?category_id={cat.id}")
    
    data = response.json()
    assert data["total"] == 1
    assert data["topics"][0]["title"] == "Topic In Category"


async def test_filter_by_tags(client: AsyncClient, mock_current_user):
    """
    If the tags filter works?
    """
    resp1 = await client.post("/api/v1/topics/", json={
        "title": "Python Topic", 
        "text": "...", 
        "tags": ["python"]
    })
    tag_id = resp1.json()["tags"][0]["id"]

    await client.post("/api/v1/topics/", json={
        "title": "Java Topic", 
        "text": "...", 
        "tags": ["java"]
    })

    response = await client.get(f"/api/v1/topics/?tags={tag_id}")

    data = response.json()
    assert data["total"] == 1
    assert data["topics"][0]["title"] == "Python Topic"


async def test_combined_filter(client: AsyncClient, mock_current_user):
    """
    If the two filters work together (Search + Tag)?
    """
    resp = await client.post("/api/v1/topics/", json={
        "title": "Super Guide", 
        "text": "...", 
        "tags": ["python"]
    })
    tag_id = resp.json()["tags"][0]["id"]

    await client.post("/api/v1/topics/", json={
        "title": "My Story", 
        "text": "...", 
        "tags": ["python"]
    })

    response = await client.get(f"/api/v1/topics/?tags={tag_id}&search=Guide")

    data = response.json()
    assert data["total"] == 1
    assert data["topics"][0]["title"] == "Super Guide"