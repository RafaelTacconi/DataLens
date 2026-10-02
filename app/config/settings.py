"""Application configuration, loaded from the environment with defaults.

R1: every setting the app needs, with a documented default, and no hard-coded
environment-specific path. Values come from environment variables (or a dict,
for tests) or fall back to the defaults below.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """The resolved configuration for one run of the application."""

    metadata_db_path: str = "data/metadata.db"
    timezone: str | None = None  # None = use the end-user's machine timezone
    row_cap: int = 30
    export_cap: int = 10000
    query_timeout_seconds: int = 30
    llm_timeout_seconds: int = 60
    llm_provider: str = "openai"
    llm_model: str = ""
    egress_default: str = "schema_only"
    simple_max_joins: int = 1
    standard_max_joins: int = 3
    standard_max_analysis_steps: int = 2
    audit_retention_days: int = 365
    history_retention_days: int = 30


def load_settings(env=None) -> Settings:
    """Build a Settings from environment variables (or a dict, for tests).

    Args:
        env: a mapping of environment variables; defaults to os.environ.

    Returns:
        A Settings instance with every field resolved.
    """
    env = env if env is not None else os.environ

    def _int(name, default):
        return int(env.get(name, str(default)))

    return Settings(
        metadata_db_path=env.get("DATALENS_METADATA_DB", "data/metadata.db"),
        timezone=env.get("DATALENS_TIMEZONE") or None,
        row_cap=_int("DATALENS_ROW_CAP", 30),
        export_cap=_int("DATALENS_EXPORT_CAP", 10000),
        query_timeout_seconds=_int("DATALENS_QUERY_TIMEOUT", 30),
        llm_timeout_seconds=_int("DATALENS_LLM_TIMEOUT", 60),
        llm_provider=env.get("DATALENS_LLM_PROVIDER", "openai"),
        llm_model=env.get("LLM_MODEL", ""),
        egress_default=env.get("DATALENS_EGRESS_DEFAULT", "schema_only"),
        simple_max_joins=_int("DATALENS_SIMPLE_MAX_JOINS", 1),
        standard_max_joins=_int("DATALENS_STANDARD_MAX_JOINS", 3),
        standard_max_analysis_steps=_int(
            "DATALENS_STANDARD_MAX_ANALYSIS_STEPS", 2),
        audit_retention_days=_int("DATALENS_AUDIT_RETENTION_DAYS", 365),
        history_retention_days=_int("DATALENS_HISTORY_RETENTION_DAYS", 30),
    )