"""
Background desktop notifications. A daemon thread sleeps until the next due (prayer, offset) and fires it through the
OS-native backend (no extra dependency except `plyer` on Windows). Messages are plain text: never pass display() output.
"""
import subprocess
import threading
from datetime import datetime, timedelta
from sys import platform
from typing import Callable, Dict, Tuple

from .config import APP_NAME, ASSETS_DIR, PRAYER_ORDER, PRAYER_LABELS
from .prayer_logic import next_notification
from .storage import get_settings

ICON = str(ASSETS_DIR / "icon.png")
MAX_SLEEP, GRACE = 30, timedelta(seconds=60)  # re-check settings at least every 30s; skip events missed by over a minute


def message(prayer: str, offset: int) -> Tuple[str, str]:
    """(title, text) for a prayer notification; offset in minutes, negative = before the prayer."""
    name = PRAYER_LABELS[prayer]
    if offset == 0: return f"وقت {name}", f"حان الآن وقت {name}"
    if offset < 0: return name, f"بقي {-offset} دقيقة على {name}"
    return name, f"مضت {offset} دقيقة على {name}"


def send(title: str, text: str) -> None:
    if platform == "darwin":
        script = f'display notification {_quote(text)} with title {_quote(title)}'
        subprocess.run(["osascript", "-e", script], check=False)
    elif platform.startswith("linux"):
        subprocess.run(["notify-send", "-i", ICON, "-a", APP_NAME, title, text], check=False)
    else:
        from plyer import notification
        notification.notify(title=title, message=text, app_name=APP_NAME, timeout=10)


def _quote(s: str) -> str:  # AppleScript string literal
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


class Notifier(threading.Thread):
    """`get_times` returns today's {prayer: "HH:MM"} (may be empty); `wake()` makes it re-read settings and times now."""

    def __init__(self, get_times: Callable[[], Dict[str, str]], sender: Callable[[str, str], None] = send):
        super().__init__(daemon=True, name="notifier")
        self.get_times, self.sender = get_times, sender
        self._wake, self._stop_event = threading.Event(), threading.Event()

    def wake(self) -> None: self._wake.set()

    def stop(self) -> None: self._stop_event.set(); self._wake.set()

    def run(self) -> None:
        while not self._stop_event.is_set():
            settings, upcoming = get_settings(), None
            if settings["notifications"]:
                rules = {p: settings[f"notify_{p}"] for p in PRAYER_ORDER}
                upcoming = next_notification(self.get_times() or {}, rules)
            wait = MAX_SLEEP if not upcoming else min(MAX_SLEEP, max(0.2, (upcoming[0] - datetime.now()).total_seconds()))
            if self._wake.wait(wait):
                self._wake.clear(); continue
            if upcoming and timedelta(0) <= datetime.now() - upcoming[0] < GRACE:  # due now (not a missed one)
                try: self.sender(*message(*upcoming[1:]))
                except Exception as e: print(f"notification failed: {e}")  # a broken backend must not kill the thread
