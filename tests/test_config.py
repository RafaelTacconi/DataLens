"""Tests for app/config/settings.py (R1)."""

import pathlib
import re

from app.config.settings import load_settings


def test_load_settings_defaults():
    """Every setting has a documented default when the environment is empty."""
    s = load_settings({})
    assert s.row_cap == 30
    assert s.export_cap == 10000
    assert s.query_timeout_seconds == 30
    assert s.egress_default == "schema_only"
    assert s.audit_retention_days == 365
    assert s.history_retention_days == 30
    assert s.llm_provider == "openai"


def test_load_settings_from_env():
    """Environment variables override the defaults."""
    s = load_settings({"DATALENS_ROW_CAP": "50", "LLM_MODEL": "gpt-4o-mini"})
    assert s.row_cap == 50
    assert s.llm_model == "gpt-4o-mini"


def test_no_absolute_path_in_config():
    """R1: no hard-coded environment-specific path in the config module."""
    text = pathlib.Path("app/config/settings.py").read_text(encoding="utf-8")
    assert not re.search(r"[A-Za-z]:[\\/]", text)