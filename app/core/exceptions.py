from enum import Enum


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    AI_ENGINE_ERROR = "AI_ENGINE_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_INACTIVE = "USER_INACTIVE"
    USER_SUSPENDED = "USER_SUSPENDED"


class AppException(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 400,
        details: list | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found.") -> None:
        super().__init__(
            code=ErrorCode.RESOURCE_NOT_FOUND,
            message=message,
            status_code=404,
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required.") -> None:
        super().__init__(
            code=ErrorCode.UNAUTHORIZED,
            message=message,
            status_code=401,
        )


class ForbiddenError(AppException):
    def __init__(self, message: str = "You do not have permission to access this resource.") -> None:
        super().__init__(
            code=ErrorCode.FORBIDDEN,
            message=message,
            status_code=403,
        )


class ValidationError(AppException):
    def __init__(self, message: str, details: list | None = None) -> None:
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            status_code=422,
            details=details,
        )
