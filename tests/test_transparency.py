"""Tests for app/ui/transparency.py (R23)."""

from app.ui.transparency import build_transparency


def test_transparency_has_all_13_items():
    """R23: a completed turn's transparency record carries all 13 items."""
    rec = build_transparency(
        question="total by region",
        understanding="aggregate trades by region",
        tables_used=["trades"],
        why_sources="the question asks about trades",
        columns_used=["region", "notional_value"],
        plan={"tables": ["trades"]},
        canonical_sql=("SELECT region, SUM(notional_value) FROM trades "
                       "GROUP BY region"),
        execution={"rows_returned": 3},
        assumptions=["2026 only"],
        resolved_period=("2026-01-01", "2026-12-31"),
        result_summary="3 rows",
        validation_status="validated",
        provenance={"model": "standin"},
    )
    assert rec.request
    assert rec.understanding
    assert rec.tables_used
    assert rec.why_sources
    assert rec.columns_used
    assert rec.plan
    assert rec.canonical_sql
    assert rec.execution
    assert rec.assumptions
    assert rec.resolved_period
    assert rec.result_summary
    assert rec.validation_status
    assert rec.provenance