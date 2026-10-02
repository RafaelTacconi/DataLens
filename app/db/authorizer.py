"""SQLite authorizer (R8).

The second safety barrier: it rejects prohibited SQLite actions even if the
SQL validator is bypassed (Guide §7). It also enforces the workspace's
exposed-table allow-list, so a table not exposed is unreadable here.
"""

import sqlite3

# Every action that is not a plain read of an allowed table.
PROHIBITED = {
    sqlite3.SQLITE_INSERT,
    sqlite3.SQLITE_UPDATE,
    sqlite3.SQLITE_DELETE,
    sqlite3.SQLITE_CREATE_TABLE,
    sqlite3.SQLITE_CREATE_INDEX,
    sqlite3.SQLITE_CREATE_VIEW,
    sqlite3.SQLITE_CREATE_TRIGGER,
    sqlite3.SQLITE_CREATE_TEMP_TABLE,
    sqlite3.SQLITE_CREATE_TEMP_INDEX,
    sqlite3.SQLITE_CREATE_TEMP_VIEW,
    sqlite3.SQLITE_CREATE_TEMP_TRIGGER,
    sqlite3.SQLITE_DROP_TABLE,
    sqlite3.SQLITE_DROP_INDEX,
    sqlite3.SQLITE_DROP_VIEW,
    sqlite3.SQLITE_DROP_TRIGGER,
    sqlite3.SQLITE_DROP_TEMP_TABLE,
    sqlite3.SQLITE_DROP_TEMP_INDEX,
    sqlite3.SQLITE_DROP_TEMP_VIEW,
    sqlite3.SQLITE_DROP_TEMP_TRIGGER,
    sqlite3.SQLITE_ALTER_TABLE,
    sqlite3.SQLITE_ATTACH,
    sqlite3.SQLITE_DETACH,
    sqlite3.SQLITE_PRAGMA,
    sqlite3.SQLITE_TRANSACTION,
    sqlite3.SQLITE_SAVEPOINT,
    sqlite3.SQLITE_REINDEX,
    sqlite3.SQLITE_ANALYZE,
}


def make_authorizer(allowed_tables):
    """Build an authorizer callback that allows only reads of allowed tables.

    Args:
        allowed_tables: an iterable of table names that may be read.

    Returns:
        A callback for sqlite3.Connection.set_authorizer.
    """
    allowed = set(allowed_tables)

    def authorizer(action, arg1, arg2, dbname, source):
        if action in PROHIBITED:
            return sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_READ:
            table = arg1
            if table not in allowed:
                return sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_FUNCTION:
            # Block extension loading, but allow built-in functions (COUNT,
            # SUM, ...) that legitimate read queries need.
            if arg1 == "load_extension":
                return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    return authorizer