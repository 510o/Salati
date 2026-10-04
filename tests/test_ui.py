"""Smoke test: builds the real windows (hidden). Skipped when there is no display."""
import json
import tempfile
import tkinter
import unittest
from pathlib import Path
from time import sleep, monotonic
from unittest.mock import patch

from src import storage
from src.text import display

DAY = {
    "date": "2026-10-05", "key": [30.04, 31.23, None], "weekday": "Monday", "hijri": {"day": 24, "month": 4, "year": 1448},
    "timings": {"Fajr": "05:24", "Sunrise": "06:51", "Dhuhr": "12:44", "Asr": "16:06", "Maghrib": "18:36", "Isha": "19:53"},
}


def pump(window, until, timeout=5):
    """Run the Tk event loop until `until()` is true."""
    end = monotonic() + timeout
    while not until() and monotonic() < end: window.update(); sleep(0.02)
    return until()


class Windows(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "settings.json"
        for p in (patch.object(storage, "SETTINGS_PATH", self.path), patch.object(storage, "_cache", None),
                  patch("src.ui.main_window.current_day", return_value=DAY)):
            p.start(); self.addCleanup(p.stop)
        try:
            from src.ui import MainWindow
            self.window = MainWindow()
        except tkinter.TclError as e:
            self.skipTest(f"no display: {e}")
        self.window.withdraw()
        self.addCleanup(self.window.destroy)

    def test_shows_loaded_day(self):
        self.assertTrue(pump(self.window, lambda: self.window.times))
        self.assertEqual(self.window.times, DAY["timings"])
        self.assertEqual(self.window.date_label.cget("text"), display("الإثنين ٢٤ ربيع الآخر ١٤٤٨"))
        self.assertEqual(self.window.cards["Fajr"][1].cget("text"), display("٥:٢٤ ص"))
        self.assertNotEqual(self.window.count_label.cget("text"), display("--:--:--"))  # countdown is running

    def test_settings_window_saves_and_rebuilds(self):
        pump(self.window, lambda: self.window.times)
        self.window.open_settings()
        win = self.window._settings_window
        win.update()
        win.fields["eastern_digits"].set(False)
        win.fields["time_format"].set(24)
        win.fields["notify_Fajr"].set([-10, 0])
        win.save()
        saved = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual((saved["eastern_digits"], saved["time_format"], saved["notify_Fajr"]), (False, 24, [-10, 0]))
        self.assertEqual(self.window.cards["Fajr"][1].cget("text"), "05:24")                 # window rebuilt with new format
        self.assertEqual(self.window.date_label.cget("text"), display("الإثنين 24 ربيع الآخر 1448"))

    def test_invalid_input_keeps_window_open_and_saves_nothing(self):
        self.window.open_settings()
        win = self.window._settings_window
        win.fields["font_size"].set("abc")
        win.save()
        self.assertTrue(win.winfo_exists())
        self.assertNotEqual(win.error.cget("text"), "")
        self.assertFalse(self.path.exists())

    def test_reset_restores_defaults_without_saving(self):
        self.window.open_settings()
        win = self.window._settings_window
        win.fields["font_size"].set(30)
        win.reset()
        self.assertEqual(win.fields["font_size"].get(), 20)
        self.assertFalse(self.path.exists())


if __name__ == "__main__":
    unittest.main()
