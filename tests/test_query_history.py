"""Tests for query history storage (R29)."""

from app.metadata.store import (
    create_workspace,
    get_query_history,
    open_metadata_db,
    store_query_run,
)


def test_query_run_stored_and_viewable(tmp_path):
    """R29: a completed run is stored and viewable in history."""
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    try:
        create_workspace(conn, "w1", "Trading", "data/trades.db")
        store_query_run(conn, "w1", "u1", "total by region",
                        "SELECT region, SUM(notional_value) FROM trades",
                        {"rows": 3})
        history = get_query_history(conn, "w1")
        assert len(history) == 1
        assert history[0]["question"] == "total by region"
        assert history[0]["canonical_sql"].startswith("SELECT")
    finally:
        conn.close()