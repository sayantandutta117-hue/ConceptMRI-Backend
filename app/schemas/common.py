from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[Any] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    timestamp: datetime = Field(default_factory=utc_now)


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    pages: int


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str | None = None
    data: T | None = None
    timestamp: datetime = Field(default_factory=utc_now)


class PaginatedAPIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str | None = None
    data: T
    pagination: PaginationMeta
    timestamp: datetime = Field(default_factory=utc_now)


def success_response(
    data: Any = None,
    message: str | None = None,
) -> dict[str, Any]:
    return APIResponse(data=data, message=message).model_dump(mode="json")
