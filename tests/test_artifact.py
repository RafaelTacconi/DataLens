"""The artifact test - strict rule 6 (house rule 18).

The primary output (contract Part 8) is the executed query result (a Polars
DataFrame) plus the transparency record for a known question against a
synthetic SQLite fixture, with the LLM replaced by a scripted stand-in.

The fixtures are SYNTHETIC - no real sample was provided (contract Part 8,
B1). They are built by tests/fixtures/make_fixture.py. Two variants with
different content prove the pipeline derives rather than recites.

The project is imported INSIDE each test function: at C0 the code does not
exist yet, and a failing top-level import would stop pytest collecting any
test.
"""

from tests.fixtures.make_fixture import build_fixture


class ScriptedLLM:
    """A scripted stand-in for the LLM provider boundary (no network, no key).

    Returns a fixed interpretation, plan and SQL for the known question, and a
    fixed explanation. The pipeline must treat this as the outside world and
    never call a real model.
    """

    def interpret(self, request):
        return {
            "intent": "aggregate",
            "entity": "trades",
            "metrics": ["notional_value"],
            "dimensions": ["region"],
            "filters": [],
            "time_intent": {"kind": "this_year"},
            "output": "table",
            "ambiguities": [],
        }

    def plan(self, request):
        return {
            "intent": "aggregate",
            "tables": ["trades"],
            "columns": ["region", "notional_value"],
            "joins": [],
            "filters": [],
            "metrics": ["SUM(notional_value)"],
            "grouping": ["region"],
            "ordering": [],
            "limits": [],
            "time_bounds": {"start": "2026-01-01", "end": "2026-12-31"},
            "expected_output": "table",
        }

    def generate_sql(self, request):
        return (
            "SELECT region, SUM(notional_value) AS total FROM trades "
            "WHERE trade_date >= '2026-01-01' AND trade_date <= '2026-12-31' "
            "GROUP BY region"
        )

    def explain(self, request):
        return "Total notional value by region for 2026."


def test_artifact_primary_output(tmp_path):
    """The known question yields the exact per-region totals and a transparency record."""
    from app.core.orchestrator import run_turn

    db = build_fixture(str(tmp_path / "trading_fixture.db"), "a")

    turn = run_turn(
        question="total notional value by region for 2026",
        db_path=db,
        llm=ScriptedLLM(),
        user_id="u1",
        workspace_id="w1",
    )

    assert turn.error is None
    rows = {r["region"]: r["total"] for r in turn.result.to_dicts()}
    assert rows["N"] == 1500000.0
    assert rows["S"] == 900000.0
    assert rows["E"] == 600000.0

    assert turn.transparency is not None
    assert "trades" in turn.transparency.tables_used
    assert turn.transparency.canonical_sql == turn.canonical_sql
    assert turn.transparency.resolved_period == ("2026-01-01", "2026-12-31")


def test_artifact_second_fixture_derives_not_recites(tmp_path):
    """A different fixture gives different totals - the pipeline derives, not recites."""
    from app.core.orchestrator import run_turn

    db = build_fixture(str(tmp_path / "trading_fixture_b.db"), "b")

    turn = run_turn(
        question="total notional value by region for 2026",
        db_path=db,
        llm=ScriptedLLM(),
        user_id="u1",
        workspace_id="w1",
    )

    assert turn.error is None
    rows = {r["region"]: r["total"] for r in turn.result.to_dicts()}
    assert rows["W"] == 2500000.0
    assert rows["C"] == 100000.0
