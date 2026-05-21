from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.community import AuthorBrief, CommentRead, PostRead


class PaginatedPosts(BaseModel):
    items: list[PostRead]
    page: int
    page_size: int
    total: int
    has_more: bool


class PaginatedComments(BaseModel):
    items: list[CommentRead]
    page: int
    page_size: int
    total: int
    has_more: bool


class GenerateContentRequest(BaseModel):
    type: str = Field(pattern="^(post|comment|qa)$")
    prompt: str = Field(min_length=4)
    tags: list[str] = Field(default_factory=list)


class GenerateContentResponse(BaseModel):
    generated_text: str
    type: str
    tags: list[str] = []


class SearchResult(BaseModel):
    items: list[PostRead]
    page: int
    page_size: int
    total: int
    query: str
    tags: list[str] = []


class UserPublicProfile(BaseModel):
    id: int
    username: str
    display_name: str | None
    avatar_url: str | None
    role: str
    bio: str | None
    post_count: int = 0


class InteractionItem(BaseModel):
    id: int
    post_id: int
    post_title: str | None
    interaction_type: str
    created_at: datetime
