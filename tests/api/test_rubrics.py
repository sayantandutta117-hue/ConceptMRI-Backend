import pytest
from httpx import AsyncClient

from app.db.models.models import Rubric, Topic
from app.db.repositories.rubric_repository import RubricRepository
from app.db.repositories.topic_repository import TopicRepository
from app.main import app


@pytest.mark.asyncio
async def test_create_rubric(client: AsyncClient, db_session) -> None:
    topic = Topic(
        subject="Math",
        topic_name="Algebra",
        difficulty="EASY",
        is_archived=False,
    )
    topic_repo = TopicRepository(db_session)
    await topic_repo.create(topic)
    await db_session.flush()

    payload = {
        "topic_id": str(topic.id),
        "concepts": [{"name": "Equations"}],
        "evaluation_rules": [{"rule": "Check steps"}],
        "common_misconceptions": [{"misconception": "Sign errors"}],
    }
    response = await client.post("/api/v1/rubrics", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["topic_id"] == str(topic.id)
    assert len(body["data"]["concepts"]) == 1


@pytest.mark.asyncio
async def test_create_rubric_with_string_lists(client: AsyncClient, db_session) -> None:
    topic = Topic(
        subject="Math",
        topic_name="Algebra",
        difficulty="EASY",
        is_archived=False,
    )
    topic_repo = TopicRepository(db_session)
    await topic_repo.create(topic)
    await db_session.flush()

    payload = {
        "topic_id": str(topic.id),
        "concepts": ["Base case", "Recursive call"],
        "evaluation_rules": ["Checks recursion understanding"],
        "common_misconceptions": ["Infinite recursion"],
    }
    response = await client.post("/api/v1/rubrics", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["concepts"] == ["Base case", "Recursive call"]


@pytest.mark.asyncio
async def test_get_rubrics_by_topic_id_empty(client: AsyncClient, db_session) -> None:
    topic = Topic(
        subject="Math",
        topic_name="Algebra",
        difficulty="EASY",
        is_archived=False,
    )
    topic_repo = TopicRepository(db_session)
    await topic_repo.create(topic)
    await db_session.flush()

    response = await client.get(f"/api/v1/rubrics/{topic.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == []


@pytest.mark.asyncio
async def test_get_rubrics_by_topic_id_with_data(client: AsyncClient, db_session) -> None:
    topic = Topic(
        subject="Math",
        topic_name="Algebra",
        difficulty="EASY",
        is_archived=False,
    )
    topic_repo = TopicRepository(db_session)
    await topic_repo.create(topic)
    await db_session.flush()

    rubric = Rubric(
        topic_id=topic.id,
        concepts=[{"name": "Equations"}],
        evaluation_rules=[{"rule": "Check steps"}],
        common_misconceptions=[{"misconception": "Sign errors"}],
        status="ACTIVE",
    )
    rubric_repo = RubricRepository(db_session)
    await rubric_repo.create(rubric)
    await db_session.flush()

    response = await client.get(f"/api/v1/rubrics/{topic.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["topic_id"] == str(topic.id)
    assert body["data"][0]["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_get_rubrics_by_topic_id_invalid_uuid(client: AsyncClient) -> None:
    response = await client.get("/api/v1/rubrics/not-a-uuid")
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
