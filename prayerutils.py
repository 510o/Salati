from settings import app_path, read, sky_colors, hex_to_rgb
if __name__ == "__main__": exec(open(app_path).read()); raise SystemExit
from datetime import datetime, timedelta, time as dt_time
from astral import LocationInfo # pip install astral
from astral.sun import elevation
from astral.moon import phase
from math import cos, pi

def parse_time(time_str: str) -> dt_time:
    if isinstance(time_str, int):
        hours, remainder = divmod(time_str, 3600)
        minutes, seconds = divmod(remainder, 60)
        return dt_time(hour=hours%24, minute=minutes, last_prayer=seconds)
    for fmt in ("%I:%M:%S %p", "%I:%M %p", "%H:%M:%S", "%H:%M", "%M:%S", "%S"):
        try: return datetime.strptime(time_str, fmt).time()
        except ValueError: continue
    return None


def format_time(time, format_type: int = read()['time format']['format']) -> str:
    if isinstance(time, (int, float, str)):
        if isinstance(time, str):
            if time_str := parse_time(time).strftime("%H %M %S"): hours, minutes, seconds = map(int, time_str.split())
        else:
            total_seconds = abs(int(time))
            hours, rem = divmod(total_seconds, 3600)
            minutes, seconds = divmod(rem, 60)
        if format_type == 12: result = f"{hours % 12 or 12}:{minutes:02}:{seconds:02} {"AM" if hours < 12 else "PM"}".replace(":00 ", ' ')
        elif format_type == 24: result = f"{hours}:{minutes:02}:{seconds:02} ".replace(":00 ", '').rstrip()
        elif format_type == 60: result = f"{minutes + hours*60}:{seconds:02}"
        elif format_type == 1440: result = f" {hours}:{minutes:02}:{seconds:02}".replace(" 0:", '').lstrip()
        elif format_type == 3600: result = str(seconds + minutes*60 + hours*3600)
        else: result = f"{hours}:{minutes:02}:{seconds:02}"
        if read()['time format']['eastern']:
            result = result.translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")).replace("AM", "ص").replace("PM", "م")
            if read()['system'] == 'Linux':
                if len(result.split()) > 1: result = ' '.join((result.split()[1], result.split()[0]))
            else: result = "\u200F" + result
        return result


def nearest_prayer(times: dict, prayer_order: dict) -> tuple:
    now, prayer_data = datetime.now(), []
    for name in prayer_order:
        if (time_str := times.get(name)) and (pt := parse_time(time_str)):
            prayer_dt = datetime.combine(now.date(), pt)
            if prayer_dt < now: prayer_dt += timedelta(days=1)
            prayer_data.append(((prayer_dt - now).total_seconds(), name))
    if not prayer_data: return None
    sorted_data = sorted(prayer_data)
    next_prayer, last_prayer = sorted_data[0], (abs(sorted_data[-1][0] - 86400), sorted_data[-1][1])

    angle = elevation(LocationInfo(**{k: read()["backup"]["meta"][k] for k in ["latitude", "longitude"]}), now.tzinfo)
    next_color, last_color = min((c for c in sky_colors if c[0] >= angle)), max((c for c in sky_colors if c[0] <= angle))
    if angle < -10: weight = (1 + cos(2*pi*(phase(now)-14)/28))/2
    else: weight = (next_color[0] - angle)/(next_color[0] - last_color[0])
    current_color = "#{:02x}{:02x}{:02x}".format(*tuple(round(hex_to_rgb(next_color[1])[i]*(1 - weight) + hex_to_rgb(last_color[1])[i]*weight) for i in range(3)))

    if last_prayer[0] <= read()['aladhan'][2]*60 and last_prayer[0] < next_prayer[0]:
        return (last_prayer[1], format_time(last_prayer[0], 1440), last_prayer[0], current_color)
    eastern, linux = read()['time format']['eastern'], read()['system']=='Linux'
    return (next_prayer[1], f"{'\u200F'*(not linux and eastern)}{'- '*(not eastern)}{format_time(next_prayer[0], 1440)}{' -'*(linux and eastern)}", -next_prayer[0], current_color)