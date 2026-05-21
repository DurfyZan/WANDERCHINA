from types import SimpleNamespace

from app.core.profile import is_profile_complete, missing_profile_fields


def _user(**kwargs):
    defaults = {"display_name": None, "avatar_url": None}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_profile_incomplete_without_avatar():
    user = _user(display_name="Alice")
    assert not is_profile_complete(user)
    assert "avatar_url" in missing_profile_fields(user)


def test_profile_incomplete_without_name():
    user = _user(avatar_url="/uploads/avatars/1.png")
    assert not is_profile_complete(user)
    assert "display_name" in missing_profile_fields(user)


def test_profile_complete():
    user = _user(display_name="Alice", avatar_url="/uploads/avatars/1.png")
    assert is_profile_complete(user)
    assert missing_profile_fields(user) == []
