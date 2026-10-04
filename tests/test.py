import customtkinter as ctk

app = ctk.CTk()
app.geometry("300x150")

# إنشاء CTkTextbox
textbox = ctk.CTkTextbox(app, width=280, height=100, corner_radius=10)
textbox.pack(pady=20)

# إدخال النص
textbox.insert("1.0", "السطر الأول\nالسطر الثاني")

# الوصول إلى عنصر tk.Text الداخلي وتطبيق تباعد الأسطر
textbox.textbox.tag_configure("spacing", spacing3=8)
textbox.textbox.tag_add("spacing", "1.0", "end")

# قفل التعديل إذا أردت جعله للعرض فقط
textbox.configure(state="disabled")

app.mainloop()
