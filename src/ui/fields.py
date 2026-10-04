"""One input widget per Setting kind, behind a uniform get()/set()."""
import customtkinter as ctk

from ..schema import Setting
from ..text import display


class Field:
    """Widget for `setting`. get() returns the coerced value or raises ValueError (message is user-facing)."""

    def __init__(self, parent, setting: Setting, value, font=None):
        self.setting = setting
        if setting.kind == "bool":
            self.var = ctk.BooleanVar()
            self.widget = ctk.CTkSwitch(parent, text="", variable=self.var, width=50)
        elif setting.kind == "choice":
            self.var, self._shown = ctk.StringVar(), {value: display(label) for value, label in setting.choices}  # value -> shown text
            self.widget = ctk.CTkOptionMenu(parent, values=list(self._shown.values()), variable=self.var, font=font, dropdown_font=font)
        else:
            self.var = ctk.StringVar()
            self.widget = ctk.CTkEntry(parent, textvariable=self.var, width=170, font=font)
        self.set(value)

    def set(self, value) -> None:
        kind = self.setting.kind
        if kind == "bool": self.var.set(bool(value))
        elif kind == "choice": self.var.set(self._shown.get(value, next(iter(self._shown.values()))))
        elif kind == "ints": self.var.set(", ".join(map(str, value)))
        else: self.var.set("" if value is None else str(value))

    def get(self):
        raw = self.var.get()
        if self.setting.kind == "choice":
            raw = next((value for value, shown in self._shown.items() if shown == raw), None)
        return self.setting.coerce(raw)
