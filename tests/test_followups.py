"""Tests for app/core/orchestrator.py follow-ups (R41)."""

from app.core.orchestrator import apply_followup
from app.models.contracts import QueryPlan


def test_followup_modifies_plan_and_states_change():
    """R41: a follow-up changes the structured plan and the change is shown."""
    plan = QueryPlan(tables=["trades"], filters=[])
    new_plan, change = apply_followup(plan, "region = Europe")
    assert len(new_plan.filters) == 1
    assert "region = Europe" in change