"""Structured LLM output parsing (R17).

All LLM output is parsed into the typed Pydantic models. Malformed output is
rejected, never silently accepted (SDD §35, Guide §3.9).
"""

from app.models.contracts import Interpretation


def parse_interpretation(data):
    """Parse LLM output into an Interpretation model.

    Args:
        data: the structured interpretation returned by the LLM.

    Returns:
        An Interpretation.

    Raises:
        pydantic.ValidationError: if the output is malformed.
    """
    return Interpretation(**data)