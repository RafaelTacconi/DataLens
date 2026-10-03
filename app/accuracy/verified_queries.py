"""Verified query library (R30).

Contributors/Owners promote a correct result into the verified library. When
the schema or context changes, a verified query is marked needs_recheck and
is not used until re-verified (SDD §31).
"""

import datetime


def _now():
    """The current UTC timestamp as an ISO string."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def promote_verified_query(conn, workspace_id, question, canonical_sql,
                           context_version=None):
    """Promote a result into the verified query library.

    Args:
        conn: the metadata sqlite3 connection.
        workspace_id: the workspace.
        question: the original question.
        canonical_sql: the canonical SQL.
        context_version: the context version it was verified against.
    """
    conn.execute(
        "INSERT INTO verified_queries (workspace_id, question, canonical_sql, "
        "context_version, status, created_at) VALUES (?, ?, ?, ?, 'verified', ?)",
        (workspace_id, question, canonical_sql, context_version, _now()),
    )
    conn.commit()


def mark_needs_recheck(conn, workspace_id, context_version):
    """Mark verified queries as needs_recheck after a schema/context change.

    Args:
        conn: the metadata sqlite3 connection.
        workspace_id: the workspace.
        context_version: the new context version.
    """
    conn.execute(
        "UPDATE verified_queries SET status='needs_recheck' "
        "WHERE workspace_id=? AND (context_version IS NULL "
        "OR context_version != ?)",
        (workspace_id, context_version),
    )
    conn.commit()


def get_verified_queries(conn, workspace_id, status="verified"):
    """Return verified queries with a given status.

    Args:
        conn: the metadata sqlite3 connection.
        workspace_id: the workspace.
        status: the status to filter by.

    Returns:
        A list of dicts.
    """
    rows = conn.execute(
        "SELECT * FROM verified_queries WHERE workspace_id=? AND status=?",
        (workspace_id, status),
    ).fetchall()
    return [dict(r) for r in rows]