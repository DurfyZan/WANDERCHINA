import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.community import Comment, Interaction, Post
from app.models.user import User
from app.schemas.community import (
    AuthorBrief,
    CommentCreate,
    CommentRead,
    PostCreate,
    PostDetailRead,
    PostRead,
)
from app.services.model_client import ModelServiceClient


def _author_brief(user: User | None) -> AuthorBrief | None:
    if not user:
        return None
    return AuthorBrief(
        id=user.id,
        display_name=user.display_name or user.username,
        avatar_url=user.avatar_url,
        role=user.role,
    )


def post_to_read(post: Post) -> PostRead:
    return PostRead(
        id=post.id,
        author_id=post.author_id,
        author=_author_brief(post.author),
        title=post.title,
        body=post.body,
        content_type=post.content_type,
        language=post.language,
        location_name=post.location_name,
        topic_tags=post.topic_tags,
        moderation_status=post.moderation_status,
        created_at=post.created_at,
    )


def comment_to_read(comment: Comment) -> CommentRead:
    return CommentRead(
        id=comment.id,
        post_id=comment.post_id,
        author_id=comment.author_id,
        author=_author_brief(comment.author),
        body=comment.body,
        language=comment.language,
        created_at=comment.created_at,
    )


class CommunityService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.models = ModelServiceClient()

    async def create_post(self, author: User, data: PostCreate) -> Post:
        mod = await self.models.moderate(data.body)
        status = "approved" if mod.get("safe", True) else "needs_review"
        post = Post(
            author_id=author.id,
            title=data.title,
            body=data.body,
            content_type=data.content_type.value,
            language=data.language,
            image_urls=json.dumps(data.image_urls) if data.image_urls else None,
            latitude=data.latitude,
            longitude=data.longitude,
            location_name=data.location_name,
            topic_tags=",".join(data.topic_tags) if data.topic_tags else None,
            moderation_status=status,
            source="user",
        )
        post.author = author
        self.db.add(post)
        await self.db.flush()
        return post_to_read(post)

    async def list_posts(self, limit: int = 20, offset: int = 0) -> list[PostRead]:
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.author))
            .where(Post.moderation_status.in_(["approved", "pending"]))
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [post_to_read(p) for p in result.scalars().all()]

    async def get_post(self, post_id: int) -> PostDetailRead | None:
        result = await self.db.execute(
            select(Post)
            .options(
                selectinload(Post.author),
                selectinload(Post.comments).selectinload(Comment.author),
            )
            .where(Post.id == post_id)
        )
        post = result.scalar_one_or_none()
        if not post:
            return None
        base = post_to_read(post)
        comments = sorted(post.comments, key=lambda c: c.created_at)
        return PostDetailRead(
            **base.model_dump(),
            comments=[comment_to_read(c) for c in comments],
        )

    async def list_comments(self, post_id: int) -> list[CommentRead]:
        result = await self.db.execute(
            select(Comment)
            .options(selectinload(Comment.author))
            .where(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())
        )
        return [comment_to_read(c) for c in result.scalars().all()]

    async def add_comment(self, author: User, post_id: int, data: CommentCreate) -> CommentRead:
        comment = Comment(
            post_id=post_id,
            author_id=author.id,
            body=data.body,
            language=data.language,
        )
        comment.author = author
        self.db.add(comment)
        await self.db.flush()
        return comment_to_read(comment)

    async def add_interaction(self, user: User, post_id: int, interaction_type: str) -> Interaction:
        interaction = Interaction(user_id=user.id, post_id=post_id, interaction_type=interaction_type)
        self.db.add(interaction)
        await self.db.flush()
        await self.db.refresh(interaction)
        return interaction
