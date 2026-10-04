"""
Arabic text rendering for the GUI. Windows/macOS Tk shapes and reorders Arabic itself, so text passes through
untouched there; on Linux (X11 Tk) it goes through ArabicDisplayer. Override with settings["arabic"]:
"auto" (default) | "on" | "off". Notifications and stored data must always use the original text, never display().
"""
from functools import lru_cache
from sys import platform

from arabicdisplayer import reshape, line_breaker, apply_display, align_text

from .storage import get_settings


@lru_cache(maxsize=512)
def render(text: str, width: int = None, align: bool = False) -> str:
    """Unconditional pipeline: reshape -> wrap -> visual order -> align."""
    text = reshape(text)
    if width: text = line_breaker(text, width)
    text = apply_display(text)
    return align_text(text, width) if width and align else text


def is_active() -> bool:
    mode = get_settings().get("arabic", "auto")
    return mode == "on" or mode == "auto" and platform.startswith("linux")


def display(text, width: int = None, align: bool = False) -> str:
    """Text ready for a Tk widget: processed when needed on this platform, unchanged otherwise."""
    text = str(text)
    return render(text, width, align) if is_active() else text
