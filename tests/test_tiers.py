"""Tests for app/core/tiers.py (R33)."""

from app.config.settings import load_settings
from app.core.tiers import classify_tier, requires_confirmation
from app.models.contracts import QueryPlan


def test_classify_simple():
    settings = load_settings({})
    plan = QueryPlan(tables=["trades"], joins=[], analysis_steps=[])
    assert classify_tier(plan, settings) == "simple"


def test_classify_standard():
    settings = load_settings({})
    plan = QueryPlan(tables=["trades"], joins=[{}, {}], analysis_steps=[])
    assert classify_tier(plan, settings) == "standard"


def test_classify_extended():
    settings = load_settings({})
    plan = QueryPlan(tables=["trades"], joins=[{}, {}, {}, {}],
                     analysis_steps=[])
    assert classify_tier(plan, settings) == "extended"


def test_extended_requires_confirmation():
    """R33: an Extended query shows the plan and asks for confirmation."""
    assert requires_confirmation("extended") is True
    assert requires_confirmation("simple") is False
    assert requires_confirmation("standard") is False