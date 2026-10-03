"""Tests for app/core/cache.py (R36)."""

import sqlite3

import pytest

from app.core.cache import (
    query_cache_key,
    require_membership,
    schema_cache_key,
)
from app.core.permissions import add_member
from app.metadata.store import create_workspace, open_metadata_db
from tests.fixtures.make_fixture import build_fixture


def test_schema_key_changes_when_file_changes(tmp_path):
    """R36: a changed file is not served from a stale cache key."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    k1 = schema_cache_key(db)
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE new_table (x INTEGER)")
    conn.execute("INSERT INTO new_table VALUES (1), (2), (3)")
    conn.commit()
    conn.close()
    k2 = schema_cache_key(db)
    assert k1 != k2


def test_query_key_includes_sql(tmp_path):
    """R36: the query-result key includes the canonical SQL."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    assert query_cache_key(db, "SELECT 1") != query_cache_key(db, "SELECT 2")


def test_membership_required_before_cached_result(tmp_path):
    """R36: a cached result is only returned to a workspace member."""
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    try:
        create_workspace(conn, "w1", "Trading", "data/trades.db")
        with pytest.raises(PermissionError):
            require_membership(conn, "w1", "nobody")
        add_member(conn, "w1", "u1", "viewer")
        require_membership(conn, "w1", "u1")  # no raise
    finally:
        conn.close()