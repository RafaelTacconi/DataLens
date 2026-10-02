"""Tests for app/ui/workspace.py (R16, R5)."""

from app.core.permissions import add_member
from app.metadata.catalog import set_business_context
from app.metadata.store import create_workspace, open_metadata_db
from app.ui.workspace import workspace_view


def _workspace(tmp_path):
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    create_workspace(conn, "w1", "Trading", "data/trades.db")
    return conn


def test_workspace_view_shows_context(tmp_path):
    """R16: the workspace view shows the business context."""
    conn = _workspace(tmp_path)
    try:
        add_member(conn, "w1", "u1", "owner")
        set_business_context(conn, "w1", "Trading volume = SUM(notional_value)")
        context, can_edit = workspace_view(conn, "w1", "u1")
        assert context == "Trading volume = SUM(notional_value)"
        assert can_edit is True
    finally:
        conn.close()


def test_workspace_view_is_role_gated(tmp_path):
    """R5: a Viewer cannot edit the business context."""
    conn = _workspace(tmp_path)
    try:
        add_member(conn, "w1", "u1", "viewer")
        context, can_edit = workspace_view(conn, "w1", "u1")
        assert can_edit is False
    finally:
        conn.close()