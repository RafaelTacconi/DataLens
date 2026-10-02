"""Guarded read-only SQLite connections (R7).

Each target query gets a fresh connection, opened read-only with query_only
on and an authorizer installed. Connections are never shared between sessions
or threads, and never cached with st.cache_resource (SDD §22, Guide §3.5).
"""

import sqlite3


def open_readonly_connection(path, authorizer=None):
    """Open a guarded read-only connection to a target SQLite database.

    Args:
        path: the resolved target database path.
        authorizer: an optional sqlite3 authorizer callback (see
            app/db/authorizer.py).

    Returns:
        A fresh sqlite3.Connection opened in read-only mode with query_only on.
    """
    uri = f"file:{path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    if authorizer is not None:
        conn.set_authorizer(authorizer)
    return conn