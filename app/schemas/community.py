from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import ContentType, ModerationStatus


class PostCreate(BaseModel):
    title: str | None = None
    body: str = Field(min_length=1)
    content_type: ContentType = ContentType.POST
    language: str = "zh"
    image_urls: list[str] | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_name: str | None = None
    topic_tags: list[str] | None = None


class AuthorBrief(BaseModel):
    id: int
    display_name: str | None = None
    avatar_url: str | None = None
    role: str


class PostRead(BaseModel):
    id: int
    author_id: int
    author: AuthorBrief | None = None
    title: str | None
    body: str
    content_type: str
    language: str
    location_name: str | None
    topic_tags: str | None
    moderation_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    body: str = Field(min_length=1)
    language: str = "zh"


class CommentRead(BaseModel):
    id: int
    post_id: int
    author_id: int
    author: AuthorBrief | None = None
    body: str
    language: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PostDetailRead(PostRead):
    comments: list[CommentRead] = []


class InteractionCreate(BaseModel):
    interaction_type: str = Field(pattern="^(like|share)$")


class ModerationUpdate(BaseModel):
    status: ModerationStatus
    reason: str | None = None


class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str = "en"
