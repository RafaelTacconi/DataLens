"""Tests for app/analysis/verifier.py (R27)."""

from app.analysis.verifier import verify_numbers
from app.models.contracts import FactsPayload

FACTS = FactsPayload(facts=[{"region": "N", "total": 1500000.0}])


def test_correct_explanation_passes():
    """R27: a number that matches the facts passes verification."""
    assert verify_numbers("North total is 1500000", FACTS) is True


def test_invented_number_fails():
    """R27: a number not in the facts fails verification."""
    assert verify_numbers("North total is 999999", FACTS) is False