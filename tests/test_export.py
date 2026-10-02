"""Tests for app/utils/export.py (R22)."""

import io

import polars as pl

from app.db.executor import execute_query
from app.utils.export import export_csv
from tests.fixtures.make_fixture import build_fixture


def test_export_matches_dataframe(tmp_path):
    """R22: the CSV is generated from the actual DataFrame."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    df, _ = execute_query(
        db,
        "SELECT region, SUM(notional_value) AS total FROM trades GROUP BY region",
        ["trades", "regions"],
    )
    csv_text, truncated = export_csv(df)
    parsed = pl.read_csv(io.StringIO(csv_text))
    assert parsed.to_dicts() == df.to_dicts()
    assert truncated is False


def test_export_caps_at_limit():
    """R22: the export is capped and truncation is reported."""
    df = pl.DataFrame({"x": list(range(15000))})
    csv_text, truncated = export_csv(df, export_cap=10000)
    parsed = pl.read_csv(io.StringIO(csv_text))
    assert parsed.height == 10000
    assert truncated is True