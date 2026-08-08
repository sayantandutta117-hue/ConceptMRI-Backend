import pytest
from httpx import AsyncClient

from app.db.models.models import Topic
from app.db.repositories.topic_repository import TopicRepository
from app.main import app


@pytest.mark.asyncio
async def test_list_topics_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/topics")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == []
    assert body["pagination"]["total"] == 0


@pytest.mark.asyncio
async def test_get_topic_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/topics/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_topics_with_data(client: AsyncClient, db_session) -> None:
    topic = Topic(
        subject="Math",
        topic_name="Algebra",
        difficulty="EASY",
        description="Basic algebra",
        learning_objectives=["Solve equations"],
        prerequisites=["Arithmetic"],
        is_archived=False,
    )
    repo = TopicRepository(db_session)
    await repo.create(topic)
    await db_session.flush()

    response = await client.get("/api/v1/topics")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["subject"] == "Math"
    assert body["data"][0]["topic_name"] == "Algebra"


@pytest.mark.asyncio
async def test_get_topic_by_id(client: AsyncClient, db_session) -> None:
    topic = Topic(
        subject="Science",
        topic_name="Physics",
        difficulty="MEDIUM",
        description="Basic physics",
        learning_objectives=None,
        prerequisites=None,
        is_archived=False,
    )
    repo = TopicRepository(db_session)
    await repo.create(topic)
    await db_session.flush()

    response = await client.get(f"/api/v1/topics/{topic.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["subject"] == "Science"
    assert body["data"]["topic_name"] == "Physics"


@pytest.mark.asyncio
async def test_list_topics_filter_by_subject(client: AsyncClient, db_session) -> None:
    topics = [
        Topic(subject="Math", topic_name="Algebra", difficulty="EASY", is_archived=False),
        Topic(subject="Science", topic_name="Physics", difficulty="MEDIUM", is_archived=False),
        Topic(subject="Math", topic_name="Geometry", difficulty="HARD", is_archived=False),
    ]
    repo = TopicRepository(db_session)
    for t in topics:
        await repo.create(t)
    await db_session.flush()

    response = await client.get("/api/v1/topics?subject=Math")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    assert all(t["subject"] == "Math" for t in body["data"])


@pytest.mark.asyncio
async def test_list_topics_filter_by_difficulty(client: AsyncClient, db_session) -> None:
    topics = [
        Topic(subject="Math", topic_name="Algebra", difficulty="EASY", is_archived=False),
        Topic(subject="Science", topic_name="Physics", difficulty="EASY", is_archived=False),
        Topic(subject="Math", topic_name="Geometry", difficulty="HARD", is_archived=False),
    ]
    repo = TopicRepository(db_session)
    for t in topics:
        await repo.create(t)
    await db_session.flush()

    response = await client.get("/api/v1/topics?difficulty=EASY")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    assert all(t["difficulty"] == "EASY" for t in body["data"])


@pytest.mark.asyncio
async def test_create_topic(client: AsyncClient) -> None:
    payload = {
        "subject": "History",
        "topic_name": "World War II",
        "difficulty": "MEDIUM",
        "description": "Major events of WWII",
        "learning_objectives": ["Understand causes", "Analyze outcomes"],
        "prerequisites": ["World War I"],
        "is_archived": False,
    }
    response = await client.post("/api/v1/topics", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["subject"] == "History"
    assert body["data"]["topic_name"] == "World War II"
    assert body["data"]["difficulty"] == "MEDIUM"


@pytest.mark.asyncio
async def test_update_topic(client: AsyncClient, db_session) -> None:
    topic = Topic(
        subject="Math",
        topic_name="Algebra",
        difficulty="EASY",
        is_archived=False,
    )
    repo = TopicRepository(db_session)
    await repo.create(topic)
    await db_session.flush()

    payload = {"topic_name": "Advanced Algebra", "is_archived": True}
    response = await client.patch(f"/api/v1/topics/{topic.id}", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["topic_name"] == "Advanced Algebra"
    assert body["data"]["is_archived"] is True


@pytest.mark.asyncio
async def test_delete_topic(client: AsyncClient, db_session) -> None:
    topic = Topic(
        subject="Math",
        topic_name="Algebra",
        difficulty="EASY",
        is_archived=False,
    )
    repo = TopicRepository(db_session)
    await repo.create(topic)
    await db_session.flush()

    response = await client.delete(f"/api/v1/topics/{topic.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Topic deleted successfully."
