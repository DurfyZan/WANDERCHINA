from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from models import UserRole, UserStatus


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="登录账号")
    email: EmailStr = Field(..., description="绑定邮箱")
    password: str = Field(..., min_length=8, max_length=128, description="密码（至少8位）")
    role: UserRole = Field(default=UserRole.USER, description="用户角色")


class UserLogin(BaseModel):
    username: str = Field(..., description="登录账号")
    password: str = Field(..., description="密码")


class TokenRefresh(BaseModel):
    refresh_token: str = Field(..., description="刷新令牌")


class PasswordChange(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    status: UserStatus
    create_time: datetime
    last_login_time: Optional[datetime]

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="绑定邮箱")
    role: Optional[UserRole] = Field(None, description="用户角色")
    status: Optional[UserStatus] = Field(None, description="账号状态")


class ApiResponse(BaseModel):
    code: int = Field(0, description="状态码，0表示成功")
    msg: str = Field("success", description="提示信息")
    data: Optional[dict] = Field(None, description="返回数据")
