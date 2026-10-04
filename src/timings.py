"""
Today's prayer timings: fetched from Aladhan, cached on disk so restarts and offline days keep working.
A "day" is {"date", "key", "timings", "hijri", "weekday"[, "stale"]}; `key` = [lat, lon, method] it was fetched for.
"""
from datetime import date as Date
from typing import Any, Dict, List, Optional

from requests import RequestException

from . import api
from .config import DATA_DIR, PRAYER_ORDER
from .storage import read_json, write_json

CACHE_PATH = DATA_DIR / "timings.json"
_ERRORS = (RequestException, ValueError, KeyError, TypeError)


def _locate(settings: Dict[str, Any], cache: Dict[str, Any], refresh: bool) -> Optional[List[float]]:
    """Manual coordinates win; otherwise the cached IP location, looked up again when `refresh` (new day)."""
    if not settings["auto_location"] and None not in (settings["latitude"], settings["longitude"]):
        return [settings["latitude"], settings["longitude"]]
    if refresh or not cache.get("ip_location"):
        try: cache["ip_location"] = list(api.locate() or cache.get("ip_location") or []) or None
        except _ERRORS: pass
    return cache.get("ip_location")


def _fetch(key: List[float], today: Date) -> Dict[str, Any]:
    data = api.get_timings(*key[:2], method=key[2], date=today.strftime("%d-%m-%Y"))
    hijri = data["date"]["hijri"]
    return {
        "date": today.isoformat(), "key": key,
        "timings": {k: v.split()[0] for k, v in data["timings"].items() if k in PRAYER_ORDER},  # drop "(EET)" suffixes
        "hijri": {"day": int(hijri["day"]), "month": int(hijri["month"]["number"]), "year": int(hijri["year"])},
        "weekday": data["date"]["gregorian"]["weekday"]["en"],
    }


def current_day(settings: Dict[str, Any], today: Optional[Date] = None) -> Optional[Dict[str, Any]]:
    """The cached day if it is today's for these settings, else a fresh fetch, else the stale cache, else None.
    Blocking (network): call it off the UI thread."""
    today = today or Date.today()
    cache = read_json(CACHE_PATH) or {}
    day = cache.get("day")
    where = _locate(settings, cache, refresh=not (day and day["date"] == today.isoformat()))
    key = [*where, settings["method"]] if where else None
    if day and key and day["date"] == today.isoformat() and day["key"] == key: return day
    if key:
        try: cache["day"] = day = _fetch(key, today)
        except _ERRORS: return {**day, "stale": True} if day else None
        write_json(CACHE_PATH, cache)
        return day
    return {**day, "stale": True} if day else None
