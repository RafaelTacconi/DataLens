"""Security test suite (R39).

Each control is tested by attempting to bypass it (SDD §38, §42, Guide §14).
Security must hold even when the SQL validator is bypassed, so the authorizer
is tested independently.
"""

import sqlite3

import pytest

from app.db.authorizer import make_authorizer
from app.db.connection import open_readonly_connection
from app.db.path_policy import PathPolicyError, validate_target_path
from app.sql.validator import ValidationError, validate_sql
from tests.fixtures.make_fixture import build_fixture

SCHEMA = {
    "trades": {"trade_id", "region", "instrument", "notional_value",
               "trade_date"},
    "regions": {"region_code", "region_name"},
}
ALLOWED = ["trades", "regions"]


def test_validator_rejects_insert():
    with pytest.raises(ValidationError):
        validate_sql(
            "INSERT INTO trades VALUES (1, 'N', 'GOLD', 1.0, '2026-01-01')",
            SCHEMA, ALLOWED)


def test_authorizer_rejects_insert(tmp_path):
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = sqlite3.connect(db)
    conn.set_authorizer(make_authorizer(ALLOWED))
    try:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute(
                "INSERT INTO trades VALUES (1, 'N', 'GOLD', 1.0, '2026-01-01')")
    finally:
        conn.close()


def test_validator_rejects_attach():
    with pytest.raises(ValidationError):
        validate_sql("ATTACH DATABASE 'x' AS other", SCHEMA, ALLOWED)


def test_authorizer_rejects_attach(tmp_path):
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    other = build_fixture(str(tmp_path / "other.db"), "b")
    conn = sqlite3.connect(db)
    conn.set_authorizer(make_authorizer(ALLOWED))
    try:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute(f"ATTACH DATABASE '{other}' AS other")
    finally:
        conn.close()


def test_validator_rejects_hidden_table():
    with pytest.raises(ValidationError):
        validate_sql("SELECT * FROM regions", SCHEMA, ["trades"])


def test_authorizer_rejects_hidden_table(tmp_path):
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = sqlite3.connect(db)
    conn.set_authorizer(make_authorizer(["trades"]))
    try:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute("SELECT * FROM regions")
    finally:
        conn.close()


def test_validator_rejects_multiple_statements():
    with pytest.raises(ValidationError):
        validate_sql("SELECT * FROM trades; DROP TABLE trades", SCHEMA,
                     ALLOWED)


def test_readonly_connection_rejects_write(tmp_path):
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    conn = open_readonly_connection(db, make_authorizer(ALLOWED))
    try:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute(
                "INSERT INTO trades VALUES (1, 'N', 'GOLD', 1.0, '2026-01-01')")
    finally:
        conn.close()


def test_path_policy_rejects_metadata_db(tmp_path):
    meta = tmp_path / "metadata.db"
    sqlite3.connect(str(meta)).close()
    with pytest.raises(PathPolicyError):
        validate_target_path(str(meta), str(meta))