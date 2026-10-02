"""Tests for app/ui/chat.py result display (R21)."""

import polars as pl

from app.db.executor import execute_query
from app.ui.chat import display_rows
from tests.fixtures.make_fixture import build_fixture


def test_display_matches_dataframe(tmp_path):
    """R21: the displayed rows are exactly the DataFrame's rows."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    df, _ = execute_query(
        db,
        "SELECT region, SUM(notional_value) AS total FROM trades GROUP BY region",
        ["trades", "regions"],
    )
    rows, truncated = display_rows(df)
    assert rows == df.to_dicts()
    assert truncated is False


def test_display_caps_at_30():
    """R21: at most 30 rows are shown in chat, and truncation is stated."""
    df = pl.DataFrame({"x": list(range(40))})
    rows, truncated = display_rows(df)
    assert len(rows) == 30
    assert truncated is True