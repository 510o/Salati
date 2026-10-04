"""Main window: date, countdown to (or since) the current prayer, and the day's prayer times."""
import threading
import tkinter as tk
from datetime import date
from queue import SimpleQueue
from time import monotonic
from typing import Callable, Optional

import customtkinter as ctk

from ..config import APP_NAME, ASSETS_DIR, HIJRI_MONTHS, MAIN_PRAYERS, PRAYER_LABELS, PRAYER_ORDER, WEEKDAYS
from ..prayer_logic import countdown
from ..storage import get_settings, update_settings
from ..text import display
from ..time_utils import format_clock, format_hms, parse_time, to_eastern_digits
from ..timings import current_day
from .settings_window import SettingsWindow

TICK_MS, RETRY_SECONDS = 250, 300  # UI refresh period; wait before retrying a failed/stale fetch
ACCENT = ("#3B8ED0", "#1F6AA5")
LOCATION_KEYS = ("auto_location", "latitude", "longitude", "method")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings, self.day, self.times = get_settings(), None, {}
        self.on_change: Optional[Callable[[], None]] = None  # called when times or notification settings changed
        self._results, self._seq, self._retry_at, self._settings_window = SimpleQueue(), 0, 0.0, None  # _results: (seq, day) from fetch threads
        self.title(display(APP_NAME))
        self._timers = [self.after(250, self._set_icon)]  # CTk installs its own icon shortly after start-up on Windows
        self.build()
        self.refresh()
        self._timers.append(self.after(TICK_MS, self.tick))

    def destroy(self) -> None:
        for timer in self._timers: self.after_cancel(timer)
        super().destroy()

    # ---- layout -------------------------------------------------------------------------------------------
    def _set_icon(self) -> None:
        try: self._icon = tk.PhotoImage(file=str(ASSETS_DIR / "icon.png")); self.iconphoto(True, self._icon)
        except tk.TclError: pass

    def build(self) -> None:
        """(Re)create all widgets from the current settings."""
        size = self.settings["font_size"]
        ctk.set_appearance_mode(self.settings["theme"])
        for child in self.winfo_children(): child.destroy()
        font, pad = (lambda k=1: ctk.CTkFont(size=round(size * k))), round(size * 0.5)
        self._shown, self._active = {}, None

        top = ctk.CTkFrame(self)
        top.pack(side="top", fill="x", padx=pad, pady=pad)
        box = round(size * 1.5)
        ctk.CTkButton(top, text="⚙", font=font(.75), width=box, height=box, corner_radius=box, command=self.open_settings).pack(side="left", padx=pad, pady=pad)
        self.date_label = ctk.CTkLabel(top, font=font(), text="", padx=pad)
        self.date_label.pack(side="right")

        row = ctk.CTkFrame(self)
        row.pack(side="bottom", fill="x", padx=pad, pady=pad)
        self.cards = {}
        for prayer in MAIN_PRAYERS:  # Fajr rightmost
            card = ctk.CTkFrame(row)
            self._card_color = card.cget("fg_color")
            card.pack(side="right", fill="y", expand=True, padx=pad // 2, pady=pad // 2)
            ctk.CTkLabel(card, text=display(PRAYER_LABELS[prayer]), font=font(), padx=pad).pack()
            time_label = ctk.CTkLabel(card, text="", font=font(), padx=pad)
            time_label.pack()
            self.cards[prayer] = (card, time_label)

        center = ctk.CTkFrame(self)
        center.pack(fill="both", expand=True, padx=pad)
        inner = ctk.CTkFrame(center)
        inner.pack(expand=True, padx=pad, pady=pad)
        self.name_label = ctk.CTkLabel(inner, text="", font=font(1.5), padx=size)
        self.caption_label = ctk.CTkLabel(inner, text="", font=font(.75), text_color="gray")
        self.count_label = ctk.CTkLabel(inner, text="", font=font(1.5), padx=size)
        self.status_label = ctk.CTkLabel(center, text="", font=font(.6), text_color="gray")
        for label in (self.name_label, self.caption_label, self.count_label): label.pack()
        self.status_label.pack(pady=(0, pad))

        self.wm_geometry("")  # fit the new content (CTk's geometry() can't take ""), then forbid shrinking below it
        self.update_idletasks()
        self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())
        self.render()

    def _set(self, label: ctk.CTkLabel, text: str) -> None:
        shown = display(text)
        if self._shown.get(label) != shown:
            label.configure(text=shown)
            self._shown[label] = shown

    # ---- content ------------------------------------------------------------------------------------------
    def _digits(self, text: str) -> str:
        return to_eastern_digits(text) if self.settings["eastern_digits"] else text

    def render(self) -> None:
        """Content that only changes with the day's data or settings."""
        s, day = self.settings, self.day
        if day:
            h = day["hijri"]
            self._set(self.date_label, self._digits(f"{WEEKDAYS.get(day['weekday'], '')} {h['day']} {HIJRI_MONTHS[h['month']]} {h['year']}"))
        else: self._set(self.date_label, "--")
        for prayer, (_, label) in self.cards.items():
            t = parse_time(self.times.get(prayer))
            self._set(label, format_clock(t, s["time_format"] == 12, s["eastern_digits"]) if t else "--:--")
        status = "لا تتوفر مواقيت، تحقق من الاتصال" if not day else "مواقيت محفوظة، تعذّر التحديث" if day.get("stale") else ""
        self._set(self.status_label, status)
        self.update_countdown()

    def update_countdown(self) -> None:
        s = self.settings
        state = countdown(self.times, PRAYER_ORDER if s["night_times"] else MAIN_PRAYERS, elapsed_minutes=s["elapsed_minutes"])
        if state:
            name, caption, count = PRAYER_LABELS[state["name"]], "مضى منذ دخول الوقت" if state["elapsed"] else "المتبقي", self._digits(format_hms(state["seconds"]))
        else: name, caption, count = "--", "", self._digits("--:--:--")
        for label, text in ((self.name_label, name), (self.caption_label, caption), (self.count_label, count)): self._set(label, text)
        active = state["name"] if state else None
        if active != self._active:
            for prayer, (card, _) in self.cards.items(): card.configure(fg_color=ACCENT if prayer == active else self._card_color)
            self._active = active

    # ---- data ---------------------------------------------------------------------------------------------
    def refresh(self) -> None:
        """Fetch/cached-load today's timings off the UI thread; tick() applies the newest result."""
        self._seq += 1
        seq, settings = self._seq, dict(self.settings)
        self._retry_at = monotonic() + RETRY_SECONDS
        def work():
            try: self._results.put((seq, current_day(settings)))
            except Exception as e: print(f"timings failed: {e}"); self._results.put((seq, None))
        threading.Thread(target=work, daemon=True).start()

    def _needs_refresh(self) -> bool:
        fresh = self.day and not self.day.get("stale") and self.day["date"] == date.today().isoformat()
        return not fresh and monotonic() >= self._retry_at

    def tick(self) -> None:
        latest = None
        while not self._results.empty():  # results of superseded refreshes (older seq) are dropped
            seq, day = self._results.get_nowait()
            if seq == self._seq: latest = (day,)
        if latest:
            self.day = latest[0] or self.day
            self.times = self.day["timings"] if self.day else {}
            self.render()
            if self.on_change: self.on_change()
        elif self._needs_refresh(): self.refresh()
        self.update_countdown()
        self._timers[-1] = self.after(TICK_MS, self.tick)  # keep the latest id so destroy() can cancel it

    # ---- settings -----------------------------------------------------------------------------------------
    def open_settings(self) -> None:
        if self._settings_window and self._settings_window.winfo_exists(): self._settings_window.focus(); return
        self._settings_window = SettingsWindow(self, self.settings, self.apply_settings)

    def apply_settings(self, changes: dict) -> None:
        old, self.settings = self.settings, update_settings(changes)
        self.build()
        if any(old[k] != self.settings[k] for k in LOCATION_KEYS): self.refresh()
        if self.on_change: self.on_change()
