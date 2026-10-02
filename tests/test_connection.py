"""Tests for app/db/connection.py (R7)."""

import sqlite3

import pytest

from app.db.connection import open_readonly_connection
from tests.fixtures.make_fixture import build_fixture


def test_connection_is_read_only(tmp_path):
    """R7: a write through the guarded connection is refused."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = open_readonly_connection(db)
    try:
        with pytest.raises(sqlite3.OperationalError):
            conn.execute(
                "INSERT INTO trades VALUES (99, 'N', 'GOLD', 1.0, '2026-01-01')")
    finally:
        conn.close()


def test_query_only_is_set(tmp_path):
    """R7: PRAGMA query_only is on."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = open_readonly_connection(db)
    try:
        assert conn.execute("PRAGMA query_only").fetchone()[0] == 1
    finally:
        conn.close()


def test_connections_are_not_shared(tmp_path):
    """R7: each call returns a fresh connection, never a shared one."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    c1 = open_readonly_connection(db)
    c2 = open_readonly_connection(db)
    try:
        assert c1 is not c2
    finally:
        c1.close()
        c2.close()