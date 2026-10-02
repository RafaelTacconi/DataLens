"""Tests for app/metadata/store.py (R2)."""

from app.metadata.store import open_metadata_db

EXPECTED_TABLES = {
    "workspaces",
    "memberships",
    "context_versions",
    "catalog",
    "business_terms",
    "profiles",
    "verified_queries",
    "evaluation_cases",
    "query_runs",
    "audit_events",
}


def test_metadata_store_has_all_tables(tmp_path):
    """R2: opening the metadata DB creates every required table."""
    db = tmp_path / "metadata.db"
    conn = open_metadata_db(str(db))
    try:
        tables = {
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert EXPECTED_TABLES <= tables
    finally:
        conn.close()


def test_metadata_store_is_wal(tmp_path):
    """R2: the metadata database runs in WAL mode."""
    db = tmp_path / "metadata.db"
    conn = open_metadata_db(str(db))
    try:
        journal = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert journal.lower() == "wal"
    finally:
        conn.close()