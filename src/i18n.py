"""
UI language. The Arabic strings in the code are the source texts and double as lookup keys: tr() returns them
unchanged for Arabic and the entry of EN for English (settings["language"]); `{0}`/`{name}` placeholders are filled by tr().
"""
from typing import Dict

from .config import FARD, PRAYER_LABELS
from .storage import get_settings

EN: Dict[str, str] = {
    "صلاتي": "Salati",
    # prayers, days, Hijri months
    "الفجر": "Fajr", "الشروق": "Sunrise", "الظهر": "Dhuhr", "العصر": "Asr", "المغرب": "Maghrib", "العشاء": "Isha",
    "الثلث الأول من الليل": "First third of the night", "منتصف الليل": "Midnight", "الثلث الأخير من الليل": "Last third of the night",
    "الأحد": "Sunday", "الاثنين": "Monday", "الثلاثاء": "Tuesday", "الأربعاء": "Wednesday", "الخميس": "Thursday", "الجمعة": "Friday", "السبت": "Saturday",
    "محرم": "Muharram", "صفر": "Safar", "ربيع الأول": "Rabi' al-Awwal", "ربيع الآخر": "Rabi' al-Thani", "جمادى الأولى": "Jumada al-Awwal",
    "جمادى الآخرة": "Jumada al-Thani", "رجب": "Rajab", "شعبان": "Sha'ban", "رمضان": "Ramadan", "شوال": "Shawwal",
    "ذو القعدة": "Dhu al-Qi'dah", "ذو الحجة": "Dhu al-Hijjah",
    "صلاة {0}": "{0} prayer",
    # main window
    "المتبقي حتى دخول الوقت": "Time remaining", "مضى منذ دخول الوقت": "Elapsed since the time began",
    "لا تتوافر مواقيت؛ تحقّق من الاتصال بالإنترنت": "No timings available. Check your internet connection.",
    "هذه مواقيت محفوظة؛ تعذّر التحديث": "Showing saved timings; the update failed.",
    # settings window
    "الإعدادات": "Settings", "حفظ": "Save", "إلغاء": "Cancel", "استعادة الإعدادات الافتراضية": "Restore defaults",
    "المظهر": "Appearance", "الموقع والحساب": "Location & Calculation", "الإشعارات": "Notifications",
    "اللغة": "Language",
    "السمة": "Theme", "تبعاً للنظام": "Follow system", "فاتحة": "Light", "داكنة": "Dark",
    "حجم الخط": "Font size",
    "نظام عرض الساعة": "Clock format", "12 ساعة": "12-hour", "24 ساعة": "24-hour",
    "الأرقام الهندية (١٢٣) و«ص/م»": "Eastern Arabic digits (Arabic interface only)",
    "إدراج أثلاث الليل ومنتصفه في العدّاد": "Include the night thirds and midnight in the countdown",
    "معالجة الحروف العربية": "Arabic text processing", "تلزم عادةً على ويندوز ولينكس": "Usually needed on Windows and Linux",
    "تلقائية": "Automatic", "مفعَّلة": "On", "معطَّلة": "Off",
    "تحديد الموقع تلقائياً (عبر عنوان IP)": "Detect the location automatically (via IP address)",
    "خط العرض": "Latitude", "خط الطول": "Longitude", "تُستخدم عند إيقاف التحديد التلقائي": "Used when automatic detection is off",
    "طريقة الحساب": "Calculation method", "تلقائية بحسب الموقع": "Automatic (by location)",
    "رابطة العالم الإسلامي": "Muslim World League", "الهيئة المصرية العامة للمساحة": "Egyptian General Authority of Survey",
    "جامعة أم القرى (مكة المكرمة)": "Umm Al-Qura University, Makkah", "الجمعية الإسلامية لأمريكا الشمالية (ISNA)": "Islamic Society of North America (ISNA)",
    "جامعة العلوم الإسلامية بكراتشي": "University of Islamic Sciences, Karachi", "دول الخليج": "Gulf Region", "الكويت": "Kuwait", "قطر": "Qatar",
    "دبي": "Dubai", "الأردن": "Jordan", "المملكة المغربية": "Morocco", "الجزائر": "Algeria", "تونس": "Tunisia",
    "تركيا (رئاسة الشؤون الدينية)": "Turkey (Diyanet)", "روسيا": "Russia", "فرنسا (اتحاد المنظمات الإسلامية)": "France (UOIF)",
    "سنغافورة": "Singapore", "ماليزيا (جاكيم)": "Malaysia (JAKIM)", "إندونيسيا (وزارة الشؤون الدينية)": "Indonesia (Ministry of Religious Affairs)",
    "لشبونة (الجالية الإسلامية)": "Lisbon (Islamic Community)", "لجنة رصد الأهلّة (Moonsighting)": "Moonsighting Committee",
    "جامعة طهران (معهد الجيوفيزياء)": "University of Tehran (Institute of Geophysics)", "الجعفرية (قم)": "Shia Ithna-Ashari (Qum)",
    "مدة العدّ التصاعدي بعد دخول الوقت (بالدقائق)": "Count-up duration after the time begins (minutes)",
    "تفعيل الإشعارات": "Enable notifications",
    "الدقائق قبل الوقت (بإشارة سالبة) أو بعده، تفصل بينها فواصل، مثل: -10, 0": "Minutes before (negative) or after the time, separated by commas, e.g. -10, 0",
    # validation errors
    "قيمة غير مدعومة": "Unsupported value", "أدخل أعداداً صحيحة تفصل بينها فواصل": "Enter whole numbers separated by commas",
    "قيمة عددية غير صالحة": "Not a valid number", "يجب أن تكون القيمة بين {0} و{1}": "The value must be between {0} and {1}",
    # notifications
    "حان الآن موعد {0}": "It is now time for {0}", "يتبقى {0} على {1}": "{0} remaining until {1}",
    "مضى على دخول وقت {1} {0}": "{1} began {0} ago",
}


def lang() -> str:
    return get_settings().get("language", "ar")


def is_rtl() -> bool:
    return lang() == "ar"


def tr(text: str, *args, **kw) -> str:
    """`text` in the UI language, with placeholders filled."""
    if lang() == "en": text = EN.get(text, text)
    return text.format(*args, **kw) if args or kw else text


def eastern(settings: dict) -> bool:
    """Eastern Arabic digits and ص/م apply to the Arabic interface only."""
    return settings["eastern_digits"] and settings["language"] == "ar"


def prayer_name(prayer: str) -> str:
    """"صلاة الفجر" for the five prayers, plain names for sunrise and the night divisions."""
    name = tr(PRAYER_LABELS[prayer])
    return tr("صلاة {0}", name) if prayer in FARD else name


def minutes(n: int) -> str:
    """"10 minutes", or the Arabic number-noun agreement: دقيقة واحدة، دقيقتان، 3 دقائق، 11 دقيقة."""
    if lang() == "en": return f"{n} minute" + "s" * (n != 1)
    return "دقيقة واحدة" if n == 1 else "دقيقتان" if n == 2 else f"{n} دقائق" if 3 <= n <= 10 else f"{n} دقيقة"
