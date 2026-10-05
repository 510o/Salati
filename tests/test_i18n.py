import re
import unittest
from unittest.mock import patch

from src import i18n, notifier
from src.config import HIJRI_MONTHS, PRAYER_LABELS, WEEKDAYS
from src.schema import SECTIONS, SETTINGS

ARABIC = re.compile("[؀-ۿ]")
LANGUAGE_NAMES = {"العربية"}  # shown in their own language in both interfaces


def language(code):
    return patch("src.i18n.get_settings", lambda: {"language": code})


def source_texts():
    """Every Arabic text the schema and config tables hand to the UI."""
    texts = set(PRAYER_LABELS.values()) | set(WEEKDAYS.values()) | set(HIJRI_MONTHS.values()) | {t for _, t in SECTIONS}
    for s in SETTINGS:
        texts |= {s.label, s.hint} | {label for _, label in s.choices}
    return {t for t in texts if ARABIC.search(t)} - LANGUAGE_NAMES


class Translation(unittest.TestCase):
    def test_every_source_text_has_an_english_translation(self):
        self.assertEqual(sorted(t for t in source_texts() if t not in i18n.EN), [])

    def test_translations_contain_no_arabic_letters(self):
        self.assertEqual([k for k, v in i18n.EN.items() if ARABIC.search(v) and v not in ("العربية",) and "ص/م" not in v], [])

    def test_translations_keep_their_placeholders(self):
        for key, value in i18n.EN.items():
            self.assertEqual(sorted(re.findall(r"\{\w*\}", key)), sorted(re.findall(r"\{\w*\}", value)), key)

    def test_tr(self):
        with language("ar"):
            self.assertEqual(i18n.tr("الفجر"), "الفجر")
            self.assertEqual(i18n.tr("يتبقى {0} على {1}", "5 دقائق", "الظهر"), "يتبقى 5 دقائق على الظهر")
        with language("en"):
            self.assertEqual(i18n.tr("الفجر"), "Fajr")
            self.assertEqual(i18n.tr("يتبقى {0} على {1}", "5 minutes", "Dhuhr"), "5 minutes remaining until Dhuhr")
            self.assertEqual(i18n.tr("نص غير مترجم"), "نص غير مترجم")  # unknown text falls back to the source

    def test_digits_and_direction_follow_language(self):
        s = {"eastern_digits": True, "language": "en"}
        self.assertFalse(i18n.eastern(s))
        self.assertTrue(i18n.eastern({**s, "language": "ar"}))
        with language("en"): self.assertFalse(i18n.is_rtl())
        with language("ar"): self.assertTrue(i18n.is_rtl())


class Minutes(unittest.TestCase):
    def test_arabic_number_noun_agreement(self):
        with language("ar"):
            self.assertEqual([i18n.minutes(n) for n in (1, 2, 3, 10, 11, 15, 30)],
                             ["دقيقة واحدة", "دقيقتان", "3 دقائق", "10 دقائق", "11 دقيقة", "15 دقيقة", "30 دقيقة"])

    def test_english(self):
        with language("en"): self.assertEqual([i18n.minutes(1), i18n.minutes(10)], ["1 minute", "10 minutes"])


class EnglishNotifications(unittest.TestCase):
    def test_messages(self):
        with language("en"):
            self.assertEqual(notifier.message("Fajr", 0), ("Fajr prayer", "It is now time for Fajr prayer"))
            self.assertEqual(notifier.message("Asr", -10)[1], "10 minutes remaining until Asr prayer")
            self.assertEqual(notifier.message("Isha", 1)[1], "Isha prayer began 1 minute ago")
            self.assertEqual(notifier.message("Lastthird", 0)[0], "Last third of the night")


if __name__ == "__main__":
    unittest.main()
