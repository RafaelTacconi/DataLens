"""Tests for app/core/orchestrator.py error handling (R38)."""

import pytest

from app.core.orchestrator import (
    generate_sql_with_retries,
    timeout_message,
)
from app.models.contracts import QueryPlan
from app.sql.validator import ValidationError

SCHEMA = {
    "trades": {"trade_id", "region", "instrument", "notional_value",
               "trade_date"},
}
PLAN = QueryPlan(tables=["trades"])


class AlwaysBad:
    def generate_sql(self, request):
        return "INSERT INTO trades VALUES (1, 'N', 'GOLD', 1.0, '2026-01-01')"


class Flaky:
    def __init__(self):
        self.calls = 0

    def generate_sql(self, request):
        self.calls += 1
        if self.calls == 1:
            return "INSERT INTO trades VALUES (1, 'N', 'GOLD', 1.0, '2026-01-01')"
        return "SELECT region FROM trades"


def test_retry_limit_reached():
    """R38: after the attempt limit the turn fails."""
    with pytest.raises(ValidationError):
        generate_sql_with_retries(AlwaysBad(), PLAN, SCHEMA, ["trades"],
                                  max_attempts=3)


def test_retry_succeeds_within_limit():
    """R38: a draft that becomes valid within the limit succeeds."""
    provider = Flaky()
    sql = generate_sql_with_retries(provider, PLAN, SCHEMA, ["trades"],
                                    max_attempts=3)
    assert "SELECT" in sql.upper()


def test_timeout_is_not_auto_retried():
    """R38: a timeout tells the user to narrow the request, not retry."""
    assert "narrow" in timeout_message()