"""Tests for app/sql/validator.py (R9)."""

import pytest

from app.sql.validator import ValidationError, validate_sql

SCHEMA = {
    "trades": {"trade_id", "region", "instrument", "notional_value",
               "trade_date"},
    "regions": {"region_code", "region_name"},
}
ALLOWED = ["trades", "regions"]


def test_rejects_insert():
    with pytest.raises(ValidationError):
        validate_sql(
            "INSERT INTO trades VALUES (1, 'N', 'GOLD', 1.0, '2026-01-01')",
            SCHEMA, ALLOWED)


def test_rejects_update():
    with pytest.raises(ValidationError):
        validate_sql("UPDATE trades SET notional_value = 0", SCHEMA, ALLOWED)


def test_rejects_delete():
    with pytest.raises(ValidationError):
        validate_sql("DELETE FROM trades", SCHEMA, ALLOWED)


def test_rejects_create():
    with pytest.raises(ValidationError):
        validate_sql("CREATE TABLE evil (x)", SCHEMA, ALLOWED)


def test_rejects_drop():
    with pytest.raises(ValidationError):
        validate_sql("DROP TABLE trades", SCHEMA, ALLOWED)


def test_rejects_attach():
    with pytest.raises(ValidationError):
        validate_sql("ATTACH DATABASE 'x' AS other", SCHEMA, ALLOWED)


def test_rejects_pragma():
    with pytest.raises(ValidationError):
        validate_sql("PRAGMA journal_mode=DELETE", SCHEMA, ALLOWED)


def test_rejects_multiple_statements():
    with pytest.raises(ValidationError):
        validate_sql("SELECT * FROM trades; DROP TABLE trades", SCHEMA, ALLOWED)


def test_comment_does_not_hide_second_statement():
    """A comment cannot hide a real second statement from the parser."""
    with pytest.raises(ValidationError):
        validate_sql("SELECT * FROM trades; DROP TABLE trades -- hidden",
                     SCHEMA, ALLOWED)


def test_rejects_unknown_table():
    with pytest.raises(ValidationError):
        validate_sql("SELECT * FROM nope", SCHEMA, ALLOWED)


def test_rejects_hidden_table():
    with pytest.raises(ValidationError):
        validate_sql("SELECT * FROM regions", SCHEMA, ["trades"])


def test_rejects_unknown_column():
    with pytest.raises(ValidationError):
        validate_sql("SELECT nope FROM trades", SCHEMA, ALLOWED)


def test_accepts_valid_query():
    stmt = validate_sql(
        "SELECT region, SUM(notional_value) AS total FROM trades "
        "GROUP BY region",
        SCHEMA, ALLOWED)
    assert stmt is not None