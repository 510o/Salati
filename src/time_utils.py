"""Time parsing/formatting helpers (pure functions)."""
from datetime import datetime, time as dt_time
from typing import Optional

_EASTERN = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def to_eastern_digits(text) -> str:
    return str(text).translate(_EASTERN)


def parse_time(value) -> Optional[dt_time]:
    """"05:30", "05:30:00" or "5:30 AM" -> time; None if it is anything else."""
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M:%S %p"):
        try: return datetime.strptime(str(value).strip(), fmt).time()
        except ValueError: pass


def format_hms(seconds: float) -> str:
    """Seconds -> "H:MM:SS" (absolute value)."""
    h, r = divmod(abs(int(seconds)), 3600)
    return f"{h}:{r // 60:02}:{r % 60:02}"


def format_clock(t: dt_time, hour12: bool = True, eastern: bool = True) -> str:
    """Clock time for display: "٥:١٢ م" (eastern) or "5:12 PM"; 24-hour: "١٧:١٢" / "17:12"."""
    if not hour12: text = f"{t.hour:02}:{t.minute:02}"
    else: text = f"{t.hour % 12 or 12}:{t.minute:02} " + (("م" if eastern else "PM") if t.hour >= 12 else ("ص" if eastern else "AM"))
    return to_eastern_digits(text) if eastern else text
