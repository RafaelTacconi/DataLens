"""Workspace view (R16, R5).

Shows a workspace's business context and whether the current user may edit it.
Editing is role-gated in Python, never by hiding a button (SDD §8).
"""

from app.core.permissions import can, get_role
from app.metadata.catalog import get_business_context


def workspace_view(conn, workspace_id, user_id):
    """Return the workspace context and whether the user may edit it.

    Args:
        conn: the metadata sqlite3 connection.
        workspace_id: the workspace to show.
        user_id: the current user.

    Returns:
        A tuple (context, can_edit).
    """
    context = get_business_context(conn, workspace_id)
    role = get_role(conn, workspace_id, user_id)
    can_edit = can(role, "edit_business_context")
    return context, can_edit