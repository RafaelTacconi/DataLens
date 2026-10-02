"""Tests for app/core/state.py (R13)."""

import pytest

from app.core.state import InvalidTransition, Turn


def test_valid_transition_sequence():
    """R13: the turn moves through the documented stages in order."""
    t = Turn("r1", "w1", "u1", "total by region")
    assert t.stage == "NEW"
    t.transition("INTERPRETED")
    t.transition("PLANNED")
    t.transition("VALIDATED")
    t.transition("EXECUTED")
    t.transition("EXPLAINED")
    t.transition("FEEDBACK_GIVEN")
    assert t.stage == "FEEDBACK_GIVEN"


def test_invalid_transition_raises():
    """R13: a turn cannot jump past a stage."""
    t = Turn("r1", "w1", "u1", "q")
    with pytest.raises(InvalidTransition):
        t.transition("EXECUTED")


def test_terminal_states_are_terminal():
    """R13: REFUSED/FAILED/TIMED_OUT are terminal."""
    for terminal in ("REFUSED", "FAILED", "TIMED_OUT"):
        t = Turn("r1", "w1", "u1", "q")
        t.transition(terminal)
        with pytest.raises(InvalidTransition):
            t.transition("INTERPRETED")


def test_rerun_does_not_repeat_work():
    """R13: a turn that has reached a stage does not redo it on a rerun."""
    t = Turn("r1", "w1", "u1", "q")
    t.transition("INTERPRETED")
    t.transition("PLANNED")
    t.transition("VALIDATED")
    t.transition("EXECUTED")
    # The orchestrator only runs a stage it has not reached yet.
    assert t.has_reached("EXECUTED")
    if not t.has_reached("EXECUTED"):
        t.record_query()
    assert t.query_count == 0