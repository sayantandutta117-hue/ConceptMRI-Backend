from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class Difficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class AssessmentStatus(str, Enum):
    PENDING_EVALUATION = "PENDING_EVALUATION"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    REPORT_AVAILABLE = "REPORT_AVAILABLE"
    FAILED = "FAILED"


class MasteryLevel(str, Enum):
    BEGINNER = "BEGINNER"
    DEVELOPING = "DEVELOPING"
    PROFICIENT = "PROFICIENT"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RecommendationPriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RubricStatus(str, Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
