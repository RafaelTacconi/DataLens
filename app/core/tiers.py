"""Execution tiers (R33).

Simple/Standard/Extended are computed by Python from the plan, never from an
LLM-generated complexity label (SDD §27). An Extended query shows the plan
and requires user confirmation.
"""


def classify_tier(plan, settings):
    """Classify a query plan into simple, standard or extended.

    Args:
        plan: a QueryPlan.
        settings: the application Settings (tier thresholds).

    Returns:
        "simple", "standard" or "extended".
    """
    joins = len(plan.joins)
    steps = len(plan.analysis_steps)
    if joins <= settings.simple_max_joins and steps == 0:
        return "simple"
    if (joins <= settings.standard_max_joins
            and steps <= settings.standard_max_analysis_steps):
        return "standard"
    return "extended"


def requires_confirmation(tier):
    """Whether a tier requires the user to confirm before execution.

    Args:
        tier: "simple", "standard" or "extended".

    Returns:
        True for extended.
    """
    return tier == "extended"