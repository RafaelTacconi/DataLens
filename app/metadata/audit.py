"""Append-only audit logging (R3, R12).

The audit_events table is append-only: the schema installs triggers that abort
any UPDATE or DELETE. This module only ever inserts.
"""

import datetime
import json


def _now():
    """The current UTC timestamp as an ISO string."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _json(value):
    """A value as a JSON string, or None."""
    if value is None:
        return None
    return json.dumps(value)


def append_audit(conn, event_type, workspace_id=None, actor=None,
                 identity_source=None, target=None, before=None, after=None):
    """Append one audit event to the metadata store.

    Args:
        conn: the metadata sqlite3 connection.
        event_type: the kind of event (e.g. "query_run", "workspace_created").
        workspace_id: the workspace the event concerns, if any.
        actor: the user who caused the event, if any.
        identity_source: how the actor was identified (e.g. "os").
        target: an optional target/reference for the event.
        before: optional before-state, serialised to JSON.
        after: optional after-state, serialised to JSON.

    Returns:
        The id of the inserted row.
    """
    cur = conn.execute(
        "INSERT INTO audit_events (event_type, workspace_id, actor, "
        "identity_source, timestamp, target, before_json, after_json) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (event_type, workspace_id, actor, identity_source, _now(), target,
         _json(before), _json(after)),
    )
    conn.commit()
    return cur.lastrowid


def log_query_run(conn, workspace_id, user_id, question, canonical_sql):
    """Audit a query run (R12).

    Args:
        conn: the metadata sqlite3 connection.
        workspace_id: the workspace the query ran in.
        user_id: the user who asked the question.
        question: the user's natural-language question.
        canonical_sql: the canonical SQL that was executed.

    Returns:
        The id of the inserted audit row.
    """
    return append_audit(
        conn,
        event_type="query_run",
        workspace_id=workspace_id,
        actor=user_id,
        identity_source="os",
        target=canonical_sql,
    )