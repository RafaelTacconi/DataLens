"""Tests for app/core/orchestrator.py analysis mode (R32)."""

import polars as pl

from app.core.orchestrator import run_analysis
from app.models.contracts import QueryPlan, QueryStep


def test_analysis_outputs_name_source():
    """R32: every analysis output identifies which step produced it."""
    plan = QueryPlan(analysis_steps=[
        QueryStep(kind="query", detail="total by region"),
        QueryStep(kind="transform", detail="top 2"),
    ])

    def executor(step):
        return pl.DataFrame({"region": ["N", "S"],
                             "total": [1500000.0, 900000.0]})

    outputs = run_analysis(plan, executor)
    assert len(outputs) == 2
    assert outputs[0]["source"] == "query"
    assert outputs[1]["source"] == "transform"
    assert outputs[0]["rows"][0]["region"] == "N"