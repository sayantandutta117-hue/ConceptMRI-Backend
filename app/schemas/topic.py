from pydantic import BaseModel


class TopicResponse(BaseModel):
    id: str
    subject: str
    topic_name: str
    difficulty: str
    description: str | None = None
    learning_objectives: list[str] | None = None
    prerequisites: list[str] | None = None
    is_archived: bool
    created_at: str
    updated_at: str | None = None


class TopicListResponse(BaseModel):
    success: bool = True
    data: list[TopicResponse]
    pagination: dict


class TopicCreateRequest(BaseModel):
    subject: str
    topic_name: str
    difficulty: str
    description: str | None = None
    learning_objectives: list[str] | None = None
    prerequisites: list[str] | None = None
    is_archived: bool = False


class TopicUpdateRequest(BaseModel):
    subject: str | None = None
    topic_name: str | None = None
    difficulty: str | None = None
    description: str | None = None
    learning_objectives: list[str] | None = None
    prerequisites: list[str] | None = None
    is_archived: bool | None = None
