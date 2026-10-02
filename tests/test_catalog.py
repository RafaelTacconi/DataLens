"""Tests for app/metadata/catalog.py (R16)."""

from app.metadata.catalog import (
    add_business_term,
    add_catalog_entry,
    get_business_context,
    get_business_terms,
    get_exposed_tables,
    set_business_context,
)
from app.metadata.store import create_workspace, open_metadata_db


def _workspace(tmp_path):
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    create_workspace(conn, "w1", "Trading", "data/trades.db")
    return conn


def test_store_and_retrieve_context(tmp_path):
    """R16: business context is stored and retrieved per workspace."""
    conn = _workspace(tmp_path)
    try:
        set_business_context(conn, "w1",
                             "Trading volume = SUM(notional_value)")
        assert get_business_context(conn, "w1") == \
            "Trading volume = SUM(notional_value)"
    finally:
        conn.close()


def test_not_exposed_object_hidden(tmp_path):
    """R16: a not-exposed table is excluded from the exposed allow-list."""
    conn = _workspace(tmp_path)
    try:
        add_catalog_entry(conn, "w1", "table", "trades", "Trades", exposed=True)
        add_catalog_entry(conn, "w1", "table", "secret", "Secret",
                          exposed=False)
        exposed = get_exposed_tables(conn, "w1")
        assert "trades" in exposed
        assert "secret" not in exposed
    finally:
        conn.close()


def test_business_terms_stored(tmp_path):
    """R16: business terms are stored and retrieved."""
    conn = _workspace(tmp_path)
    try:
        add_business_term(conn, "w1", "revenue", "gross revenue")
        terms = get_business_terms(conn, "w1")
        assert terms == {"revenue": "gross revenue"}
    finally:
        conn.close()