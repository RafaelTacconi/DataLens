"""Versioned prompt templates (R20, R42).

Prompts live here, separate from business logic (Guide §4). They are versioned
and every turn records the prompt-template version (SDD §36). Prompts are not
security controls; code remains the enforcement layer.
"""

PROMPT_VERSION = "1.0"


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