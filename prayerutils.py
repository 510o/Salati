from datetime import datetime, timedelta, time as dt_time
from settings import app_path, read, sky_colors, hex_to_rbg
if __name__ == "__main__": exec(open(app_path).read())

def parse_time(time_str: str) -> dt_time:
    if isinstance(time_str, int):
        hours, remainder = divmod(time_str, 3600)
        minutes, seconds = divmod(remainder, 60)
        return dt_time(hour=hours%24, minute=minutes, last_prayer=seconds)
    for fmt in ("%I:%M:%S %p", "%I:%M %p", "%H:%M:%S", "%H:%M", "%M:%S", "%S"):
        try: return datetime.strptime(time_str, fmt).time()
        except ValueError: continue
    return None


def format_time(time, format_type: int = read()['time format'][0]) -> str:
    if isinstance(time, (int, float, str)):
        if isinstance(time, str):
            time_str = parse_time(time).strftime("%H %M %S")
            if time_str: hours, minutes, seconds = map(int, time_str.split())
        else:
            total_seconds = abs(int(time))
            hours, rem = divmod(total_seconds, 3600)
            minutes, seconds = divmod(rem, 60)
        if format_type == 12: return f"{hours % 12 or 12}:{minutes:02}:{seconds:02} {"AM" if hours < 12 else "PM"}".replace(":00 ", ' ')
        elif format_type == 24: return f"{hours}:{minutes:02}:{seconds:02} ".replace(":00 ", '').rstrip()
        elif format_type == 60: return f"{minutes + hours*60}:{seconds:02}"
        elif format_type == 1440: return f" {hours}:{minutes:02}:{seconds:02}".replace(" 0:", '').lstrip()
        elif format_type == 3600: return str(total_seconds)
        return f"{hours}:{minutes:02}:{seconds:02}"


def nearest_prayer(times: dict, prayer_order: dict) -> tuple:
    now, prayer_data = datetime.now(), []
    for name, time_str in times.items():
        pt = parse_time(time_str)
        if name not in prayer_order or not pt: continue
        prayer_dt = datetime.combine(now.date(), pt)
        time_diff = (prayer_dt - now).total_seconds()
        if time_diff < 0:
            prayer_dt += timedelta(days=1)
            time_diff = (prayer_dt - now).total_seconds()
        prayer_data.append({ 'name': name, 'time_obj': pt,
            'time_diff': time_diff})
    if not prayer_data: return None
    sorted_prayers = sorted(prayer_data, key=lambda x: x['time_diff'])
    next_prayer, last_prayer, time_after = sorted_prayers[0], sorted_prayers[-1], read()['aladhan'][2]*60
    last_prayer['time_diff'] = abs(last_prayer['time_diff'] - 86400)
    
    ratio = last_prayer['time_diff']/(last_prayer['time_diff'] + next_prayer['time_diff'])
    period_colors = sorted(sky_colors[last_prayer['name']])
    default_next_color, default_last_color =  [(c[0]/100, c[1]) for c in (min(sky_colors[next_prayer['name']]), max(sky_colors[sorted_prayers[-1]['name']]))]
    default_next_color = (default_next_color[0]+1, default_next_color[1])
    next_color = min((c for c in period_colors if c[0] >= ratio), default=default_next_color)
    last_color = max((c for c in period_colors if c[0] <= ratio), default=default_last_color)
    weight = (ratio - next_color[0])/(last_color[0] - next_color[0] or 1)
    mixed = tuple(int(hex_to_rbg(next_color[1])[i]*(1 - weight) + hex_to_rbg(last_color[1])[i]*weight) for i in range(3))
    current_color = "#{:02x}{:02x}{:02x}".format(*mixed)

    if last_prayer['time_diff'] <= time_after and last_prayer['time_diff'] < next_prayer['time_diff']:
        return (last_prayer['name'], format_time(last_prayer['time_diff'], 1440), last_prayer['time_diff'], current_color)
    return (next_prayer['name'], '- ' + format_time(next_prayer['time_diff'], 1440), -next_prayer['time_diff'], current_color)