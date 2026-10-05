"""
The single definition of every user setting. Defaults, validation and the settings window are all generated from
SETTINGS: to add a feature's option, add one Setting here (storage, defaults merge and the UI pick it up).
Texts are Arabic sources; src/i18n.py translates them (coerce raises ValueError(template, *args) for the same reason).
"""
from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .config import FARD, PRAYER_LABELS, PRAYER_ORDER

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
        """Validated value for `raw` (widget input or stored JSON); raises ValueError(template, *args), see i18n.tr."""
        if self.kind == "bool": return bool(raw)
        if self.kind == "choice":
            if raw not in dict(self.choices): raise ValueError("قيمة غير مدعومة")
            return raw
        if self.kind == "ints":
            try: return [int(p) for p in (raw.replace("،", ",").split(",") if isinstance(raw, str) else raw) if str(p).strip()]
            except (ValueError, TypeError): raise ValueError("أدخل أعداداً صحيحة تفصل بينها فواصل") from None
        if raw in (None, "") and self.default is None: return None
        try: value = (int if self.kind == "int" else float)(raw)
        except (ValueError, TypeError): raise ValueError("قيمة عددية غير صالحة") from None
        if (self.lo is not None and value < self.lo) or (self.hi is not None and value > self.hi):
            raise ValueError("يجب أن تكون القيمة بين {0} و{1}", f"{self.lo:g}", f"{self.hi:g}")
        return value


SECTIONS = (("appearance", "المظهر"), ("location", "الموقع والحساب"), ("notifications", "الإشعارات"))

_METHODS = (
    (None, "تلقائية بحسب الموقع"), (3, "رابطة العالم الإسلامي"), (5, "الهيئة المصرية العامة للمساحة"), (4, "جامعة أم القرى (مكة المكرمة)"),
    (2, "الجمعية الإسلامية لأمريكا الشمالية (ISNA)"), (1, "جامعة العلوم الإسلامية بكراتشي"), (8, "دول الخليج"), (9, "الكويت"), (10, "قطر"),
    (16, "دبي"), (23, "الأردن"), (21, "المملكة المغربية"), (19, "الجزائر"), (18, "تونس"), (13, "تركيا (رئاسة الشؤون الدينية)"), (14, "روسيا"),
    (12, "فرنسا (اتحاد المنظمات الإسلامية)"), (11, "سنغافورة"), (17, "ماليزيا (جاكيم)"), (20, "إندونيسيا (وزارة الشؤون الدينية)"),
    (22, "لشبونة (الجالية الإسلامية)"), (15, "لجنة رصد الأهلّة (Moonsighting)"), (7, "جامعة طهران (معهد الجيوفيزياء)"), (0, "الجعفرية (قم)"),
)

_NOTIFY = tuple(
    Setting(f"notify_{p}", "ints", PRAYER_LABELS[p], [0] if p in FARD else [], "notifications",
            hint="الدقائق قبل الوقت (بإشارة سالبة) أو بعده، تفصل بينها فواصل، مثل: -10, 0")
    for p in PRAYER_ORDER
)

SETTINGS: Tuple[Setting, ...] = (
    Setting("language", "choice", "اللغة", "ar", "appearance", (("ar", "العربية"), ("en", "English"))),
    Setting("theme", "choice", "السمة", "system", "appearance", (("system", "تبعاً للنظام"), ("light", "فاتحة"), ("dark", "داكنة"))),
    Setting("font_size", "int", "حجم الخط", 20, "appearance", lo=10, hi=60),
    Setting("time_format", "choice", "نظام عرض الساعة", 12, "appearance", ((12, "12 ساعة"), (24, "24 ساعة"))),
    Setting("eastern_digits", "bool", "الأرقام الهندية (١٢٣) و«ص/م»", True, "appearance"),
    Setting("night_times", "bool", "إدراج أثلاث الليل ومنتصفه في العدّاد", True, "appearance"),
    Setting("arabic", "choice", "معالجة الحروف العربية", "auto", "appearance",
            (("auto", "تلقائية"), ("on", "مفعَّلة"), ("off", "معطَّلة")), hint="تلزم عادةً على ويندوز ولينكس"),
    Setting("auto_location", "bool", "تحديد الموقع تلقائياً (عبر عنوان IP)", True, "location"),
    Setting("latitude", "float", "خط العرض", None, "location", lo=-90, hi=90, hint="تُستخدم عند إيقاف التحديد التلقائي"),
    Setting("longitude", "float", "خط الطول", None, "location", lo=-180, hi=180, hint="تُستخدم عند إيقاف التحديد التلقائي"),
    Setting("method", "choice", "طريقة الحساب", None, "location", _METHODS),
    Setting("elapsed_minutes", "int", "مدة العدّ التصاعدي بعد دخول الوقت (بالدقائق)", 35, "location", lo=0, hi=180),
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
