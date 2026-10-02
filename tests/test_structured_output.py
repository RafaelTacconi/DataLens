"""Tests for app/llm/structured_output.py (R17)."""

import pytest
from pydantic import ValidationError

from app.llm.structured_output import parse_interpretation


def test_parse_interpretation():
    """R17: a structured interpretation parses into the typed model."""
    data = {
        "intent": "aggregate",
        "entity": "trades",
        "metrics": ["notional_value"],
        "dimensions": ["region"],
        "time_intent": {"kind": "this_year"},
    }
    interp = parse_interpretation(data)
    assert interp.intent == "aggregate"
    assert interp.entity == "trades"
    assert interp.metrics == ["notional_value"]
    assert interp.dimensions == ["region"]


def test_parse_rejects_malformed():
    """R17: malformed LLM output is rejected, not silently accepted."""
    with pytest.raises(ValidationError):
        parse_interpretation({"intent": "aggregate"})  # entity is required