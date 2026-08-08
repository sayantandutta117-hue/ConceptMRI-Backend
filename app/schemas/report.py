from pydantic import BaseModel, Field


class ReportCreateRequest(BaseModel):
    evaluation_id: str
    overall_score: int
    mastery_level: str
    teacher_summary: str
    student_summary: str
    strengths: list[str]
    weaknesses: list[str]
    misconceptions: list[str]
    recommendations: list[str]


class ReportResponse(BaseModel):
    id: str
    evaluation_id: str
    overall_score: int
    mastery_level: str
    teacher_summary: str
    student_summary: str
    strengths: list[str]
    weaknesses: list[str]
    misconceptions: list[str]
    recommendations: list[str]
    created_at: str
