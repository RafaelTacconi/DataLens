"""The query pipeline orchestrator (R18, R20, R28, R32, R38, R41).

Coordinates the stages of a turn. This module holds no SQL parser internals
and no UI rendering (Guide §4). It grows checkpoint by checkpoint.
"""

from app.sql.canonical import canonicalize_sql
from app.sql.validator import validate_sql


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