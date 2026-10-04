"""Visual check of Arabic rendering on this OS. Run: python tests/render_check.py
For each sample the first row is the raw text, the second is src.text.render(). The right one is the row that
reads correctly (right-to-left, letters joined, lam-alef ligatures). Report which one per OS -> that is the "auto" rule."""
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
