"""Tests for app/sql/plan_checker.py (R19)."""

from app.models.contracts import Interpretation, QueryPlan
from app.sql.plan_checker import build_plan, plan_to_plain


def test_build_plan_from_interpretation():
    """R19: a structured plan is built from the interpretation."""
    interp = Interpretation(
        intent="aggregate",
        entity="trades",
        metrics=["notional_value"],
        dimensions=["region"],
    )
    plan = build_plan(interp)
    assert plan.tables == ["trades"]
    assert plan.metrics == ["SUM(notional_value)"]
    assert plan.grouping == ["region"]


def test_plan_to_plain():
    """R19: the plan is shown to the user in plain language."""
    plan = QueryPlan(
        tables=["trades"],
        metrics=["SUM(notional_value)"],
        grouping=["region"],
    )
    text = plan_to_plain(plan)
    assert "trades" in text
    assert "region" in text