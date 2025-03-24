from tkinter import font as fonts # fonts.families())
from plyer import notification # pip install plyer
from requests import get # pip install requests
from prayerutils import *
from settings import *
import tkinter as tk

root, working, size_history = tk.Tk(), True, (); root.title(app_title)
try: root.iconphoto(True, tk.PhotoImage(file=icon_path))
except tk.TclError as e: print(e)

def themes() -> dict:
    try: return {'bg': style,  'fg': 'black' if tuple(value//257 for value in root.winfo_rgb(style))[0] > 130 else 'white'}
    except:
        hex_color = (nearest_prayer(times, prayer_times) or [None, None, None, '#000000'])[3]
        rgb = hex_to_rbg(hex_color)
        lum = int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
        return {'bg': '#' + f'{lum:02x}'*3 if style == "monochrome" else hex_color, 'fg': 'black' if lum > 130 else 'white'}

def notifications(prayer, _, time_left, __):
    def time_out(): global working; working = not working
    if prayer and time_left:
        time = round(time_left/60, 2)
        notifi = next((n for n in notifis.get(prayer, [[()]]) if n[0] == time), None)
        if working and notifi:
            notification.notify( app_name=app_title, title=notifi[1], message=notifi[2], app_icon=app_icon)
            time_out(); root.after(10000, time_out)

def update(event):
    global reupdate_id
    if windows[0] == 'main':
        window_size = event.width, event.height
        if window_size[0] >= root.winfo_width() and window_size[1] >= root.winfo_height():
            if reupdate_id: root.after_cancel(reupdate_id)
            shown_prayer = nearest_prayer(times, prayer_times) or [None, None, None, None]
            x_span = (window_size[0] - sum(width for element in labels.values() for width in element.values()))//(len(labels)+1)
            x_offset, theme = x_span, themes()
            for element in list(labels.values())[::-1]:
                label, time = list(*element.keys())
                element_width = int(*element.values())
                element[(label, time)] = element_width
                time.config(**theme); label.config(**theme)
                time.place(x=x_offset + (element_width-time.winfo_width())//2, y=window_size[1] - font_height)
                label.place(x=x_offset + (element_width-label.winfo_width())//2, y=window_size[1] - font_height*2)
                x_offset += element_width + x_span
            line.place(width=root.winfo_screenwidth(), y=window_size[1] - font_height*2); line.config(bg=theme['fg'])
            y_span = [(window_size[1] - frame_heights[0])//2, (window_size[1] - frame_heights[1])//2, 0]

            time_left_label.config(text=shown_prayer[1] if times else '--:--:--', font=center_font, **theme)
            time_left_label.place(x=(window_size[0] - time_left_label.winfo_width())//2, y=y_span[0])
            shown_prayer_label.config(text=prayer_times[shown_prayer[0]][islinux]  if times else  '--', font=center_font, **theme)
            shown_prayer_label.place(x=(window_size[0] - shown_prayer_label.winfo_width())//2, y=y_span[0] - shown_prayer_label.winfo_height())
            root.config(bg=theme['bg'])
            notifications(*shown_prayer)

            reupdate_id = root.after(100, lambda: update(event))

    elif windows[0] == 'settings': pass

def window():
    global windows, style, reupdate_id, labels, font_height, line, center_font, frame_heights, times, time_left_label, shown_prayer_label, islinux, notifis, size_history
    data = read()
    try: data = edit({'backup': get(f"https://api.aladhan.com/v1/timings?latitude={data['aladhan'][0][0]}&longitude={data['aladhan'][0][1]}{('&method=' + str(data['aladhan'][1])) if data['aladhan'][1] != 'int' else ''}").json()["data"]})
    except: pass # https://aladhan.com/prayer-times-api
    times, notifis, islinux, windows, style, span, reupdate_id = data['backup'].get('timings', {}), data['notifications'], 1 if data['system'] == 'Linux' else 0, ['main', 'settings'], data['style'][data['style'][0]], data['font'][1], None
    theme, labels = themes(), {} # { 'prayer': {('name', 'time'): width} }
    for key in prayer_times:
        if key not in exception_times:
            labels[key] = {(tk.Label(root, text=prayer_times[key][islinux], font=data['font'], **theme), # الصلاة
                tk.Label(root, text=format_time(times.get(key)) if times else '--:--:--', font=data['font'], **theme)): # وقتها
                    int} # عرضها
    line = tk.Frame(root, height=3, bg=theme['fg'])
    center_font = (data['font'][0], str(round(int(data['font'][1])*1.5)))
    time_left_label = tk.Label(root, **theme, font=center_font)
    shown_prayer_label = tk.Label(root, **theme, font=center_font)
    for obj in root.winfo_children(): obj.place(x=0, y=0) # ادراج العناصر
    root.update_idletasks()
    
    x_offset, font_height = span, list(labels['Fajr'].keys())[0][0].winfo_height()
    for element in list(labels.values()):
        label, time = list(*element.keys())
        element_width = max(label.winfo_width(), time.winfo_width())
        element[(label, time)] = element_width
        x_offset += element_width + span
    frame_heights = [font_height*2 + span, time_left_label.winfo_height() + shown_prayer_label.winfo_height() + span, 0]
    min_x, min_y = x_offset, sum(frame_heights)
    root.minsize(min_x, min_y); root.maxsize(root.winfo_screenwidth(), root.winfo_screenheight())
    screen_x, screen_y = (root.winfo_screenwidth() - min_x)//2, (root.winfo_screenheight() - min_y)//2
    
    if screen_x >= 0 and screen_y >= 0:
        root.geometry(f'{root.winfo_reqwidth()}x{root.winfo_reqheight()}+{screen_x}+{screen_y}')
        root.bind("<Configure>", update)
    else:
        if size_history: new_size = int(abs((size_history[0] - screen_x)*root.winfo_screenwidth()/root.winfo_screenheight() + (size_history[1] - screen_y)*root.winfo_screenheight()/root.winfo_screenwidth()))
        else: new_size = data['font'][1] - 1
        size_history = (screen_x, screen_y)
        edit({'font': (data['font'][0], new_size)})
        for obj in root.winfo_children(): obj.destroy()
        root.update(); window()
window(); root.mainloop()