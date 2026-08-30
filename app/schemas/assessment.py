from pydantic import BaseModel, Field


class AssessmentCreateRequest(BaseModel):
    student_id: str | None = None
    topic_id: str
    answer: str = Field(..., min_length=20, max_length=5000)


class AssessmentResponse(BaseModel):
    id: str
    student_id: str
    topic_id: str
    answer: str
    status: str
    submitted_at: str
    completed_at: str | None = None
    created_at: str


class AssessmentListResponse(BaseModel):
    success: bool = True
    data: list[AssessmentResponse]
