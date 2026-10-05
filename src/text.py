"""
Arabic text rendering for the GUI. Tk on Windows (measured: it draws the words of a logical-order string left to
right) and on Linux needs the text shaped and put in visual order, so it goes through ArabicDisplayer there. macOS
text is left untouched in "auto" (not verified). Override with settings["arabic"]: "auto" (default) | "on" | "off".
Notifications and stored data must always use the original text, never display().
"""
from functools import lru_cache
import re
from sys import platform

from arabicdisplayer import reshape, line_breaker, apply_display, align_text

from .storage import get_settings

# What reshape() leaves out, as measured on Windows (a lone U+0621 among shaped letters is drawn wrongly, and lam+alef
# must be one ligature glyph): lam initial/medial + alef final -> ligature isolated/final, and hamza -> its isolated form.
_ALEF_FINAL = {"ﺎ": 0xFEFB, "ﺄ": 0xFEF7, "ﺈ": 0xFEF9, "ﺂ": 0xFEF5}  # ا أ إ آ -> lam-alef ligature (isolated form)
_FIXES = {"ء": "ﺀ", **{lam + alef: chr(ligature + final) for lam, final in (("ﻟ", 0), ("ﻠ", 1))
                                  for alef, ligature in _ALEF_FINAL.items()}}
_FIX = re.compile("|".join(map(re.escape, _FIXES)))


@lru_cache(maxsize=512)
def render(text: str, width: int = None, align: bool = False) -> str:
    """Unconditional pipeline: reshape -> wrap -> visual order -> align."""
    text = _FIX.sub(lambda m: _FIXES[m.group()], reshape(text, harakat=False))  # diacritics are dropped: measured on Windows, the library's mark placement breaks the word (تبعاً)
    if width: text = line_breaker(text, width)
    text = apply_display(text)
    return align_text(text, width) if width and align else text


def is_active() -> bool:
    settings = get_settings()
    mode = settings.get("arabic", "auto")
    return settings.get("language", "ar") == "ar" and (mode == "on" or mode == "auto" and platform.startswith(("win", "linux")))


def display(text, width: int = None, align: bool = False) -> str:
    """Text ready for a Tk widget: processed when needed on this platform, unchanged otherwise."""
    text = str(text)
    return render(text, width, align) if is_active() else text
