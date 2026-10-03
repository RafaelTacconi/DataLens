"""Tests for app/llm/prompts.py prompt versioning (R42)."""

from app.llm.prompts import prompt_version, record_prompt_version
from app.models.contracts import TransparencyRecord


def test_prompt_version_is_recorded_on_turn():
    """R42: every turn records the prompt-template version."""
    rec = TransparencyRecord()
    rec = record_prompt_version(rec)
    assert rec.provenance["prompt_version"] == prompt_version()