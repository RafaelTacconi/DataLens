"""The query pipeline orchestrator (R18, R20, R28, R32, R38, R41).

Coordinates the stages of a turn. This module holds no SQL parser internals
and no UI rendering (Guide §4). It grows checkpoint by checkpoint.
"""

import uuid

from app.metadata.audit import append_audit
from app.models.contracts import Turn
from app.sql.canonical import canonicalize_sql
from app.sql.validator import ValidationError, validate_sql


def run_analysis(plan, executor_fn):
    """Run a multi-step analysis, each output naming its source (R32).

    Args:
        plan: a QueryPlan with analysis_steps.
        executor_fn: a callable that runs one step and returns a DataFrame.

    Returns:
        A list of dicts, each with "source", "detail" and "rows".
    """
    outputs = []
    for step in plan.analysis_steps:
        df = executor_fn(step)
        outputs.append({
            "source": step.kind,
            "detail": step.detail,
            "rows": df.to_dicts(),
        })
    return outputs


def needs_clarification(interpretation):
    """Whether an interpretation has material ambiguities that must be asked.

    Args:
        interpretation: an Interpretation model.

    Returns:
        True if the user must be asked before proceeding (R18).
    """
    return bool(interpretation.ambiguities)


def generate_and_validate_sql(provider, plan, schema, allowed_tables):
    """Get a draft from the provider, validate it, return canonical SQL (R20).

    The draft is never executed directly: it must pass validation first.

    Args:
        provider: an LLMProvider.
        plan: the approved QueryPlan.
        schema: the target database schema.
        allowed_tables: the exposed-table allow-list.

    Returns:
        The canonical SQL string.

    Raises:
        ValidationError: if the draft is unsafe or does not match the schema.
    """
    draft = provider.generate_sql({"plan": plan})
    validate_sql(draft, schema, allowed_tables, plan)
    return canonicalize_sql(draft)


def generate_sql_with_retries(provider, plan, schema, allowed_tables,
                              max_attempts=3):
    """Generate and validate SQL, retrying up to the attempt limit (R38).

    Args:
        provider: an LLMProvider.
        plan: the approved QueryPlan.
        schema: the target database schema.
        allowed_tables: the exposed-table allow-list.
        max_attempts: the maximum total SQL attempts.

    Returns:
        The canonical SQL string.

    Raises:
        ValidationError: if the draft never validates within the limit.
    """
    last_error = None
    for _ in range(max_attempts):
        try:
            return generate_and_validate_sql(provider, plan, schema,
                                             allowed_tables)
        except ValidationError as err:
            last_error = err
    raise last_error


def timeout_message():
    """The message shown when a query times out (R38).

    A timeout is not auto-retried; the user is asked to narrow the request.
    """
    return "The query was too expensive. Please narrow the request."


def record_feedback(conn, turn, feedback, correction_text=None):
    """Record feedback on a turn (R28).

    A "not what I meant" correction creates a new turn and is audited; the
    previous turn is never silently modified.

    Args:
        conn: the metadata sqlite3 connection.
        turn: the Turn the feedback concerns.
        feedback: "correct" or "not_what_i_meant".
        correction_text: the user's correction, for a "not what I meant".

    Returns:
        A new Turn for a correction, or None for a correct result.
    """
    append_audit(
        conn,
        event_type="user_feedback",
        workspace_id=turn.workspace_id,
        actor=turn.user_id,
        target=turn.run_id,
        after={"feedback": feedback, "correction": correction_text},
    )
    if feedback == "not_what_i_meant":
        return Turn(
            run_id=uuid.uuid4().hex,
            workspace_id=turn.workspace_id,
            user_id=turn.user_id,
            question=correction_text or turn.question,
        )
    return None