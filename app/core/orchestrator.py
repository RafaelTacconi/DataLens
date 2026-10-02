"""The query pipeline orchestrator (R18, R20, R28, R32, R38, R41).

Coordinates the stages of a turn. This module holds no SQL parser internals
and no UI rendering (Guide §4). It grows checkpoint by checkpoint; the
clarification decision is the first piece.
"""


def needs_clarification(interpretation):
    """Whether an interpretation has material ambiguities that must be asked.

    Args:
        interpretation: an Interpretation model.

    Returns:
        True if the user must be asked before proceeding (R18).
    """
    return bool(interpretation.ambiguities)