"""Tests for app/core/permissions.py identity resolution (R4)."""

from app.core.permissions import current_user


def test_current_user_resolves_os_user():
    """R4: the current user is resolved from the OS without asking."""
    user = current_user()
    assert user.user_id
    assert user.username
    assert user.identity_source == "os"


def test_identity_source_is_recorded():
    """R4: the identity source is recorded for audit and permissions."""
    user = current_user()
    assert user.identity_source == "os"