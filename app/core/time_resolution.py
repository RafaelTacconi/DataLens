"""Relative date resolution (R24).

Python resolves relative dates (today, this week/month/year, last month, YTD)
into explicit start/end values; the LLM never calculates today's date (SDD
§18, Guide §11). The resolved period is shown in the transparency panel.
"""

import datetime


def resolve_time_intent(time_intent, now=None):
    """Resolve a relative time intent into explicit (start, end) dates.

    Args:
        time_intent: a dict with a "kind" key, e.g. {"kind": "this_year"}.
        now: the reference datetime (defaults to the current UTC time).

    Returns:
        A tuple (start, end) of ISO date strings.

    Raises:
        ValueError: if the time intent kind is unknown.
    """
    now = now or datetime.datetime.now(datetime.timezone.utc)
    kind = time_intent.get("kind")

    if kind in ("this_year", "year_to_date"):
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0,
                            microsecond=0)
        return start.date().isoformat(), now.date().isoformat()

    if kind == "this_month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return start.date().isoformat(), now.date().isoformat()

    if kind == "this_week":
        start = (now - datetime.timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0)
        return start.date().isoformat(), now.date().isoformat()

    if kind == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start.date().isoformat(), now.date().isoformat()

    if kind == "last_month":
        first_this = now.replace(day=1, hour=0, minute=0, second=0,
                                 microsecond=0)
        end = first_this - datetime.timedelta(days=1)
        start = end.replace(day=1)
        return start.date().isoformat(), end.date().isoformat()

    raise ValueError(f"unknown time intent: {kind}")