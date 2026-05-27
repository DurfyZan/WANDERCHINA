from typing import Protocol


class ProfileLike(Protocol):
    display_name: str | None
    avatar_url: str | None


REQUIRED_PROFILE_FIELDS = ("display_name", "avatar_url")


def missing_profile_fields(user: ProfileLike) -> list[str]:
    missing = []
    if not (user.display_name and user.display_name.strip()):
        missing.append("display_name")
    if not (user.avatar_url and user.avatar_url.strip()):
        missing.append("avatar_url")
    return missing


def is_profile_complete(user: ProfileLike) -> bool:
    return len(missing_profile_fields(user)) == 0
