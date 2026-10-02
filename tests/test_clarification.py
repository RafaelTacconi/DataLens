"""Tests for app/core/orchestrator.py clarification (R18)."""

from app.core.orchestrator import needs_clarification
from app.models.contracts import Interpretation


def test_ambiguous_question_yields_clarification():
    """R18: a material ambiguity asks the user, not a guess."""
    interp = Interpretation(
        intent="aggregate",
        entity="trades",
        ambiguities=["revenue: gross or net?"],
    )
    assert needs_clarification(interp) is True


def test_unambiguous_question_needs_no_clarification():
    """R18: a clear question proceeds without asking."""
    interp = Interpretation(intent="aggregate", entity="trades")
    assert needs_clarification(interp) is False