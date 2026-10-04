import threading
import unittest
from datetime import datetime, time, timedelta
from unittest.mock import patch

from src import notifier
from src.config import MAIN_PRAYERS, PRAYER_ORDER
from src.prayer_logic import countdown, next_notification
from src.time_utils import format_clock

TIMES = {"Fajr": "05:00", "Sunrise": "06:30", "Dhuhr": "12:00", "Asr": "15:30", "Maghrib": "18:00", "Isha": "19:30", "Midnight": "00:43"}
at = lambda h, m=0: datetime(2026, 10, 5, h, m)


class Countdown(unittest.TestCase):
    def test_counts_down_to_next_prayer(self):
        self.assertEqual(countdown(TIMES, MAIN_PRAYERS, at(10)), {"name": "Dhuhr", "seconds": 7200, "elapsed": False})

    def test_counts_up_shortly_after_a_prayer(self):
        self.assertEqual(countdown(TIMES, MAIN_PRAYERS, at(12, 20)), {"name": "Dhuhr", "seconds": 1200, "elapsed": True})
        self.assertEqual(countdown(TIMES, MAIN_PRAYERS, at(12, 40))["name"], "Asr")  # past the 35 min window
        self.assertFalse(countdown(TIMES, MAIN_PRAYERS, at(12, 20), elapsed_minutes=0)["elapsed"])

    def test_wraps_around_midnight(self):
        self.assertEqual(countdown(TIMES, MAIN_PRAYERS, at(23))["seconds"], 6 * 3600)   # tomorrow's Fajr
        self.assertEqual(countdown(TIMES, MAIN_PRAYERS, at(4)), {"name": "Fajr", "seconds": 3600, "elapsed": False})

    def test_night_times_only_when_requested(self):
        self.assertEqual(countdown(TIMES, PRAYER_ORDER, at(23, 50))["name"], "Midnight")
        self.assertEqual(countdown(TIMES, MAIN_PRAYERS, at(23, 50))["name"], "Fajr")

    def test_no_valid_times(self):
        self.assertIsNone(countdown({}, PRAYER_ORDER, at(10)))
        self.assertIsNone(countdown({"Fajr": "garbage"}, PRAYER_ORDER, at(10)))


class NextNotification(unittest.TestCase):
    RULES = {"Fajr": [-10, 0], "Isha": [0]}

    def test_picks_earliest_offset(self):
        self.assertEqual(next_notification(TIMES, self.RULES, at(4, 45)), (at(4, 50), "Fajr", -10))
        self.assertEqual(next_notification(TIMES, self.RULES, at(4, 51)), (at(5), "Fajr", 0))

    def test_strictly_after_now_and_wraps(self):
        self.assertEqual(next_notification(TIMES, self.RULES, at(4, 50))[0], at(5))
        self.assertEqual(next_notification(TIMES, self.RULES, at(20)), (at(4, 50) + timedelta(days=1), "Fajr", -10))

    def test_offset_after_prayer(self):
        self.assertEqual(next_notification(TIMES, {"Dhuhr": [15]}, at(12, 5)), (at(12, 15), "Dhuhr", 15))

    def test_nothing_scheduled(self):
        self.assertIsNone(next_notification(TIMES, {}, at(10)))
        self.assertIsNone(next_notification(TIMES, {"Fajr": []}, at(10)))
        self.assertIsNone(next_notification({}, self.RULES, at(10)))


class FormatClock(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(format_clock(time(17, 5)), "٥:٠٥ م")
        self.assertEqual(format_clock(time(17, 5), eastern=False), "5:05 PM")
        self.assertEqual(format_clock(time(17, 5), hour12=False), "١٧:٠٥")
        self.assertEqual(format_clock(time(0, 7)), "١٢:٠٧ ص")
        self.assertEqual(format_clock(time(12, 0), eastern=False), "12:00 PM")


class Notifier(unittest.TestCase):
    def test_messages(self):
        self.assertEqual(notifier.message("Fajr", 0), ("وقت الفجر", "حان الآن وقت الفجر"))
        self.assertEqual(notifier.message("Fajr", -10)[1], "بقي 10 دقيقة على الفجر")
        self.assertEqual(notifier.message("Fajr", 15)[1], "مضت 15 دقيقة على الفجر")

    def test_thread_fires_a_due_event_once_and_stops(self):
        fired, done = [], threading.Event()
        due = iter([(datetime.now() + timedelta(seconds=0.4), "Dhuhr", 0)])
        settings = {"notifications": True, **{f"notify_{p}": [0] for p in PRAYER_ORDER}}
        sender = lambda title, text: (fired.append((title, text)), done.set())
        with patch.object(notifier, "get_settings", lambda: settings), patch.object(notifier, "next_notification", lambda *a: next(due, None)):
            worker = notifier.Notifier(lambda: TIMES, sender)
            worker.start()
            self.assertTrue(done.wait(5), "notification never fired")
            worker.stop(); worker.join(3)
        self.assertEqual(fired, [("وقت الظهر", "حان الآن وقت الظهر")])
        self.assertFalse(worker.is_alive())


if __name__ == "__main__":
    unittest.main()
