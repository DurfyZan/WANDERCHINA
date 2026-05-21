from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_user, require_admin, require_role
from exceptions import ForbiddenException
from models import User, UserRole
from schemas import ApiResponse

router = APIRouter(prefix="/api/permissions", tags=["权限测试"])


@router.get("/test", response_model=ApiResponse)
async def test_auth(
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(
        code=0,
        msg="success",
        data={
            "user_id": current_user.id,
            "username": current_user.username,
            "role": current_user.role.value,
        },
    )


@router.get("/test/admin", response_model=ApiResponse)
async def test_admin_permission(
    admin: User = Depends(require_admin),
):
    return ApiResponse(
        code=0,
        msg="success",
        data={
            "message": "管理员权限验证通过",
            "user_id": admin.id,
            "username": admin.username,
        },
    )


@router.get("/test/annotator", response_model=ApiResponse)
async def test_annotator_permission(
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANNOTATOR)),
):
    return ApiResponse(
        code=0,
        msg="success",
        data={
            "message": "标注员权限验证通过",
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
        },
    )


@router.get("/test/user", response_model=ApiResponse)
async def test_user_permission(
    user: User = Depends(get_current_user),
):
    if user.role not in [UserRole.ADMIN, UserRole.ANNOTATOR, UserRole.USER]:
        raise ForbiddenException()

    return ApiResponse(
        code=0,
        msg="success",
        data={
            "message": "普通用户权限验证通过",
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
        },
    )
