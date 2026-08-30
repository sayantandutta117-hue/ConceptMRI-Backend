from pydantic import BaseModel


class RubricResponse(BaseModel):
    id: str
    topic_id: str
    concepts: list[str | dict]
    evaluation_rules: list[str | dict]
    common_misconceptions: list[str | dict]
    status: str
    created_at: str


class RubricListResponse(BaseModel):
    success: bool = True
    data: list[RubricResponse]
