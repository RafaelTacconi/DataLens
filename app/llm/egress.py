"""LLM data egress policy (R35).

Controls how much workspace information may be sent to an external LLM (SDD
§13). The default is the safest configured level, and sensitive columns are
never profiled or sent.
"""

LEVELS = ("schema_only", "aggregates", "samples")

# What each level may send. schema_only is the safest and the default.
_ALLOWED = {
    "schema_only": {
        "schema", "descriptions", "business_terms", "business_rules",
        "time_bounds",
    },
    "aggregates": {
        "schema", "descriptions", "business_terms", "business_rules",
        "time_bounds", "aggregates", "facts",
    },
    "samples": {
        "schema", "descriptions", "business_terms", "business_rules",
        "time_bounds", "aggregates", "facts", "samples",
    },
}


def default_level():
    """The default egress level: the safest configured one."""
    return "schema_only"


def allowed_content(level):
    """The kinds of content that may be sent at a given egress level.

    Args:
        level: "schema_only", "aggregates" or "samples".

    Returns:
        A set of content kinds.

    Raises:
        ValueError: if the level is unknown.
    """
    if level not in _ALLOWED:
        raise ValueError(f"unknown egress level: {level}")
    return set(_ALLOWED[level])


def filter_sensitive(columns, sensitive_columns):
    """Remove sensitive columns from a list of columns.

    Args:
        columns: the candidate columns.
        sensitive_columns: columns that must never be profiled or sent.

    Returns:
        The columns with sensitive ones removed.
    """
    sensitive = set(sensitive_columns)
    return [c for c in columns if c not in sensitive]