from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_profile_complete, require_roles
from app.core.enums import UserRole
from app.core.profile import is_profile_complete, missing_profile_fields
from app.db.session import get_db
from app.models.user import User
from app.schemas.community import (
    CommentCreate,
    CommentRead,
    InteractionCreate,
    ModerationUpdate,
    PostCreate,
    PostDetailRead,
    PostRead,
    TranslateRequest,
)
from app.schemas.profile import CommunityAccessStatus
from app.services.community_service import CommunityService
from app.services.model_client import ModelServiceClient
from app.services.profile_service import ProfileService

# 社区模块：须先登录
router = APIRouter(dependencies=[Depends(get_current_user)])

# 进入社区浏览/互动：须已完善头像与姓名
protected = APIRouter(dependencies=[Depends(require_profile_complete)])


@router.get("/access", response_model=CommunityAccessStatus)
async def community_access_check(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """进入社区前调用：判断是否已登录、资料是否完善。"""
    profile = ProfileService(db).to_profile_read(user)
    complete = is_profile_complete(user)
    return CommunityAccessStatus(
        authenticated=True,
        profile_completed=complete,
        can_enter_community=complete,
        missing_fields=missing_profile_fields(user),
        user=profile,
    )


@protected.post("/posts", response_model=PostRead, status_code=201)
async def create_post(
    data: PostCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await CommunityService(db).create_post(user, data)


@protected.get("/posts", response_model=list[PostRead])
async def list_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 20,
    offset: int = 0,
):
    return await CommunityService(db).list_posts(limit, offset)


@protected.get("/posts/{post_id}", response_model=PostDetailRead)
async def get_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    post = await CommunityService(db).get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@protected.get("/posts/{post_id}/comments", response_model=list[CommentRead])
async def list_comments(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await CommunityService(db).list_comments(post_id)


@protected.post("/posts/{post_id}/comments", response_model=CommentRead, status_code=201)
async def create_comment(
    post_id: int,
    data: CommentCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await CommunityService(db).add_comment(user, post_id, data)


@protected.post("/posts/{post_id}/interactions", status_code=201)
async def interact(
    post_id: int,
    data: InteractionCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await CommunityService(db).add_interaction(user, post_id, data.interaction_type)
    return {"ok": True}


@protected.patch("/posts/{post_id}/moderation")
async def moderate_post(
    post_id: int,
    data: ModerationUpdate,
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    from sqlalchemy import select

    from app.models.community import Post

    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.moderation_status = data.status.value
    return {"id": post_id, "status": post.moderation_status}


@protected.post("/translate")
async def translate_text(data: TranslateRequest):
    translation = await ModelServiceClient().translate(data.text, data.source_lang, data.target_lang)
    return {"translation": translation, "target_lang": data.target_lang}


router.include_router(protected)
