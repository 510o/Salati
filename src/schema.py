"""
The single definition of every user setting. Defaults, validation and the settings window are all generated from
SETTINGS: to add a feature's option, add one Setting here (storage, defaults merge and the UI pick it up).
"""
from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .config import MAIN_PRAYERS, PRAYER_LABELS, PRAYER_ORDER

# kinds: bool | choice (value from `choices`) | int | float | ints (list of ints) ; a None default makes int/float optional
@dataclass(frozen=True)
class Setting:
    key: str
    kind: str
    label: str
    default: Any
    section: str
    choices: Tuple[Tuple[Any, str], ...] = ()  # (value, label) pairs, for kind == "choice"
    lo: float = None
    hi: float = None
    hint: str = ""

    def coerce(self, raw: Any) -> Any:
        """Validated value for `raw` (widget input or stored JSON); raises ValueError with a user-facing reason."""
        if self.kind == "bool": return bool(raw)
        if self.kind == "choice":
            if raw not in dict(self.choices): raise ValueError("قيمة غير مدعومة")
            return raw
        if self.kind == "ints":
            try: return [int(p) for p in (raw.replace("،", ",").split(",") if isinstance(raw, str) else raw) if str(p).strip()]
            except (ValueError, TypeError): raise ValueError("أرقام صحيحة مفصولة بفواصل") from None
        if raw in (None, "") and self.default is None: return None
        try: value = (int if self.kind == "int" else float)(raw)
        except (ValueError, TypeError): raise ValueError("رقم غير صالح") from None
        if (self.lo is not None and value < self.lo) or (self.hi is not None and value > self.hi):
            raise ValueError(f"القيمة بين {self.lo:g} و{self.hi:g}")
        return value


SECTIONS = (("appearance", "المظهر"), ("location", "الموقع والحساب"), ("notifications", "الإشعارات"))

_METHODS = (
    (None, "تلقائية حسب الموقع"), (3, "رابطة العالم الإسلامي"), (5, "الهيئة المصرية العامة للمساحة"), (4, "أم القرى (مكة)"),
    (2, "أمريكا الشمالية (ISNA)"), (1, "جامعة العلوم الإسلامية بكراتشي"), (8, "منطقة الخليج"), (9, "الكويت"), (10, "قطر"),
    (16, "دبي"), (23, "الأردن"), (21, "المغرب"), (19, "الجزائر"), (18, "تونس"), (13, "تركيا (ديانت)"), (14, "روسيا"),
    (12, "فرنسا (UOIF)"), (11, "سنغافورة"), (17, "ماليزيا (جاكيم)"), (20, "إندونيسيا (كمنج)"), (22, "لشبونة"),
    (15, "لجنة رؤية الهلال"), (7, "طهران"), (0, "الجعفرية (قم)"),
)

_NOTIFY = tuple(
    Setting(f"notify_{p}", "ints", PRAYER_LABELS[p], [0] if p in MAIN_PRAYERS and p != "Sunrise" else [], "notifications",
            hint="دقائق قبل (-) أو بعد الوقت، مفصولة بفواصل: -10, 0")
    for p in PRAYER_ORDER
)

SETTINGS: Tuple[Setting, ...] = (
    Setting("theme", "choice", "السمة", "system", "appearance", (("system", "حسب النظام"), ("light", "فاتحة"), ("dark", "داكنة"))),
    Setting("font_size", "int", "حجم الخط", 20, "appearance", lo=10, hi=60),
    Setting("time_format", "choice", "نظام الساعة", 12, "appearance", ((12, "12 ساعة"), (24, "24 ساعة"))),
    Setting("eastern_digits", "bool", "الأرقام الهندية (١٢٣) وص/م", True, "appearance"),
    Setting("night_times", "bool", "عدّ تنازلي لأثلاث الليل ومنتصفه", True, "appearance"),
    Setting("arabic", "choice", "معالجة الحروف العربية", "auto", "appearance",
            (("auto", "تلقائي"), ("on", "مفعّلة"), ("off", "معطّلة")), hint="يلزم لينكس فقط عادةً"),
    Setting("auto_location", "bool", "تحديد الموقع تلقائياً (عبر IP)", True, "location"),
    Setting("latitude", "float", "خط العرض", None, "location", lo=-90, hi=90, hint="عند إيقاف التحديد التلقائي"),
    Setting("longitude", "float", "خط الطول", None, "location", lo=-180, hi=180, hint="عند إيقاف التحديد التلقائي"),
    Setting("method", "choice", "طريقة الحساب", None, "location", _METHODS),
    Setting("elapsed_minutes", "int", "مدة العدّ التصاعدي بعد الوقت (دقيقة)", 35, "location", lo=0, hi=180),
    Setting("notifications", "bool", "تفعيل الإشعارات", True, "notifications"),
) + _NOTIFY

BY_KEY: Dict[str, Setting] = {s.key: s for s in SETTINGS}


def defaults() -> Dict[str, Any]:
    return {s.key: list(s.default) if isinstance(s.default, list) else s.default for s in SETTINGS}


def merged(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Defaults overlaid with every stored value that is still valid; unknown or invalid keys fall back/pass through."""
    out = {**raw, **defaults()}
    for key, value in raw.items():
        try: out[key] = BY_KEY[key].coerce(value) if key in BY_KEY else value
        except ValueError: pass
    return out
