"""Application wiring: single-instance lock, main window, background notifier."""
from .instance import acquire_instance_lock
from .notifier import Notifier
from .ui import MainWindow


def run() -> None:
    lock = acquire_instance_lock()
    if lock is None:
        print("Salati is already running.")
        return
    window = MainWindow()
    notifier = Notifier(lambda: window.times)
    window.on_change = notifier.wake  # new times or notification settings -> reschedule now
    notifier.start()
    try: window.mainloop()
    finally:
        notifier.stop()
        lock.close()
