"""Target database path policy (R6).

A target path must be a real file, a SQLite database, and not the metadata
database or its -wal/-shm side files. The approved-data-root check was dropped
by builder decision (contract Part 5); the checks that remain are the ones
here. This module only validates paths; it never executes queries (Guide §4).
"""

import pathlib

_SQLITE_HEADER = b"SQLite format 3\x00"


class PathPolicyError(Exception):
    """A target path was rejected."""


def _is_sqlite(path):
    """True if the file begins with the SQLite header."""
    with open(path, "rb") as fh:
        return fh.read(16) == _SQLITE_HEADER


def validate_target_path(path, metadata_db_path):
    """Validate a target SQLite path and return its resolved form.

    Args:
        path: the user-supplied target path.
        metadata_db_path: the metadata database path, which must never be a
            target.

    Returns:
        The resolved absolute path as a string.

    Raises:
        PathPolicyError: if the path is not a real, non-metadata SQLite file.
    """
    p = pathlib.Path(path)
    if not p.exists():
        raise PathPolicyError("path does not exist")
    if p.is_dir():
        raise PathPolicyError("path is a directory, not a file")
    resolved = p.resolve()
    meta = pathlib.Path(metadata_db_path).resolve()
    if resolved == meta:
        raise PathPolicyError("path is the metadata database")
    if resolved in (meta.with_name(meta.name + "-wal"),
                    meta.with_name(meta.name + "-shm")):
        raise PathPolicyError("path is a metadata database side file")
    if not _is_sqlite(resolved):
        raise PathPolicyError("path is not a SQLite database")
    return str(resolved)