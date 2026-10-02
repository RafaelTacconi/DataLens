"""Cache keys and membership guard (R36).

Cache keys include the database file's identity (resolved path, mtime_ns,
size) so a changed file is never served stale; query-result keys add the
canonical SQL. A cached result is only returned to a workspace member (SDD
§34, Guide §8).
"""

import os

from app.core.permissions import get_role


def file_identity(path):
    """The (mtime_ns, size) identity of a file.

    Args:
        path: the resolved database path.

    Returns:
        A tuple (mtime_ns, size).
    """
    st = os.stat(path)
    return st.st_mtime_ns, st.st_size


def schema_cache_key(path):
    """The cache key for a database's schema/profile.

    Args:
        path: the resolved database path.

    Returns:
        A string key that changes when the file changes.
    """
    mtime, size = file_identity(path)
    return f"{path}:{mtime}:{size}"


def query_cache_key(path, canonical_sql):
    """The cache key for a query result.

    Args:
        path: the resolved database path.
        canonical_sql: the canonical SQL string.

    Returns:
        A string key that changes when the file or the SQL changes.
    """
    return f"{schema_cache_key(path)}:{canonical_sql}"


def require_membership(conn, workspace_id, user_id):
    """Raise if the user is not a member of the workspace.

    Args:
        conn: the metadata sqlite3 connection.
        workspace_id: the workspace.
        user_id: the user.

    Raises:
        PermissionError: if the user is not a member.
    """
    if get_role(conn, workspace_id, user_id) is None:
        raise PermissionError("not a member of this workspace")