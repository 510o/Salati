import unittest
from unittest.mock import patch

from src import text

SAMPLE = "الثلث الأول"


def mode(value, platform="linux"):
    """Patch the settings and platform seen by src.text."""
    return patch.multiple(text, get_settings=lambda: {"arabic": value}, platform=platform)


class Display(unittest.TestCase):
    def test_auto_processes_on_windows_and_linux(self):
        for system in ("win32", "linux"):
            with mode("auto", system): self.assertNotEqual(text.display(SAMPLE), SAMPLE)
        with mode("auto", "darwin"): self.assertEqual(text.display(SAMPLE), SAMPLE)

    def test_explicit_modes_ignore_platform(self):
        with mode("on", "darwin"): self.assertEqual(text.display(SAMPLE), text.render(SAMPLE))
        with mode("off", "win32"): self.assertEqual(text.display(SAMPLE), SAMPLE)

    def test_english_is_never_processed(self):
        with patch.multiple(text, get_settings=lambda: {"arabic": "on", "language": "en"}, platform="win32"):
            self.assertEqual(text.display("Fajr"), "Fajr")

    def test_missing_setting_defaults_to_auto(self):
        with patch.multiple(text, get_settings=dict, platform="darwin"): self.assertEqual(text.display(SAMPLE), SAMPLE)
        with patch.multiple(text, get_settings=dict, platform="win32"): self.assertNotEqual(text.display(SAMPLE), SAMPLE)

    def test_render_pipeline(self):
        self.assertEqual(text.render("الفجر"), "ﺮﺠﻔﻟﺍ")                       # shaped + reversed
        self.assertEqual(text.render("الفجر الظهر", width=6).count("\n"), 1)    # wrapped
        self.assertTrue(text.render("الفجر", width=8, align=True).startswith("   "))

    def test_hamza_and_lam_alef_are_presentation_forms(self):
        self.assertEqual(text.render("لا"), "ﻻ")                 # isolated lam-alef ligature
        self.assertIn("ﻼ", text.render("صلاتي"))                 # final ligature after a joining letter
        self.assertIn("ﻹ", text.render("الإعدادات"))             # lam + alef with hamza below
        for word in ("إلغاء", "العشاء", "شيء"): self.assertNotIn("ء", text.render(word), word)

    def test_diacritics_are_dropped_from_display_only(self):
        self.assertEqual(text.render("تبعاً"), text.render("تبعا"))
        with mode("on"): self.assertNotEqual(text.display("تبعاً"), "تبعاً")
        self.assertEqual(len("تبعاً"), 5)  # the stored/original text keeps its tanween

    def test_non_string_input(self):
        with mode("off"): self.assertEqual(text.display(12), "12")


if __name__ == "__main__":
    unittest.main()
