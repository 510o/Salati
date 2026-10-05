"""Visual check of Arabic rendering on this OS. Run: python tests/render_check.py
For each sample the first row is the raw text, the second is src.text.render(). The right one is the row that
reads correctly (first word at the right, letters joined). Windows and Linux need the second row; the OS where the
raw row is right should be left out of the "auto" rule in src/text.py (macOS is assumed raw and still unverified)."""
import sys
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.text import render

SAMPLES = ["الفجر", "الثلث الأول", "لا إله إلا الله", "١٤٤٧ رجب ٢  الجمعة", "٥:٣٠ م", "الثلث الآخر من الليل يبدأ بعد منتصف الليل بساعات"]

root = tk.Tk()
root.title(f"render check - {sys.platform}")
for i, sample in enumerate(SAMPLES):
    for j, (label, text) in enumerate((("raw", sample), ("render()", render(sample)))):
        tk.Label(root, text=label, width=9, fg="gray").grid(row=2 * i + j, column=0)
        tk.Label(root, text=text, font=("", 20), anchor="e", justify="right", width=26).grid(row=2 * i + j, column=1)
root.mainloop()
