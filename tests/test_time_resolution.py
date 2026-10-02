"""Tests for app/core/time_resolution.py (R24)."""

import datetime

import pytest

from app.core.time_resolution import resolve_time_intent

NOW = datetime.datetime(2026, 5, 15, 12, 0, 0, tzinfo=datetime.timezone.utc)


def test_resolve_this_year():
    start, end = resolve_time_intent({"kind": "this_year"}, now=NOW)
    assert start == "2026-01-01"
    assert end == "2026-05-15"


def test_resolve_this_month():
    start, end = resolve_time_intent({"kind": "this_month"}, now=NOW)
    assert start == "2026-05-01"
    assert end == "2026-05-15"


def test_resolve_last_month():
    start, end = resolve_time_intent({"kind": "last_month"}, now=NOW)
    assert start == "2026-04-01"
    assert end == "2026-04-30"


def test_resolve_today():
    start, end = resolve_time_intent({"kind": "today"}, now=NOW)
    assert start == "2026-05-15"
    assert end == "2026-05-15"


def test_resolve_unknown_raises():
    with pytest.raises(ValueError):
        resolve_time_intent({"kind": "nope"}, now=NOW)