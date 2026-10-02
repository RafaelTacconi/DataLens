"""Identity and permissions (R4, R5).

Identity is the OS user, fetched automatically and never asked (Part 5). The
identity source is recorded so a self-declared or weak attribution is never
mistaken for strong identity (SDD §9). Workspace roles are enforced in Python
(SDD §8), never by hiding a button in the UI.
"""

import getpass
from dataclasses import dataclass

ROLES = ("viewer", "contributor", "owner")

# SDD §8: which roles may perform each action.
ROLE_MATRIX = {
    "ask_questions": ("viewer", "contributor", "owner"),
    "view_results": ("viewer", "contributor", "owner"),
    "give_feedback": ("viewer", "contributor", "owner"),
    "edit_business_context": ("contributor", "owner"),
    "edit_catalog": ("contributor", "owner"),
    "edit_business_terms": ("contributor", "owner"),
    "manage_verified_queries": ("contributor", "owner"),
    "manage_evaluation_cases": ("contributor", "owner"),
    "change_database_path": ("contributor", "owner"),
    "manage_members": ("owner",),
    "change_egress_policy": ("owner",),
    "archive_workspace": ("owner",),
}


@dataclass(frozen=True)
class User:
    """A resolved user, with the source of the identity recorded."""

    user_id: str
    username: str
    identity_source: str = "os"


def current_user() -> User:
    """Resolve the current OS user without asking.

    Returns:
        A User whose identity_source is "os".
    """
    username = getpass.getuser()
    return User(user_id=username, username=username, identity_source="os")


def can(role, action):
    """Whether a role may perform an action (R5).

    Args:
        role: "viewer", "contributor" or "owner".
        action: an action name from ROLE_MATRIX.

    Returns:
        True if the role is allowed the action.
    """
    return role in ROLE_MATRIX.get(action, ())


def add_member(conn, workspace_id, user_id, role):
    """Add a member to a workspace with a role (R5)."""
    conn.execute(
        "INSERT INTO memberships (workspace_id, user_id, role, identity_source) "
        "VALUES (?, ?, ?, 'os')",
        (workspace_id, user_id, role),
    )
    conn.commit()


def get_role(conn, workspace_id, user_id):
    """The role of a user in a workspace, or None if they are not a member."""
    row = conn.execute(
        "SELECT role FROM memberships WHERE workspace_id=? AND user_id=?",
        (workspace_id, user_id),
    ).fetchone()
    return row["role"] if row else None


def _owner_count(conn, workspace_id):
    """How many Owners a workspace currently has."""
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM memberships "
        "WHERE workspace_id=? AND role='owner'",
        (workspace_id,),
    ).fetchone()
    return row["n"]


def set_role(conn, workspace_id, user_id, role):
    """Change a member's role, refusing to demote the last Owner (R5).

    Raises:
        PermissionError: if the change would leave the workspace with no Owner.
    """
    if (get_role(conn, workspace_id, user_id) == "owner"
            and role != "owner" and _owner_count(conn, workspace_id) <= 1):
        raise PermissionError("cannot demote the last Owner of a workspace")
    conn.execute(
        "UPDATE memberships SET role=? WHERE workspace_id=? AND user_id=?",
        (role, workspace_id, user_id),
    )
    conn.commit()


def remove_member(conn, workspace_id, user_id):
    """Remove a member, refusing to remove the last Owner (R5).

    Raises:
        PermissionError: if the removal would leave the workspace with no Owner.
    """
    if (get_role(conn, workspace_id, user_id) == "owner"
            and _owner_count(conn, workspace_id) <= 1):
        raise PermissionError("cannot remove the last Owner of a workspace")
    conn.execute(
        "DELETE FROM memberships WHERE workspace_id=? AND user_id=?",
        (workspace_id, user_id),
    )
    conn.commit()