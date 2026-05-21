from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from crud import (
    create_refresh_token,
    create_user,
    delete_refresh_token,
    delete_user_refresh_tokens,
    get_user_by_email,
    get_user_by_username,
    increment_failed_login,
    update_last_login,
)
from database import get_db
from dependencies import get_current_user
from exceptions import AuthException, UserLockedException, ValidationException
from models import User, UserRole
from schemas import ApiResponse, TokenRefresh, TokenResponse, UserCreate, UserResponse
from security import create_access_token, create_refresh_token as create_jwt_refresh_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=ApiResponse)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    if await get_user_by_username(db, user_create.username):
        raise ValidationException("用户名已存在")

    if await get_user_by_email(db, user_create.email):
        raise ValidationException("邮箱已被注册")

    user = await create_user(db, user_create)
    user_response = UserResponse.from_orm(user)

    return ApiResponse(code=0, msg="注册成功", data={"user": user_response.dict()})


@router.post("/login", response_model=ApiResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_username(db, form_data.username)

    if not user:
        raise AuthException("账号不存在")

    if user.status == "disabled":
        raise AuthException("账号已被禁用")

    if user.lock_time and user.lock_time > datetime.utcnow():
        raise UserLockedException()

    if not verify_password(form_data.password, user.password):
        is_locked = await increment_failed_login(db, user.id)
        if is_locked:
            raise UserLockedException("密码错误次数过多，账号已被锁定")
        raise AuthException("密码错误")

    await update_last_login(db, user.id)

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_jwt_refresh_token(data={"sub": user.id})
    refresh_expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    await create_refresh_token(db, user.id, refresh_token, refresh_expire)

    user_response = UserResponse.from_orm(user)

    return ApiResponse(
        code=0,
        msg="登录成功",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user_response.dict(),
        },
    )


@router.post("/refresh", response_model=ApiResponse)
async def refresh_token(
    token_refresh: TokenRefresh,
    db: AsyncSession = Depends(get_db),
):
    from dependencies import get_refresh_token

    token_record = await get_refresh_token(token_refresh.refresh_token, db)

    user = await get_user_by_username(db, token_record.user_id)
    if not user:
        raise AuthException("用户不存在")

    if user.status == "disabled":
        raise AuthException("账号已被禁用")

    await delete_refresh_token(db, token_refresh.refresh_token)

    access_token = create_access_token(data={"sub": user.id})
    new_refresh_token = create_jwt_refresh_token(data={"sub": user.id})
    refresh_expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    await create_refresh_token(db, user.id, new_refresh_token, refresh_expire)

    user_response = UserResponse.from_orm(user)

    return ApiResponse(
        code=0,
        msg="刷新成功",
        data={
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": user_response.dict(),
        },
    )


@router.post("/logout", response_model=ApiResponse)
async def logout(
    token_refresh: TokenRefresh,
    db: AsyncSession = Depends(get_db),
):
    await delete_refresh_token(db, token_refresh.refresh_token)
    return ApiResponse(code=0, msg="登出成功")


@router.post("/logout-all", response_model=ApiResponse)
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_user_refresh_tokens(db, current_user.id)
    return ApiResponse(code=0, msg="已退出所有设备")
