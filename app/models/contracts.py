"""Typed data contracts (R43).

Pydantic models for the structured data that flows through the pipeline (SDD
§41). All LLM output is parsed into these models; malformed output is
rejected, never silently accepted.
"""

from typing import Any, List, Optional

from pydantic import BaseModel


class Interpretation(BaseModel):
    """The structured interpretation of a user request (SDD §16)."""

    intent: str
    entity: str
    metrics: List[str] = []
    dimensions: List[str] = []
    filters: List[dict] = []
    time_intent: dict = {}
    output: str = "table"
    ambiguities: List[str] = []


class Ambiguity(BaseModel):
    """A material ambiguity that must be asked of the user (SDD §17)."""

    question: str
    options: List[str] = []


class QueryStep(BaseModel):
    """One step of an analysis plan (SDD §26)."""

    kind: str
    detail: str = ""


class QueryPlan(BaseModel):
    """The structured query plan (SDD §19)."""

    intent: str = ""
    tables: List[str] = []
    columns: List[str] = []
    joins: List[dict] = []
    filters: List[dict] = []
    metrics: List[str] = []
    grouping: List[str] = []
    ordering: List[str] = []
    limits: List[str] = []
    time_bounds: dict = {}
    expected_output: str = "table"
    analysis_steps: List[QueryStep] = []


class ExecutionMetrics(BaseModel):
    """Honest execution metrics (SDD §23)."""

    duration_seconds: float = 0.0
    rows_returned: int = 0
    truncated: bool = False
    plan_shape: str = ""


class FactsPayload(BaseModel):
    """The facts an explanation is allowed to use (SDD §25)."""

    facts: List[dict] = []


class TransparencyRecord(BaseModel):
    """The transparency panel for a completed turn (SDD §28)."""

    request: str = ""
    understanding: str = ""
    tables_used: List[str] = []
    why_sources: str = ""
    columns_used: List[str] = []
    plan: dict = {}
    canonical_sql: str = ""
    execution: dict = {}
    assumptions: List[str] = []
    resolved_period: tuple = ()
    result_summary: str = ""
    validation_status: str = ""
    provenance: dict = {}


class Turn(BaseModel):
    """The state and output of one user turn (SDD §33, Guide §5)."""

    run_id: str
    workspace_id: str
    user_id: str
    question: str
    stage: str = "NEW"
    interpretation: Optional[Interpretation] = None
    plan: Optional[QueryPlan] = None
    canonical_sql: str = ""
    result: Any = None
    transparency: Optional[TransparencyRecord] = None
    error: Optional[str] = None


class AuditEvent(BaseModel):
    """One append-only audit event (SDD §11)."""

    event_type: str
    workspace_id: Optional[str] = None
    actor: Optional[str] = None
    identity_source: str = "os"
    timestamp: str = ""
    target: Optional[str] = None


class Workspace(BaseModel):
    """One workspace: a target database plus its business knowledge (SDD §7)."""

    id: str
    name: str
    target_db_path: str
    egress_level: str = "schema_only"


class Membership(BaseModel):
    """A user's role in a workspace (SDD §8)."""

    workspace_id: str
    user_id: str
    role: str


class VerifiedQuery(BaseModel):
    """A promoted, verified query (SDD §31)."""

    workspace_id: str
    question: str
    canonical_sql: str
    status: str = "verified"


class EvaluationCase(BaseModel):
    """A golden question for evaluation (SDD §32)."""

    workspace_id: str
    question: str
    expected_columns: List[str] = []
    expected_rows: List[list] = []
    order_matters: bool = False