"""JSON helpers and the settings store: stored values over schema defaults, cached in memory."""
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock
from typing import Any, Dict

from .config import SETTINGS_PATH
from .schema import merged

_lock, _cache = Lock(), None


def read_json(path: Path) -> Any:
    """Parsed JSON, or None if the file is missing or unreadable."""
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError): return None


def write_json(path: Path, data: Any) -> None:
    """Write to a temp file in the same dir, then replace (a crash never leaves a half-written file)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding="utf-8") as tf:
        json.dump(data, tf, ensure_ascii=False, indent=4)
    Path(tf.name).replace(path)


def get_settings() -> Dict[str, Any]:
    """All settings (new options appear with their defaults without resetting the user's choices)."""
    global _cache
    with _lock:
        if _cache is None:
            raw = read_json(SETTINGS_PATH)
            _cache = merged(raw if isinstance(raw, dict) else {})
        return dict(_cache)


def update_settings(changes: Dict[str, Any]) -> Dict[str, Any]:
    """Save the given keys; returns the new settings."""
    global _cache
    data = {**get_settings(), **changes}
    with _lock:
        write_json(SETTINGS_PATH, data)
        _cache = data
    return dict(data)
