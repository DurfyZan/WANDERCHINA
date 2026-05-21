from datetime import datetime, timedelta

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models import RefreshToken, User, UserStatus
from schemas import UserCreate, UserUpdate
from security import get_password_hash


LOCK_DURATION_MINUTES = 15
MAX_FAILED_ATTEMPTS = 5


async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
    hashed_password = get_password_hash(user_create.password)
    user = User(
        username=user_create.username,
        email=user_create.email,
        password=hashed_password,
        role=user_create.role,
        status=UserStatus.ACTIVE,
        create_time=datetime.utcnow(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_all_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).order_by(User.id))
    return result.scalars().all()


async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> User | None:
    update_data = user_update.dict(exclude_unset=True)
    if not update_data:
        return None

    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(**update_data)
    )
    await db.commit()

    return await get_user_by_id(db, user_id)


async def update_user_password(db: AsyncSession, user_id: int, new_password: str) -> None:
    hashed_password = get_password_hash(new_password)
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(password=hashed_password)
    )
    await db.commit()


async def update_last_login(db: AsyncSession, user_id: int) -> None:
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(last_login_time=datetime.utcnow(), failed_login_attempts=0)
    )
    await db.commit()


async def increment_failed_login(db: AsyncSession, user_id: int) -> bool:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return False

    new_attempts = user.failed_login_attempts + 1
    lock_time = None

    if new_attempts >= MAX_FAILED_ATTEMPTS:
        lock_time = datetime.utcnow() + timedelta(minutes=LOCK_DURATION_MINUTES)

    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(failed_login_attempts=new_attempts, lock_time=lock_time)
    )
    await db.commit()

    return new_attempts >= MAX_FAILED_ATTEMPTS


async def create_refresh_token(db: AsyncSession, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        created_at=datetime.utcnow(),
    )
    db.add(refresh_token)
    await db.commit()
    await db.refresh(refresh_token)
    return refresh_token


async def delete_refresh_token(db: AsyncSession, token: str) -> None:
    await db.execute(delete(RefreshToken).where(RefreshToken.token == token))
    await db.commit()


async def delete_user_refresh_tokens(db: AsyncSession, user_id: int) -> None:
    await db.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))
    await db.commit()
