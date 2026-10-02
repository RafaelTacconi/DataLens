"""Tests for database update behavior (R37)."""

import sqlite3

from app.core.cache import refresh_schema_if_stale
from tests.fixtures.make_fixture import build_fixture


def test_refresh_after_file_change(tmp_path):
    """R37: a changed file is detected and the schema refreshed, no restart."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    schema, ident = refresh_schema_if_stale(db, None, None)
    assert "trades" in schema

    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE new_table (x)")
    conn.commit()
    conn.close()

    schema2, ident2 = refresh_schema_if_stale(db, ident, schema)
    assert "new_table" in schema2
    assert ident2 != ident


def test_no_refresh_when_unchanged(tmp_path):
    """R37: an unchanged file is not re-read."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    schema, ident = refresh_schema_if_stale(db, None, None)
    schema2, ident2 = refresh_schema_if_stale(db, ident, schema)
    assert ident2 == ident
    assert schema2 == schema