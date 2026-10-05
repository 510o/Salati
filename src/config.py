from pathlib import Path

APP_NAME = "صلاتي"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path.home() / f".{APP_NAME.lower()}"
SETTINGS_PATH = DATA_DIR / "settings.json"
ASSETS_DIR = PROJECT_ROOT / "assets"

# prayer identifiers (Aladhan keys), in daily order; the last three are the night divisions
PRAYER_ORDER = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha", "Firstthird", "Midnight", "Lastthird"]
MAIN_PRAYERS = PRAYER_ORDER[:6]  # shown as cards on the main window
FARD = ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha")  # the five obligatory prayers ("صلاة" is said only of these)

# Arabic source texts; src/i18n.py translates them
PRAYER_LABELS = {
    "Fajr": "الفجر", "Sunrise": "الشروق", "Dhuhr": "الظهر", "Asr": "العصر", "Maghrib": "المغرب", "Isha": "العشاء",
    "Firstthird": "الثلث الأول من الليل", "Midnight": "منتصف الليل", "Lastthird": "الثلث الأخير من الليل",
}
WEEKDAYS = {  # keyed by Aladhan's English gregorian weekday
    "Sunday": "الأحد", "Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء",
    "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت",
}
HIJRI_MONTHS = {
    1: "محرم", 2: "صفر", 3: "ربيع الأول", 4: "ربيع الآخر", 5: "جمادى الأولى", 6: "جمادى الآخرة",
    7: "رجب", 8: "شعبان", 9: "رمضان", 10: "شوال", 11: "ذو القعدة", 12: "ذو الحجة",
}
