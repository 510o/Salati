"""
Pure scheduling logic (no I/O): what the countdown shows and when notifications are due.
Prayer times are clock times that repeat daily, so every event is looked up in yesterday/today/tomorrow.
"""

from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional, Tuple

from .time_utils import parse_time

DAY = timedelta(days=1)


def _occurrences(times: Dict[str, str], names: Iterable[str], now: datetime):
    """(datetime, name) for every valid listed prayer on days now-1, now, now+1."""
    for name in names:
        t = parse_time(times.get(name))
        if t:
            for shift in (-DAY, timedelta(0), DAY):
                yield datetime.combine(now.date(), t) + shift, name


def countdown(times: Dict[str, str], names: Iterable[str], now: Optional[datetime] = None, elapsed_minutes: int = 35) -> Optional[dict]:
    """
    What to show now: {"name", "seconds", "elapsed"}.
    - elapsed False: `seconds` until the next prayer in `names`.
    - elapsed True: `seconds` since a prayer that began within `elapsed_minutes` (count-up).
    None if no valid times.
    """
    now = now or datetime.now()
    events = list(_occurrences(times, names, now))
    upcoming = [e for e in events if e[0] > now]
    if not upcoming: return None
    (nxt, nxt_name) = min(upcoming)
    (last, last_name) = max(e for e in events if e[0] <= now)  # yesterday's events guarantee one exists
    if now - last <= timedelta(minutes=elapsed_minutes):
        return {"name": last_name, "seconds": (now - last).total_seconds(), "elapsed": True}
    return {"name": nxt_name, "seconds": (nxt - now).total_seconds(), "elapsed": False}


def next_notification(times: Dict[str, str], rules: Dict[str, List[int]], now: Optional[datetime] = None) -> Optional[Tuple[datetime, str, int]]:
    """
    Earliest (datetime, prayer, offset_minutes) strictly after `now`.
    `rules` maps a prayer name to its offsets in minutes (negative = before the prayer, positive = after).
    """
    now = now or datetime.now()
    due = [(when + timedelta(minutes=offset), name, offset)
           for when, name in _occurrences(times, rules, now) for offset in rules[name]]
    return min((d for d in due if d[0] > now), default=None)
