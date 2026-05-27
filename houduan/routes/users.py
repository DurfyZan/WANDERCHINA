from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud import get_all_users, get_user_by_id, update_user, update_user_password
from database import get_db
from dependencies import get_current_user, require_admin
from exceptions import UserNotFoundException, ValidationException
from models import User
from schemas import ApiResponse, PasswordChange, UserResponse, UserUpdate

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("/me", response_model=ApiResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    user_response = UserResponse.from_orm(current_user)
    return ApiResponse(code=0, msg="success", data={"user": user_response.dict()})


@router.put("/me/password", response_model=ApiResponse)
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from security import verify_password

    if not verify_password(password_change.old_password, current_user.password):
        raise ValidationException("旧密码错误")

    await update_user_password(db, current_user.id, password_change.new_password)
    return ApiResponse(code=0, msg="密码修改成功")


@router.get("/", response_model=ApiResponse)
async def get_users(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    users = await get_all_users(db)
    user_responses = [UserResponse.from_orm(user).dict() for user in users]
    return ApiResponse(code=0, msg="success", data={"users": user_responses})


@router.get("/{user_id}", response_model=ApiResponse)
async def get_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise UserNotFoundException()

    user_response = UserResponse.from_orm(user)
    return ApiResponse(code=0, msg="success", data={"user": user_response.dict()})


@router.put("/{user_id}", response_model=ApiResponse)
async def update_user_info(
    user_id: int,
    user_update: UserUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await update_user(db, user_id, user_update)
    if not user:
        raise UserNotFoundException()

    user_response = UserResponse.from_orm(user)
    return ApiResponse(code=0, msg="更新成功", data={"user": user_response.dict()})
