"""Tests for app/ui/history.py (R29)."""

from app.metadata.store import (
    create_workspace,
    open_metadata_db,
    store_query_run,
)
from app.ui.history import history_view


def test_history_view_shows_stored_runs(tmp_path):
    """R29: the history view shows the stored query runs."""
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    try:
        create_workspace(conn, "w1", "Trading", "data/trades.db")
        store_query_run(conn, "w1", "u1", "total by region",
                        "SELECT region, SUM(notional_value) FROM trades")
        runs = history_view(conn, "w1")
        assert len(runs) == 1
        assert runs[0]["question"] == "total by region"
    finally:
        conn.close()