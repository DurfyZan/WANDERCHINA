import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.profile import is_profile_complete, missing_profile_fields
from app.models.user import User
from app.schemas.profile import ProfileUpdate, UserProfileRead

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
CONTENT_TYPE_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


class ProfileService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.settings = get_settings()

    def to_profile_read(self, user: User) -> UserProfileRead:
        missing = missing_profile_fields(user)
        return UserProfileRead(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            preferred_languages=user.preferred_languages,
            location_tags=user.location_tags,
            profile_completed=is_profile_complete(user),
            missing_fields=missing,
            created_at=user.created_at,
        )

    async def update_profile(self, user: User, data: ProfileUpdate) -> UserProfileRead:
        if data.display_name is not None:
            user.display_name = data.display_name.strip()
        if data.bio is not None:
            user.bio = data.bio.strip() or None
        if data.preferred_languages is not None:
            user.preferred_languages = data.preferred_languages
        if data.location_tags is not None:
            user.location_tags = data.location_tags
        await self.db.flush()
        await self.db.refresh(user)
        return self.to_profile_read(user)

    async def upload_avatar(self, user: User, file: UploadFile) -> UserProfileRead:
        if not file.content_type or file.content_type not in self.settings.allowed_avatar_types.split(","):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"仅支持: {self.settings.allowed_avatar_types}",
            )

        content = await file.read()
        max_bytes = self.settings.max_avatar_size_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"头像大小不能超过 {self.settings.max_avatar_size_mb}MB",
            )

        ext = CONTENT_TYPE_TO_EXT.get(file.content_type) or Path(file.filename or "").suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            ext = ".jpg"

        upload_root = Path(self.settings.upload_dir) / "avatars"
        upload_root.mkdir(parents=True, exist_ok=True)

        filename = f"{user.id}_{uuid.uuid4().hex}{ext}"
        dest = upload_root / filename
        dest.write_bytes(content)

        user.avatar_url = f"/uploads/avatars/{filename}"
        await self.db.flush()
        await self.db.refresh(user)
        return self.to_profile_read(user)
