"""Tests for app/db/path_policy.py (R6)."""

import sqlite3

import pytest

from app.db.path_policy import PathPolicyError, validate_target_path


def test_accepts_real_sqlite(tmp_path):
    """R6: a real SQLite file is accepted and resolved."""
    db = tmp_path / "trades.db"
    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE t (x)")
    conn.close()
    assert validate_target_path(str(db), str(tmp_path / "metadata.db")) == \
        str(db.resolve())


def test_rejects_nonexistent(tmp_path):
    """R6: a path that does not exist is rejected."""
    with pytest.raises(PathPolicyError):
        validate_target_path(str(tmp_path / "missing.db"),
                             str(tmp_path / "metadata.db"))


def test_rejects_directory(tmp_path):
    """R6: a directory is rejected."""
    with pytest.raises(PathPolicyError):
        validate_target_path(str(tmp_path), str(tmp_path / "metadata.db"))


def test_rejects_non_sqlite(tmp_path):
    """R6: a file that is not a SQLite database is rejected."""
    f = tmp_path / "notes.txt"
    f.write_text("hello", encoding="utf-8")
    with pytest.raises(PathPolicyError):
        validate_target_path(str(f), str(tmp_path / "metadata.db"))


def test_rejects_metadata_db(tmp_path):
    """R6: the metadata database itself is rejected as a target."""
    meta = tmp_path / "metadata.db"
    sqlite3.connect(str(meta)).close()
    with pytest.raises(PathPolicyError):
        validate_target_path(str(meta), str(meta))


def test_rejects_metadata_wal(tmp_path):
    """R6: a metadata -wal side file is rejected as a target."""
    meta = tmp_path / "metadata.db"
    sqlite3.connect(str(meta)).close()
    wal = tmp_path / "metadata.db-wal"
    wal.write_bytes(b"x")
    with pytest.raises(PathPolicyError):
        validate_target_path(str(wal), str(meta))