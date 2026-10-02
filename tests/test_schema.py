"""Tests for app/db/schema.py (R15)."""

from app.db.schema import inspect_schema
from tests.fixtures.make_fixture import build_fixture


def test_inspect_schema_finds_tables_and_columns(tmp_path):
    """R15: the target database's tables and columns are read."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    schema = inspect_schema(db)
    assert "trades" in schema
    assert "regions" in schema
    assert {"trade_id", "region", "instrument", "notional_value",
            "trade_date"} <= schema["trades"]
    assert {"region_code", "region_name"} <= schema["regions"]