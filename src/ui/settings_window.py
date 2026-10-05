"""Settings window, generated entirely from src.schema: one tab per section, one row per Setting."""
from typing import Any, Callable, Dict

import customtkinter as ctk

from ..i18n import is_rtl, tr
from ..schema import BY_KEY, SECTIONS, SETTINGS
from ..text import display
from .fields import Field


def _t(text: str, *args) -> str:
    """Translated and, where the platform needs it, shaped for display."""
    return display(tr(text, *args))


class SettingsWindow(ctk.CTkToplevel):
    """`on_save(changes)` gets {key: value} for every setting once all of them validate."""

    def __init__(self, master, settings: Dict[str, Any], on_save: Callable[[Dict[str, Any]], None]):
        super().__init__(master)
        self.on_save, self.fields = on_save, {}
        rtl = is_rtl()
        label_col, field_col, anchor = (1, 0, "e") if rtl else (0, 1, "w")  # RTL: labels on the right, controls on the left
        self.title(tr("الإعدادات"))  # OS-drawn title bar: no display()
        self.geometry("620x540")
        self.transient(master)
        font = ctk.CTkFont(size=max(13, round(settings["font_size"] * 0.65)))
        hint_font = ctk.CTkFont(size=max(11, round(settings["font_size"] * 0.5)))

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True, padx=12, pady=(0, 6))
        for section, title in SECTIONS:
            body = ctk.CTkScrollableFrame(tabs.add(_t(title)), fg_color="transparent")
            body.pack(fill="both", expand=True)
            body.grid_columnconfigure(label_col, weight=1)
            for row, setting in enumerate(s for s in SETTINGS if s.section == section):
                self.fields[setting.key] = field = Field(body, setting, settings[setting.key], font)
                field.widget.grid(row=row, column=field_col, padx=8, pady=8, sticky="w" if rtl else "e")
                text = ctk.CTkFrame(body, fg_color="transparent")
                text.grid(row=row, column=label_col, padx=8, pady=4, sticky=anchor)
                ctk.CTkLabel(text, text=_t(setting.label), font=font, anchor=anchor).pack(anchor=anchor)
                if setting.hint: ctk.CTkLabel(text, text=_t(setting.hint), font=hint_font, text_color="gray", anchor=anchor).pack(anchor=anchor)

        self.error = ctk.CTkLabel(self, text="", text_color="#E5484D", font=font)
        self.error.pack(padx=12)
        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkButton(buttons, text=_t("حفظ"), font=font, command=self.save).pack(side="right", padx=4)
        ctk.CTkButton(buttons, text=_t("إلغاء"), font=font, fg_color="gray", command=self.destroy).pack(side="right", padx=4)
        ctk.CTkButton(buttons, text=_t("استعادة الإعدادات الافتراضية"), font=font, fg_color="transparent", border_width=1,
                      text_color=("black", "white"), command=self.reset).pack(side="left", padx=4)
        self.after(150, lambda: self.winfo_exists() and self.grab_set())  # modal, once the window is mapped

    def save(self) -> None:
        changes = {}
        for key, field in self.fields.items():
            try: changes[key] = field.get()
            except ValueError as e:
                self.error.configure(text=_t("{0}: {1}", tr(BY_KEY[key].label), tr(*e.args)))
                return
        self.on_save(changes)
        self.destroy()

    def reset(self) -> None:
        """Put every field back to its default (nothing is saved until Save)."""
        for key, field in self.fields.items(): field.set(BY_KEY[key].default)
