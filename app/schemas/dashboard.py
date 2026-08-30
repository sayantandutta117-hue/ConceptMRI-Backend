from pydantic import BaseModel


class RecentReport(BaseModel):
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


class StudentDashboardResponse(BaseModel):
    total_assessments: int
    completed_evaluations: int
    average_score: float | None = None
    recent_reports: list[RecentReport] = []


class TeacherDashboardResponse(BaseModel):
    total_students: int
    total_assessments: int
    average_class_score: float | None = None


class AdminDashboardResponse(BaseModel):
    total_users: int
    total_topics: int
    total_assessments: int
    total_evaluations: int
