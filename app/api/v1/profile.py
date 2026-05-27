from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.models.user import User
from app.db.session import get_db
from app.schemas.profile import ProfileUpdate, UserProfileRead
from app.services.profile_service import ProfileService

router = APIRouter()


@router.get("/me", response_model=UserProfileRead)
async def get_my_profile(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return ProfileService(db).to_profile_read(user)


@router.put("/me", response_model=UserProfileRead)
async def update_my_profile(
    data: ProfileUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await ProfileService(db).update_profile(user, data)


@router.post("/avatar", response_model=UserProfileRead)
async def upload_avatar(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(..., description="头像图片"),
):
    return await ProfileService(db).upload_avatar(user, file)
