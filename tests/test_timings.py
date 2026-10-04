import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from requests import ConnectionError as NetworkDown

from src import timings
from src.schema import defaults

TODAY = date(2026, 10, 5)
API = {
    "timings": {"Fajr": "05:24 (EET)", "Dhuhr": "12:44", "Sunset": "18:36", "Imsak": "05:14", "Midnight": "00:43"},
    "date": {"hijri": {"day": "24", "month": {"number": 4}, "year": "1448"}, "gregorian": {"weekday": {"en": "Monday"}}},
}


class CurrentDay(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.net = {"fetches": [], "locates": 0, "down": False}

        def get_timings(lat, lon, method=None, date=None):
            if self.net["down"]: raise NetworkDown()
            self.net["fetches"].append((lat, lon, method, date))
            return API

        def locate():
            self.net["locates"] += 1
            if self.net["down"]: raise NetworkDown()
            return (30.04, 31.23)

        for target in (patch.object(timings, "CACHE_PATH", Path(self.tmp.name) / "timings.json"),
                       patch.object(timings.api, "get_timings", get_timings), patch.object(timings.api, "locate", locate)):
            target.start(); self.addCleanup(target.stop)

    def day(self, today=TODAY, **settings):
        return timings.current_day({**defaults(), **settings}, today)

    def test_fetch_normalizes_and_filters(self):
        day = self.day()
        self.assertEqual(day["timings"], {"Fajr": "05:24", "Dhuhr": "12:44", "Midnight": "00:43"})  # no suffix, no Imsak/Sunset
        self.assertEqual((day["hijri"], day["weekday"], day["date"]), ({"day": 24, "month": 4, "year": 1448}, "Monday", "2026-10-05"))
        self.assertEqual(self.net["fetches"], [(30.04, 31.23, None, "05-10-2026")])  # explicit date in DD-MM-YYYY

    def test_cache_is_reused_until_the_day_or_settings_change(self):
        self.day(); self.day()
        self.assertEqual(len(self.net["fetches"]), 1)
        self.day(method=3)
        self.assertEqual(len(self.net["fetches"]), 2)                       # method is part of the cache key
        self.day(today=date(2026, 10, 6), method=3)
        self.assertEqual(len(self.net["fetches"]), 3)                       # next day

    def test_manual_location_skips_ip_lookup(self):
        self.day(auto_location=False, latitude=21.4, longitude=39.8, method=0)
        self.assertEqual(self.net["locates"], 0)
        self.assertEqual(self.net["fetches"][0][:3], (21.4, 39.8, 0))       # method 0 is sent, not dropped

    def test_manual_without_coordinates_falls_back_to_ip(self):
        self.day(auto_location=False)
        self.assertEqual(self.net["locates"], 1)

    def test_offline_serves_stale_cache_then_nothing(self):
        self.net["down"] = True
        self.assertIsNone(self.day())                                       # nothing cached and offline
        self.net["down"] = False
        self.day(today=date(2026, 10, 4))                                   # online: caches yesterday
        self.net["down"] = True
        stale = self.day()                                                  # a day later, offline
        self.assertTrue(stale["stale"])
        self.assertEqual(stale["date"], "2026-10-04")


if __name__ == "__main__":
    unittest.main()
