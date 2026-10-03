"""Versioned prompt templates (R20, R42).

Prompts live here, separate from business logic (Guide §4). They are versioned
and every turn records the prompt-template version (SDD §36). Prompts are not
security controls; code remains the enforcement layer.
"""

PROMPT_VERSION = "1.0"


def prompt_version():
    """The current prompt-template version (R42)."""
    return PROMPT_VERSION


def record_prompt_version(transparency):
    """Record the prompt-template version on a turn's transparency record.

    Args:
        transparency: a TransparencyRecord.

    Returns:
        The same record with the version added to its provenance.
    """
    provenance = dict(transparency.provenance)
    provenance["prompt_version"] = PROMPT_VERSION
    transparency.provenance = provenance
    return transparency


def build_sql_prompt(plan):
    """Build the prompt that asks the LLM to draft SQL from a plan.

    Args:
        plan: the approved QueryPlan.

    Returns:
        A prompt string.
    """
    return (
        "You are a SQLite query planner. Draft exactly one read-only SELECT "
        "statement for the approved plan. Never write to the database. "
        f"Plan: {plan.model_dump_json()}\n"
        "Return only the SQL."
    )