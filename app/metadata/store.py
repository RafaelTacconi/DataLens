"""The metadata SQLite store (R2).

A separate SQLite database, in WAL mode, holding the application's own state:
workspaces, memberships, context, catalog, business terms, profiles, verified
queries, evaluation cases, query runs and audit events. It is always a
different file from every target business database (SDD §4, §10).
"""

import datetime
import sqlite3

_SCHEMA = """
CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    target_db_path TEXT NOT NULL,
    business_context TEXT,
    egress_level TEXT NOT NULL DEFAULT 'schema_only',
    created_at TEXT NOT NULL,
    archived_at TEXT
);

CREATE TABLE IF NOT EXISTS memberships (
    workspace_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    identity_source TEXT NOT NULL,
    PRIMARY KEY (workspace_id, user_id)
);

CREATE TABLE IF NOT EXISTS context_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    content TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS catalog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    object_type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    exposed INTEGER NOT NULL DEFAULT 1,
    context_version INTEGER
);

CREATE TABLE IF NOT EXISTS business_terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    term TEXT NOT NULL,
    definition TEXT NOT NULL,
    context_version INTEGER
);

CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    profile_json TEXT,
    file_identity TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS verified_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    question TEXT NOT NULL,
    plan_json TEXT,
    canonical_sql TEXT NOT NULL,
    context_version INTEGER,
    status TEXT NOT NULL DEFAULT 'verified',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evaluation_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    question TEXT NOT NULL,
    expected_columns_json TEXT,
    expected_rows_json TEXT,
    order_matters INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS query_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    question TEXT NOT NULL,
    canonical_sql TEXT,
    result_metadata_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    workspace_id TEXT,
    actor TEXT,
    identity_source TEXT,
    timestamp TEXT NOT NULL,
    target TEXT,
    before_json TEXT,
    after_json TEXT
);

-- R3: audit rows are append-only. Application code cannot update or delete
-- them; the triggers abort either attempt at the database level.
CREATE TRIGGER IF NOT EXISTS audit_events_no_update
BEFORE UPDATE ON audit_events
BEGIN
    SELECT RAISE(ABORT, 'audit_events are append-only');
END;

CREATE TRIGGER IF NOT EXISTS audit_events_no_delete
BEFORE DELETE ON audit_events
BEGIN
    SELECT RAISE(ABORT, 'audit_events are append-only');
END;
"""


def open_metadata_db(path):
    """Open (creating if needed) the metadata SQLite database in WAL mode.

    Args:
        path: the file path of the metadata database.

    Returns:
        A sqlite3.Connection with the schema applied and WAL journaling on.
    """
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


def _now():
    """The current UTC timestamp as an ISO string."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def create_workspace(conn, workspace_id, name, target_db_path,
                     egress_level="schema_only"):
    """Create a workspace row in the metadata store.

    Args:
        conn: the metadata sqlite3 connection.
        workspace_id: the workspace's stable id.
        name: a human-readable name.
        target_db_path: the target SQLite database path.
        egress_level: the workspace's LLM egress level (default schema_only).
    """
    conn.execute(
        "INSERT INTO workspaces (id, name, target_db_path, egress_level, "
        "created_at) VALUES (?, ?, ?, ?, ?)",
        (workspace_id, name, target_db_path, egress_level, _now()),
    )
    conn.commit()