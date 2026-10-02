"""Tests for app/metadata/audit.py query-run logging (R12)."""

from app.metadata.audit import log_query_run
from app.metadata.store import open_metadata_db


def test_log_query_run_leaves_row(tmp_path):
    """R12: a query run is an audited action that leaves a row."""
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    try:
        log_query_run(conn, "w1", "u1", "total by region",
                      "SELECT region, SUM(notional_value) FROM trades")
        rows = conn.execute(
            "SELECT * FROM audit_events WHERE event_type='query_run'"
        ).fetchall()
        assert len(rows) == 1
        assert rows[0]["workspace_id"] == "w1"
        assert rows[0]["actor"] == "u1"
    finally:
        conn.close()