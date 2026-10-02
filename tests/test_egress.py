"""Tests for app/llm/egress.py (R35)."""

import pytest

from app.llm.egress import allowed_content, default_level, filter_sensitive


def test_default_is_safest():
    """R35: the default egress level is the safest configured one."""
    assert default_level() == "schema_only"


def test_schema_only_excludes_result_rows():
    """R35: schema_only sends no result rows or aggregates."""
    content = allowed_content("schema_only")
    assert "samples" not in content
    assert "aggregates" not in content
    assert "schema" in content


def test_aggregates_adds_aggregates_not_samples():
    """R35: aggregates adds aggregates but still no sample rows."""
    content = allowed_content("aggregates")
    assert "aggregates" in content
    assert "samples" not in content


def test_samples_adds_samples():
    """R35: samples is the only level that may send sample rows."""
    content = allowed_content("samples")
    assert "samples" in content


def test_unknown_level_rejected():
    """R35: an unknown level is refused, not silently treated as safe."""
    with pytest.raises(ValueError):
        allowed_content("everything")


def test_sensitive_columns_never_sent():
    """R35: sensitive columns are removed from what may be sent."""
    cols = filter_sensitive(["region", "salary", "name"], {"salary", "name"})
    assert cols == ["region"]