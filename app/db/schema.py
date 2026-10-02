"""Schema inspection (R15).

Reads the target database's tables and columns. This module only inspects the
schema; it never executes user queries.
"""

import sqlite3


def inspect_schema(db_path):
    """Return the target database's schema as {table: {column, ...}}.

    Args:
        db_path: the resolved target database path.

    Returns:
        A mapping of table name to a set of column names.
    """
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        tables = {}
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        for (name,) in rows:
            cols = {r[1] for r in conn.execute(f'PRAGMA table_info("{name}")')}
            tables[name] = cols
        return tables
    finally:
        conn.close()