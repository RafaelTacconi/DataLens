"""Tests for app/core/permissions.py roles and membership (R5)."""

import pytest

from app.core.permissions import (
    add_member,
    can,
    get_role,
    remove_member,
    set_role,
)
from app.metadata.store import create_workspace, open_metadata_db


def test_role_matrix():
    """R5: the Viewer/Contributor/Owner matrix from SDD §8 is enforced."""
    assert can("viewer", "ask_questions")
    assert can("viewer", "view_results")
    assert can("viewer", "give_feedback")
    assert not can("viewer", "edit_business_context")
    assert not can("viewer", "manage_members")

    assert can("contributor", "edit_business_context")
    assert can("contributor", "edit_catalog")
    assert can("contributor", "change_database_path")
    assert not can("contributor", "manage_members")
    assert not can("contributor", "change_egress_policy")

    assert can("owner", "manage_members")
    assert can("owner", "change_egress_policy")
    assert can("owner", "archive_workspace")


def test_last_owner_cannot_be_removed(tmp_path):
    """R5: removing the last Owner of a workspace is refused."""
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    try:
        create_workspace(conn, "w1", "Trading", "data/trades.db")
        add_member(conn, "w1", "u1", "owner")
        add_member(conn, "w1", "u2", "viewer")
        with pytest.raises(PermissionError):
            remove_member(conn, "w1", "u1")
        # a non-owner can be removed
        remove_member(conn, "w1", "u2")
        assert get_role(conn, "w1", "u2") is None
    finally:
        conn.close()


def test_last_owner_cannot_be_demoted(tmp_path):
    """R5: demoting the last Owner of a workspace is refused."""
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    try:
        create_workspace(conn, "w1", "Trading", "data/trades.db")
        add_member(conn, "w1", "u1", "owner")
        with pytest.raises(PermissionError):
            set_role(conn, "w1", "u1", "viewer")
    finally:
        conn.close()