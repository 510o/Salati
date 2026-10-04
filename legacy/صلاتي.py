from prayerutils import *
from settings import *
external_libraries("customtkinter")
import customtkinter as ctk

deduplicate(0)
Popen([executable, notifi_path], stdout=DEVNULL, stderr=DEVNULL)

app, islinux, windows, reupdate_id = ctk.CTk(), platform.startswith("linux")*1, ['main', 'settings'], None
app.maxsize(app.winfo_screenwidth(), app.winfo_screenheight()); app.title(app_name)
try: app.iconphoto(True, PhotoImage(file=icon_path))
except Exception as e: print(e)

#def themes() -> dict:
#    try: return {'bg': style,  'fg': 'black' if tuple(value//257 for value in app.winfo_rgb(style))[0] > 128 else 'white'}
#    except:
#        hex_color = (nearest_prayer(times, prayer_times) or [None, None, None, '#000000'])[3]
#        rgb = hex_to_rgb(hex_color)
#        lum = int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
#        return {'bg': '#' + f'{lum:02x}'*3 if style == "monochrome" else hex_color, 'fg': 'black' if lum > 128 else 'white'}

def update():
    global data, times, date, style
    data = data_manager()
    try:
        data = data_manager(None, {'backup': get('api.aladhan.com', f'/v1/timings?latitude={data["aladhan"]['location'][0]}&longitude={data["aladhan"]['location'][1]}{('&method=' + str(data['aladhan']['method'])) if data['aladhan']['method'] else ''}')["data"]})
        data['alabhan']['method'] = data['backup']['meta']['method']['id']
        data = data_manager(None, {'aladhan': data['aladhan']})
    except: pass
    times, date, style = data['backup'].get('timings', {}), data['backup'].get('date'), data['style'][data['style'][0]]
    if reupdate_id: 
        pass
update()

def layout(event):
    global reupdate_id
    if reupdate_id: app.after_cancel(reupdate_id)
    # update()
    prayer_left = nearest_prayer(times, prayer_times) or [None, None, None] #, None]
    shown_prayer.configure(text=prayer_times[prayer_left[0]][islinux] if prayer_left[0] else '--')
    time_left.configure(text=prayer_left[1] or '--:--:--')
    reupdate_id = app.after(100, lambda: layout(event))

def font(size_factor: int = 1): return (data['font'][0], round(data['font'][1]*size_factor), *data['font'][2:])

upper_frame = ctk.CTkFrame(app)
upper_frame.pack(side="top", fill="x", padx=font(.5)[1], pady=font(.5)[1])
settings_button = ctk.CTkButton(upper_frame, text="⚙", font=font(.75), width=font(1.25)[1], height=font(1.25)[1], corner_radius=font(1.25)[1])
settings_button.pack(side="left", padx=font(.5)[1], pady=font(.5)[1])
date_label = ctk.CTkLabel(upper_frame, font=font(), text=f"{date['hijri']['year']} {months[date['hijri']['month']['number']][islinux]} {date['hijri']['day']}  {days[date['gregorian']['weekday']['en']][islinux]}" if date else "--/--/--  --", padx=font(.5)[1])
date_label.pack(side="right")

lower_frame = ctk.CTkFrame(app)
lower_frame.pack(side="bottom", fill="x", padx=font(.5)[1], pady=font(.5)[1])
labels = {} # { 'prayer': ('name', 'time')}
for key in prayer_times:
    if key not in exception_times:
        labels_frame = ctk.CTkFrame(lower_frame)
        labels[key] = (ctk.CTkLabel(labels_frame, font=font(), text=prayer_times[key][islinux], padx=font(.5)[1]),
                                ctk.CTkLabel(labels_frame, font=font(), text=format_time(times.get(key)) or '--:--', padx=font(.5)[1]))
        labels_frame.pack(side="right", fill="y", padx=font(.5)[1], pady=font(.5)[1], expand=True)
for frame in labels.values(): frame[0].pack(); frame[1].pack()

central_frame = ctk.CTkFrame(app)
central_frame.pack(fill="both", padx=font(.5)[1], expand=True)
labels_frame = ctk.CTkFrame(central_frame); labels_frame.pack(padx=font(.5)[1], pady=font(.5)[1], expand=True)
shown_prayer = ctk.CTkLabel(labels_frame, text="--", padx=font()[1], font=font(1.5))
time_left = ctk.CTkLabel(labels_frame, text="--:--:--", padx=font()[1], font=font(1.5))
shown_prayer.pack(); time_left.pack()

app.update_idletasks()
app.minsize(app.winfo_width(), app.winfo_height())
app.bind("<Configure>", layout)
app.mainloop()