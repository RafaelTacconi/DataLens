"""Tests for app/models/contracts.py (R43)."""

import pytest
from pydantic import ValidationError

from app.models.contracts import (
    Ambiguity,
    AuditEvent,
    EvaluationCase,
    ExecutionMetrics,
    FactsPayload,
    Interpretation,
    Membership,
    QueryPlan,
    QueryStep,
    TransparencyRecord,
    Turn,
    VerifiedQuery,
    Workspace,
)


def test_models_construct():
    """R43: every typed contract constructs from valid input."""
    Interpretation(intent="aggregate", entity="trades")
    Ambiguity(question="revenue?", options=["gross", "net"])
    QueryPlan(tables=["trades"])
    QueryStep(kind="query")
    ExecutionMetrics(rows_returned=3)
    FactsPayload(facts=[{"region": "N", "total": 1500000}])
    TransparencyRecord(tables_used=["trades"], canonical_sql="SELECT 1")
    Turn(run_id="r1", workspace_id="w1", user_id="u1", question="q")
    AuditEvent(event_type="query_run")
    Workspace(id="w1", name="Trading", target_db_path="data/trades.db")
    Membership(workspace_id="w1", user_id="u1", role="owner")
    VerifiedQuery(workspace_id="w1", question="q", canonical_sql="SELECT 1")
    EvaluationCase(workspace_id="w1", question="q")


def test_models_reject_malformed():
    """R43: malformed input is rejected, not silently accepted."""
    with pytest.raises(ValidationError):
        Interpretation()  # intent and entity are required
    with pytest.raises(ValidationError):
        Turn()  # run_id, workspace_id, user_id, question are required
    with pytest.raises(ValidationError):
        Workspace()  # id, name, target_db_path are required