"""Tests for app/core/orchestrator.py feedback (R28)."""

from app.core.orchestrator import record_feedback
from app.metadata.store import create_workspace, open_metadata_db
from app.models.contracts import Turn


def _turn():
    return Turn(run_id="r1", workspace_id="w1", user_id="u1",
                question="total by region")


def test_correction_creates_new_turn_and_audits(tmp_path):
    """R28: a correction creates a new turn and is audited."""
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    try:
        create_workspace(conn, "w1", "Trading", "data/trades.db")
        new_turn = record_feedback(conn, _turn(), "not_what_i_meant",
                                   correction_text="total by country")
        assert new_turn is not None
        assert new_turn.question == "total by country"
        rows = conn.execute(
            "SELECT * FROM audit_events WHERE event_type='user_feedback'"
        ).fetchall()
        assert len(rows) == 1
    finally:
        conn.close()


def test_correct_feedback_no_new_turn(tmp_path):
    """R28: a correct result does not create a new turn."""
    conn = open_metadata_db(str(tmp_path / "metadata.db"))
    try:
        create_workspace(conn, "w1", "Trading", "data/trades.db")
        new_turn = record_feedback(conn, _turn(), "correct")
        assert new_turn is None
    finally:
        conn.close()