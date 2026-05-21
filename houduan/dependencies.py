from datetime import datetime

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from exceptions import AuthException, ForbiddenException, UserLockedException, UserNotFoundException
from models import RefreshToken, User, UserRole
from security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        raise AuthException("未提供认证令牌")

    payload = decode_token(token)
    if not payload or payload.get("token_type") != "access":
        raise AuthException("无效的认证令牌")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthException("令牌信息无效")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise UserNotFoundException()

    if user.status == "disabled":
        raise AuthException("账号已被禁用")

    if user.lock_time and user.lock_time > datetime.utcnow():
        raise UserLockedException()

    return user


async def require_role(
    *roles: UserRole,
    user: User = Depends(get_current_user),
):
    if user.role not in roles:
        raise ForbiddenException(f"需要角色权限: {', '.join(r.value for r in roles)}")
    return user


async def require_admin(user: User = Depends(get_current_user)):
    return await require_role(UserRole.ADMIN, user=user)


async def get_refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
    token_record = result.scalar_one_or_none()

    if not token_record:
        raise AuthException("无效的刷新令牌")

    if token_record.expires_at < datetime.utcnow():
        raise AuthException("刷新令牌已过期")

    return token_record
