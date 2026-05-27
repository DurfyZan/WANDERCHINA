from enum import StrEnum


class UserRole(StrEnum):
    TOURIST = "tourist"
    STUDENT = "student"
    LOCAL = "local"
    ADMIN = "admin"


class ContentType(StrEnum):
    POST = "post"
    COMMENT = "comment"
    QA_PAIR = "qa_pair"
    RECOMMENDATION = "recommendation"


class GenerationType(StrEnum):
    POST = "post"
    COMMENT = "comment"
    QA_PAIR = "qa_pair"
    RECOMMENDATION = "recommendation"


class ModerationStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class SentimentLabel(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class LLMProvider(StrEnum):
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    OPENAI_COMPAT = "openai_compat"
