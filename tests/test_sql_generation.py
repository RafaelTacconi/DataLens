"""Tests for SQL generation (R20)."""

import pytest

from app.core.orchestrator import generate_and_validate_sql
from app.db.schema import inspect_schema
from app.models.contracts import QueryPlan
from app.sql.validator import ValidationError
from tests.fixtures.make_fixture import build_fixture

SCHEMA = {
    "trades": {"trade_id", "region", "instrument", "notional_value",
               "trade_date"},
    "regions": {"region_code", "region_name"},
}
PLAN = QueryPlan(tables=["trades"], metrics=["SUM(notional_value)"],
                 grouping=["region"])


class GoodLLM:
    """Returns a valid SELECT draft."""

    def generate_sql(self, request):
        return ("SELECT region, SUM(notional_value) AS total FROM trades "
                "GROUP BY region")


class BadLLM:
    """Returns an unsafe draft that must be rejected."""

    def generate_sql(self, request):
        return "INSERT INTO trades VALUES (1, 'N', 'GOLD', 1.0, '2026-01-01')"


def test_draft_passes_validation_before_execution():
    """R20: a valid draft is validated and canonicalised, never run directly."""
    sql = generate_and_validate_sql(GoodLLM(), PLAN, SCHEMA, ["trades"])
    assert "SELECT" in sql.upper()


def test_invalid_draft_is_rejected():
    """R20: an unsafe draft is rejected before it can be executed."""
    with pytest.raises(ValidationError):
        generate_and_validate_sql(BadLLM(), PLAN, SCHEMA, ["trades"])