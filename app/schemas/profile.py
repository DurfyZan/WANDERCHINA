from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import UserRole


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=64, description="姓名/昵称")
    bio: str | None = Field(default=None, max_length=500)
    preferred_languages: str | None = Field(default=None, max_length=128)
    location_tags: str | None = Field(default=None, max_length=512)


class UserProfileRead(BaseModel):
    id: int
    email: str
    username: str
    role: UserRole
    display_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    preferred_languages: str | None = None
    location_tags: str | None = None
    profile_completed: bool = False
    missing_fields: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class CommunityAccessStatus(BaseModel):
    authenticated: bool = True
    profile_completed: bool
    can_enter_community: bool
    missing_fields: list[str] = []
    user: UserProfileRead | None = None
