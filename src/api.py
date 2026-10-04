"""Aladhan timings and IP geolocation over one `requests` session with retries."""
from typing import Any, Dict, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api.aladhan.com/v1"
_session = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        _session.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))))
    return _session


def get_timings(latitude: float, longitude: float, method: Optional[int] = None, date: Optional[str] = None, timeout: int = 10) -> Dict[str, Any]:
    """Aladhan's `data` for `date` ('DD-MM-YYYY', default today). Method 0 is valid. The date must go in the
    path: the API silently ignores a `date` query parameter. Raises requests.HTTPError / KeyError on bad replies."""
    params = {"latitude": latitude, "longitude": longitude, **({} if method is None else {"method": method})}
    resp = _get_session().get(f"{BASE_URL}/timings" + (f"/{date}" if date else ""), params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()["data"]


def locate(timeout: int = 10) -> Optional[Tuple[float, float]]:
    """Approximate (latitude, longitude) from the public IP (ipwho.is); None if the lookup is refused."""
    resp = _get_session().get("https://ipwho.is/", timeout=timeout)
    resp.raise_for_status()
    j = resp.json()
    return (float(j["latitude"]), float(j["longitude"])) if j.get("success") else None
