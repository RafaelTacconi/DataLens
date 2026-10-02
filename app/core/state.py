"""Turn state machine (R13).

A turn moves through the documented stages (SDD §33, Guide §5). A Streamlit
rerun must not repeat an LLM call or a query: the orchestrator only runs a
stage the turn has not already reached, so a rerun resumes rather than redoes.
"""

# The ordered, non-terminal stages of a turn.
STAGES = (
    "NEW",
    "INTERPRETED",
    "AWAITING_CLARIFICATION",
    "PLANNED",
    "AWAITING_CONFIRMATION",
    "VALIDATED",
    "EXECUTED",
    "EXPLAINED",
    "FEEDBACK_GIVEN",
)

TERMINAL_STAGES = ("REFUSED", "FAILED", "TIMED_OUT")

# Which stage each stage may move to. A stage may also move to a terminal
# stage (REFUSED/FAILED/TIMED_OUT) at any point.
VALID_TRANSITIONS = {
    "NEW": {"INTERPRETED"},
    "INTERPRETED": {"AWAITING_CLARIFICATION", "PLANNED"},
    "AWAITING_CLARIFICATION": {"PLANNED"},
    "PLANNED": {"AWAITING_CONFIRMATION", "VALIDATED"},
    "AWAITING_CONFIRMATION": {"VALIDATED"},
    "VALIDATED": {"EXECUTED"},
    "EXECUTED": {"EXPLAINED"},
    "EXPLAINED": {"FEEDBACK_GIVEN"},
    "FEEDBACK_GIVEN": set(),
    "REFUSED": set(),
    "FAILED": set(),
    "TIMED_OUT": set(),
}


class InvalidTransition(Exception):
    """A turn tried to move to a stage it cannot reach from its current one."""


class Turn:
    """The state of one user turn, resumable across Streamlit reruns."""

    def __init__(self, run_id, workspace_id, user_id, question):
        self.run_id = run_id
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.question = question
        self.stage = "NEW"
        self.llm_calls = 0
        self.query_count = 0

    def transition(self, to):
        """Move the turn to a new stage, refusing invalid moves.

        Args:
            to: the target stage name.

        Raises:
            InvalidTransition: if the move is not allowed from the current
                stage.
        """
        allowed = VALID_TRANSITIONS[self.stage] | set(TERMINAL_STAGES)
        if to not in allowed:
            raise InvalidTransition(
                f"cannot move from {self.stage} to {to}")
        self.stage = to

    def has_reached(self, stage):
        """Whether the turn has already reached a stage (so it is not redone).

        Args:
            stage: a stage name.

        Returns:
            True if the turn is at or past the stage in the ordered list.
        """
        if stage in TERMINAL_STAGES:
            return self.stage == stage
        if stage not in STAGES:
            return False
        return STAGES.index(self.stage) >= STAGES.index(stage)

    def record_llm_call(self):
        """Count one LLM call made for this turn."""
        self.llm_calls += 1

    def record_query(self):
        """Count one database query made for this turn."""
        self.query_count += 1