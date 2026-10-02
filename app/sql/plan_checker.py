"""Query plan building and plain-language rendering (R19).

Builds a structured QueryPlan from an interpretation and renders it for the
user. The plan is also the reference the SQL validator checks the generated
SQL against (SDD §19, §21).
"""

from app.models.contracts import QueryPlan


def build_plan(interpretation):
    """Build a QueryPlan from a structured interpretation.

    Args:
        interpretation: an Interpretation model.

    Returns:
        A QueryPlan.
    """
    return QueryPlan(
        intent=interpretation.intent,
        tables=[interpretation.entity] if interpretation.entity else [],
        columns=interpretation.metrics + interpretation.dimensions,
        metrics=[f"SUM({m})" for m in interpretation.metrics],
        grouping=interpretation.dimensions,
        time_bounds=interpretation.time_intent,
    )


def plan_to_plain(plan):
    """Render a QueryPlan in plain language for the user.

    Args:
        plan: a QueryPlan.

    Returns:
        A short human-readable description.
    """
    parts = []
    if plan.tables:
        parts.append("tables: " + ", ".join(plan.tables))
    if plan.metrics:
        parts.append("metrics: " + ", ".join(plan.metrics))
    if plan.grouping:
        parts.append("grouped by: " + ", ".join(plan.grouping))
    return "; ".join(parts)