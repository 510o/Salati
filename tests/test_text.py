import unittest
from unittest.mock import patch

from src import text

SAMPLE = "الثلث الأول"


def mode(value, platform="linux"):
    """Patch the settings and platform seen by src.text."""
    return patch.multiple(text, get_settings=lambda: {"arabic": value}, platform=platform)


class Display(unittest.TestCase):
    def test_auto_processes_on_linux_only(self):
        with mode("auto", "linux"): self.assertNotEqual(text.display(SAMPLE), SAMPLE)
        for other in ("win32", "darwin"):
            with mode("auto", other): self.assertEqual(text.display(SAMPLE), SAMPLE)

    def test_explicit_modes_ignore_platform(self):
        with mode("on", "win32"): self.assertEqual(text.display(SAMPLE), text.render(SAMPLE))
        with mode("off", "linux"): self.assertEqual(text.display(SAMPLE), SAMPLE)

    def test_missing_setting_defaults_to_auto(self):
        with patch.multiple(text, get_settings=dict, platform="win32"): self.assertEqual(text.display(SAMPLE), SAMPLE)

    def test_render_pipeline(self):
        self.assertEqual(text.render("الفجر"), "ﺮﺠﻔﻟﺍ")                       # shaped + reversed
        self.assertEqual(text.render("الفجر الظهر", width=6).count("\n"), 1)    # wrapped
        self.assertTrue(text.render("الفجر", width=8, align=True).startswith("   "))

    def test_non_string_input(self):
        with mode("off"): self.assertEqual(text.display(12), "12")


if __name__ == "__main__":
    unittest.main()
