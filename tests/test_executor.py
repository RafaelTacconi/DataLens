"""Tests for app/db/executor.py (R11)."""

import polars as pl

from app.db.executor import execute_query
from tests.fixtures.make_fixture import build_fixture


def test_execute_returns_dataframe(tmp_path):
    """R11: canonical SQL returns a Polars DataFrame and metrics."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    df, metrics = execute_query(
        db,
        "SELECT region, SUM(notional_value) AS total FROM trades GROUP BY region",
        ["trades", "regions"],
    )
    assert isinstance(df, pl.DataFrame)
    assert df.height == 3
    assert metrics["rows_returned"] == 3
    assert metrics["truncated"] is False


def test_execute_enforces_fetch_cap(tmp_path):
    """R11: the fetch cap is enforced and truncation is reported."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    df, metrics = execute_query(
        db, "SELECT * FROM trades", ["trades", "regions"], row_cap=2)
    assert df.height == 2
    assert metrics["truncated"] is True