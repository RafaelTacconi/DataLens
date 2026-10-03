"""Tests for app/analysis/facts.py (R26)."""

from app.analysis.facts import build_facts
from app.db.executor import execute_query
from tests.fixtures.make_fixture import build_fixture


def test_build_facts_from_result(tmp_path):
    """R26: the facts payload is built from the actual result."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    df, _ = execute_query(
        db,
        "SELECT region, SUM(notional_value) AS total FROM trades GROUP BY region",
        ["trades", "regions"],
    )
    payload = build_facts(df)
    assert len(payload.facts) == 3
    by_region = {f["region"]: f["total"] for f in payload.facts}
    assert by_region["N"] == 1500000.0