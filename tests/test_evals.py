"""Tests for app/accuracy/evals.py (R31)."""

import polars as pl

from app.accuracy.evals import evaluate_case
from app.db.executor import execute_query
from tests.fixtures.make_fixture import build_fixture


def test_evaluate_case_matches(tmp_path):
    """R31: a result matching the golden case passes, evaluated on results."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    df, _ = execute_query(
        db,
        "SELECT region, SUM(notional_value) AS total FROM trades GROUP BY region",
        ["trades", "regions"],
    )
    expected_rows = [["E", 600000.0], ["N", 1500000.0], ["S", 900000.0]]
    assert evaluate_case(df, ["region", "total"], expected_rows) is True


def test_evaluate_case_mismatch():
    """R31: a wrong result fails the case."""
    df = pl.DataFrame({"region": ["N"], "total": [1.0]})
    assert evaluate_case(df, ["region", "total"], [["N", 2.0]]) is False