from pydantic import AliasChoices, BaseModel, Field


class EvaluationCreateRequest(BaseModel):
    assessment_id: str
    overall_score: int | None = Field(
        None,
        validation_alias=AliasChoices("overall_score", "score"),
    )
    mastery_level: str
    confidence_level: str | float | None = Field(
        None,
        validation_alias=AliasChoices("confidence_level", "confidence"),
    )
    strengths: list[str] | None = None
    weaknesses: list[str] | None = None
    misconceptions: list[str] | None = None


class EvaluationResponse(BaseModel):
    id: str
    assessment_id: str
    overall_score: int
    mastery_level: str
    confidence_level: str
    strengths: list[str]
    weaknesses: list[str]
    misconceptions: list[str]
    created_at: str
