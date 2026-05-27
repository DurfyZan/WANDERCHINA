from pydantic import BaseModel, EmailStr, Field

from app.core.enums import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=8)
    role: UserRole = UserRole.TOURIST
    preferred_languages: str = "en,zh"


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: UserRole
    preferred_languages: str | None = None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(Token):
    profile_completed: bool = False
    missing_fields: list[str] = []
