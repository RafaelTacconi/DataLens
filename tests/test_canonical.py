"""Tests for app/sql/canonical.py (R10)."""

import hashlib

from app.sql.canonical import canonicalize_sql, sql_hash


def test_canonical_is_deterministic():
    """R10: different spellings of the same query render to one canonical form."""
    a = canonicalize_sql(
        "SELECT region, SUM(notional_value) AS total FROM trades GROUP BY region")
    b = canonicalize_sql(
        "select region, sum(notional_value) as total from trades group by region")
    assert a == b


def test_canonical_is_single_string():
    """R10: canonicalisation returns one SQL string."""
    sql = canonicalize_sql("SELECT region FROM trades")
    assert isinstance(sql, str)
    assert sql.strip()


def test_hash_matches_canonical():
    """R10: the stored hash is the hash of the canonical string."""
    sql = canonicalize_sql("SELECT region FROM trades")
    assert sql_hash(sql) == hashlib.sha256(sql.encode("utf-8")).hexdigest()