"""Tests for app/metadata/audit.py (R3)."""

import sqlite3

import pytest

from app.metadata.audit import append_audit
from app.metadata.store import open_metadata_db


def test_append_audit_writes_row(tmp_path):
    """R12: an audited action leaves an audit row."""
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    try:
        append_audit(
            conn,
            event_type="workspace_created",
            workspace_id="w1",
            actor="u1",
            identity_source="os",
        )
        rows = conn.execute("SELECT * FROM audit_events").fetchall()
        assert len(rows) == 1
        assert rows[0]["event_type"] == "workspace_created"
        assert rows[0]["workspace_id"] == "w1"
    finally:
        conn.close()


def test_audit_rows_cannot_be_updated(tmp_path):
    """R3: application code cannot update an audit row."""
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    try:
        append_audit(conn, event_type="query_run", actor="u1")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE audit_events SET event_type='tampered'")
    finally:
        conn.close()


def test_audit_rows_cannot_be_deleted(tmp_path):
    """R3: application code cannot delete an audit row."""
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    try:
        append_audit(conn, event_type="query_run", actor="u1")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM audit_events")
    finally:
        conn.close()