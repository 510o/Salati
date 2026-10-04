import unittest

from src.config import PRAYER_ORDER
from src.schema import BY_KEY, SECTIONS, SETTINGS, defaults, merged


class Schema(unittest.TestCase):
    def test_definitions_are_consistent(self):
        self.assertEqual(len(BY_KEY), len(SETTINGS))                              # unique keys
        self.assertTrue({s.section for s in SETTINGS} <= {k for k, _ in SECTIONS})
        for s in SETTINGS: self.assertEqual(s.coerce(s.default), s.default, s.key)  # every default is valid
        for p in PRAYER_ORDER: self.assertIn(f"notify_{p}", BY_KEY)

    def test_defaults_do_not_share_mutable_state(self):
        a, b = defaults(), defaults()
        a["notify_Fajr"].append(99)
        self.assertEqual(b["notify_Fajr"], [0])

    def test_coerce(self):
        self.assertEqual(BY_KEY["font_size"].coerce("24"), 24)
        self.assertEqual(BY_KEY["notify_Fajr"].coerce("-10, 0،5"), [-10, 0, 5])
        self.assertEqual(BY_KEY["notify_Fajr"].coerce(""), [])
        self.assertEqual(BY_KEY["time_format"].coerce(24), 24)
        self.assertIsNone(BY_KEY["latitude"].coerce(""))
        self.assertEqual(BY_KEY["latitude"].coerce("30.5"), 30.5)
        self.assertIsNone(BY_KEY["method"].coerce(None))
        self.assertEqual(BY_KEY["method"].coerce(0), 0)  # 0 is a real method, not "unset"

    def test_coerce_rejects_bad_input(self):
        for key, bad in (("font_size", "abc"), ("font_size", 5), ("latitude", "91"), ("notify_Fajr", "a,b"), ("time_format", 7), ("theme", "red")):
            with self.assertRaises(ValueError, msg=f"{key}={bad!r}"): BY_KEY[key].coerce(bad)

    def test_merged_keeps_valid_values_and_heals_invalid_ones(self):
        out = merged({"font_size": 30, "theme": "red", "time_format": 24, "legacy_key": 1})
        self.assertEqual((out["font_size"], out["theme"], out["time_format"]), (30, "system", 24))  # invalid theme -> default
        self.assertEqual(out["legacy_key"], 1)                                                      # unknown keys survive
        self.assertEqual(out["eastern_digits"], True)                                               # new options get defaults


if __name__ == "__main__":
    unittest.main()
