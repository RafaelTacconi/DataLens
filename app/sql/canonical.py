"""Canonical SQL (R10).

After validation, the SQL is rendered to one canonical string, its hash is
stored, and exactly that string is executed. Displayed SQL equals executed
SQL (SDD §21, Guide §6).
"""

import hashlib

import sqlglot


def canonicalize_sql(sql):
    """Render one canonical SQL string for the SQLite dialect.

    Args:
        sql: the validated SQL draft.

    Returns:
        A single canonical SQL string.
    """
    stmt = sqlglot.parse_one(sql, read="sqlite")
    return stmt.sql(dialect="sqlite")


def sql_hash(sql):
    """The SHA-256 hash of a canonical SQL string.

    Args:
        sql: the canonical SQL string.

    Returns:
        The hex digest of the string.
    """
    return hashlib.sha256(sql.encode("utf-8")).hexdigest()