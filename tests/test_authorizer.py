"""Tests for app/db/authorizer.py (R8).

The authorizer is tested independently by sending deliberately unsafe SQL
directly to a connection (Guide §7): security must hold even if the SQL
validator is bypassed.
"""

import sqlite3

import pytest

from app.db.authorizer import make_authorizer
from tests.fixtures.make_fixture import build_fixture


def _conn(db, allowed):
    """A normal (writable) connection with only the authorizer installed."""
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    conn.set_authorizer(make_authorizer(allowed))
    return conn


def test_authorizer_rejects_insert(tmp_path):
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = _conn(db, ["trades", "regions"])
    try:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute(
                "INSERT INTO trades VALUES (99, 'N', 'GOLD', 1.0, '2026-01-01')")
    finally:
        conn.close()


def test_authorizer_rejects_update(tmp_path):
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = _conn(db, ["trades", "regions"])
    try:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute("UPDATE trades SET notional_value = 0")
    finally:
        conn.close()


def test_authorizer_rejects_delete(tmp_path):
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = _conn(db, ["trades", "regions"])
    try:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute("DELETE FROM trades")
    finally:
        conn.close()


def test_authorizer_rejects_create(tmp_path):
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = _conn(db, ["trades", "regions"])
    try:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute("CREATE TABLE evil (x)")
    finally:
        conn.close()


def test_authorizer_rejects_drop(tmp_path):
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = _conn(db, ["trades", "regions"])
    try:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute("DROP TABLE trades")
    finally:
        conn.close()


def test_authorizer_rejects_alter(tmp_path):
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = _conn(db, ["trades", "regions"])
    try:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute("ALTER TABLE trades ADD COLUMN y")
    finally:
        conn.close()


def test_authorizer_rejects_attach(tmp_path):
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    other = build_fixture(str(tmp_path / "other.db"), "b")
    conn = _conn(db, ["trades", "regions"])
    try:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute(f"ATTACH DATABASE '{other}' AS other")
    finally:
        conn.close()


def test_authorizer_rejects_pragma(tmp_path):
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = _conn(db, ["trades", "regions"])
    try:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute("PRAGMA journal_mode=DELETE")
    finally:
        conn.close()


def test_authorizer_blocks_hidden_table(tmp_path):
    """R8: reading a table not on the allow-list is denied."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = _conn(db, ["trades"])  # regions is NOT allowed
    try:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute("SELECT * FROM regions")
    finally:
        conn.close()


def test_authorizer_allows_allowed_table(tmp_path):
    """R8: reading an allowed table succeeds."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = _conn(db, ["trades", "regions"])
    try:
        rows = conn.execute("SELECT COUNT(*) AS n FROM trades").fetchone()
        assert rows["n"] == 6
    finally:
        conn.close()