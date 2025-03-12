from datetime import datetime, timedelta, date, time as dt_time
from settings import Settings

def parse_time(time_str: str) -> dt_time:
    if isinstance(time_str, int):
        hours, remainder = divmod(time_str, 3600)
        minutes, seconds = divmod(remainder, 60)
        return dt_time(hour=hours%24, minute=minutes, second=seconds)
    for fmt in ("%I:%M:%S %p", "%I:%M %p", "%H:%M:%S", "%H:%M", "%M:%S", "%S"):
        try: return datetime.strptime(time_str, fmt).time()
        except ValueError: continue
    return None


def format_time(time, format_type: int = None) -> str:
    format_type = format_type or Settings.read()['time format'][0]
    if isinstance(time, (int, float, str)):
        if isinstance(time, str):
            time_str = parse_time(time).strftime("%H:%M:%S")
            if time_str: hours, minutes, seconds = map(int, time_str.split(":"))
        else:
            total_seconds = abs(int(time))
            hours, rem = divmod(total_seconds, 3600)
            minutes, seconds = divmod(rem, 60)
        if format_type == 12: return f"{hours % 12 or 12}:{minutes:02}:{seconds:02} {"AM" if hours < 12 else "PM"}".replace(":00 ", ' ')
        elif format_type == 24: return f"{hours}:{minutes:02}:{seconds:02} ".replace(":00 ", ' ').strip(' ')
        elif format_type == 60: return f"{minutes + hours*60}:{seconds:02}"
        elif format_type == 1440: return f"{hours}:{minutes:02}:{seconds:02} ".lstrip("0:")
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
            'time_diff': time_diff, 'datetime': prayer_dt})
    if not prayer_data: return None
    sorted_prayers = sorted(prayer_data, key=lambda x: x['time_diff'])
    first, second, time_after = sorted_prayers[0], sorted_prayers[-1], 2100 # وقت إبقاء العرض بعد الأذان
    if abs(second['time_diff'] - 86400) <= time_after and abs(second['time_diff'] - 86400) < first['time_diff']:
        return (second['name'], format_time(second['time_diff'] - 86400, 1400), second['time_diff'])
    return (first['name'], '- ' + format_time(first['time_diff'], 1400), first['time_diff'])