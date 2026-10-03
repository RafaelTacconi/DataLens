"""Safe data profiles (R25).

Profiles a table's columns for row and distinct counts. Sensitive columns are
never profiled (SDD §13, §44 Phase 3).
"""

import sqlite3


def profile_table(db_path, table, sensitive_columns=()):
    """Return a safe profile of a table, excluding sensitive columns.

    Args:
        db_path: the resolved target database path.
        table: the table to profile.
        sensitive_columns: columns that must never be profiled.

    Returns:
        A mapping {column: {"count": n, "distinct": d}} for safe columns.
    """
    sensitive = set(sensitive_columns)
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')]
        profile = {}
        for col in cols:
            if col in sensitive:
                continue
            row = conn.execute(
                f'SELECT COUNT(*) AS n, COUNT(DISTINCT "{col}") AS d '
                f'FROM "{table}"'
            ).fetchone()
            profile[col] = {"count": row[0], "distinct": row[1]}
        return profile
    finally:
        conn.close()