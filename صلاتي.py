from prayerutils import format_time, nearest_prayer
from tkinter import font as fonts # fonts.families())
from plyer import notification # pip install plyer
from requests import get # pip install requests
from settings import *
import tkinter as tk

root, working = tk.Tk(), True; root.title(app_title)
try: root.iconphoto(True, tk.PhotoImage(file=app_icon))
except tk.TclError as e: print(e)

def notifications(prayer, _, time_left):
    def time_out(): global working; working = not working
    if working and notifi.get(prayer, [None])[0] == round(time_left/60, 2):
        notification.notify( app_name=app_title, title=f"وقت {prayer_times[prayer][0]}", message=notifi[prayer][1], app_icon=app_icon)
        time_out(); root.after(60000, time_out)

def update(event):
    global reupdate_id, times
    if windows[0] == 'main':
        window_size = event.width, event.height
        if window_size[0] >= root.winfo_width() and window_size[1] >= root.winfo_height():
            if reupdate_id: root.after_cancel(reupdate_id)
            x_span = (window_size[0] - sum(width for element in labels.values() for width in element.values()))//(len(labels)+1)
            x_offset = x_span
            for element in list(labels.values())[::-1]:
                label, time = list(*element.keys())
                element_width = int(*element.values())
                element[(label, time)] = element_width
                time.place(x=x_offset + (element_width-time.winfo_width())//2, y=window_size[1] - font_height)
                label.place(x=x_offset + (element_width-label.winfo_width())//2, y=window_size[1] - font_height*2)
                x_offset += element_width + x_span
            line.place(width=root.winfo_screenwidth(), y=window_size[1] - font_height*2)
            y_span = [(window_size[1] - frame_heights[0])//2, (window_size[1] - frame_heights[1])//2, 0]

            shown_prayer = nearest_prayer(times, prayer_times) or [None, None, None]
            time_left_label.config(text=shown_prayer[1] if times else '--:--:--', **center_config)
            time_left_label.place(x=(window_size[0] - time_left_label.winfo_width())//2, y=y_span[0])
            shown_prayer_label.config(text=prayer_times[shown_prayer[0]][islinux]  if times else  '--', **center_config)
            shown_prayer_label.place(x=(window_size[0] - shown_prayer_label.winfo_width())//2, y=y_span[0] - shown_prayer_label.winfo_height())
            notifications(*shown_prayer)

            reupdate_id = root.after(100, lambda: update(event))

    elif windows[0] == 'settings': pass

def window(): # تنسيق شاشة العرض
    global font_height, labels, frame_heights
    x_offset, font_height = span, list(labels['Fajr'].keys())[0][0].winfo_height()
    for element in list(labels.values()):
        label, time = list(*element.keys())
        element_width = max(label.winfo_width(), time.winfo_width())
        element[(label, time)] = element_width
        x_offset += element_width + span
    frame_heights = [font_height*2 + span, time_left_label.winfo_height() + shown_prayer_label.winfo_height() + span, 0]
    min_x, min_y = x_offset, sum(frame_heights)
    root.minsize(min_x, min_y); root.maxsize(root.winfo_screenwidth(), root.winfo_screenheight())
    screen_x, screen_y = (root.winfo_screenwidth() - min_x)//2, round((root.winfo_screenheight() - min_y)/2)
    root.geometry(f'{root.winfo_reqwidth()}x{root.winfo_reqheight()}+{screen_x}+{screen_y}')
    root.bind("<Configure>", update)

def main():
    global times, islinux, reupdate_id, notifi, windows, span, labels, line, center_config, time_left_label, shown_prayer_label
    
    data = read()
    try: data = edit({'backup': get(f"https://api.aladhan.com/v1/timings?latitude={data['aladhan'][0][0]}&longitude={data['aladhan'][0][1]}").json()["data"]})
    except: pass # https://aladhan.com/prayer-times-api\
    times, notifi, islinux, reupdate_id = data['backup'].get('timings', {}), data['notifications'], 1 if data['system'] == 'Linux' else 0, None
    windows, font_settings, frame_heights = ['main', 'settings'], data['font'], []
    span = font_settings[0][1]
    root.config(bg='black')
    labels_config, labels = {'font':font_settings[0], 'fg':font_settings[1][0], 'bg':font_settings[1][1]}, {} # { 'prayer': {('name', 'time'): width} }
    for key in prayer_times:
        if key not in exception_times:
            labels[key] = {(tk.Label(root, text=prayer_times[key][islinux], **labels_config), # الصلاة
                tk.Label(root, text=format_time(times.get(key)) if times else '--:--:--', **labels_config)): # وقتها
                    int} # عرضها
    line = tk.Frame(root, height=3, bg=font_settings[1][0])
    center_config = {'fg': font_settings[1][0], 'bg': font_settings[1][1], 'font': (font_settings[0][0], str(round(int(font_settings[0][1])*1.5)))}
    time_left_label = tk.Label(root, **center_config)
    shown_prayer_label = tk.Label(root, **center_config)
    for obj in root.winfo_children(): obj.place(x=0, y=0) # ادراج العناصر
    root.after(200, window)
main(); root.mainloop()