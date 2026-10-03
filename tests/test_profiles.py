"""Tests for app/db/profiles.py (R25)."""

from app.db.profiles import profile_table
from tests.fixtures.make_fixture import build_fixture


def test_profile_excludes_sensitive_columns(tmp_path):
    """R25: sensitive columns are never profiled."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    profile = profile_table(db, "trades", sensitive_columns={"instrument"})
    assert "instrument" not in profile
    assert "region" in profile
    assert profile["region"]["count"] == 6


def test_profile_counts_distinct(tmp_path):
    """R25: a profile reports row and distinct counts."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    profile = profile_table(db, "trades")
    assert profile["region"]["distinct"] == 3