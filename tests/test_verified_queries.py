"""Tests for app/accuracy/verified_queries.py (R30)."""

from app.accuracy.verified_queries import (
    get_verified_queries,
    mark_needs_recheck,
    promote_verified_query,
)
from app.metadata.store import create_workspace, open_metadata_db


def test_promote_and_needs_recheck(tmp_path):
    """R30: a schema/context change marks a verified query needs_recheck."""
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    try:
        create_workspace(conn, "w1", "Trading", "data/trades.db")
        promote_verified_query(conn, "w1", "total by region",
                               "SELECT region, SUM(notional_value) FROM trades",
                               context_version=1)
        assert len(get_verified_queries(conn, "w1")) == 1

        mark_needs_recheck(conn, "w1", context_version=2)
        assert len(get_verified_queries(conn, "w1")) == 0
        assert len(get_verified_queries(conn, "w1",
                                        status="needs_recheck")) == 1
    finally:
        conn.close()