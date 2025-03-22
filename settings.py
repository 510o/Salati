from json import load, dump; from requests import get

app_icon, app_title, system = 'icon.png', 'صلاتي', __import__('platform').system()
separator = '\\' if system == 'Windows' else '/'
folder_path = __file__.rsplit(separator, 1)[0] + separator
app_path, icon_path = folder_path + app_title + '.py', folder_path + app_icon
if __name__ == "__main__": exec(open(app_path).read())

prayer_times, exception_times,  = {
    'Fajr':('الفجر', 'ﺮﺠﻔﻟﺍ'), 'Sunrise': ('الشروق', 'ﻕﻭﺮﺸﻟﺍ'), 'Dhuhr': ('الظهر', 'ﺮﻬﻈﻟﺍ'),
    'Asr': ('العصر', 'ﺮﺼﻌﻟﺍ'), 'Maghrib': ('المغرب', 'ﺏﺮﻐﻤﻟﺍ'), 'Isha': ('العشاء', 'ءﺎﺸﻌﻟﺍ'),
    'Firstthird': ('الثلث الأول', 'ﻝﻭﺄﻟﺍ ﺚﻠﺜﻟﺍ'), 'Midnight': ('منتصف الليل', 'ﻞﻴﻠﻟﺍ ﻒﺼﺘﻨﻣ'),
    'Lastthird': ('الثلث الآخر', 'ﺮﺧﺂﻟﺍ ﺚﻠﺜﻟﺍ')}, ['Firstthird', 'Midnight', 'Lastthird']

sky_colors = { # https://coolors.co/color-picker
    'Fajr': [(0, '#2a2d6f')], 
    'Sunrise': [(0, '#248AFF')],
    'Dhuhr': [(0, '#00B7FF')],
    'Asr': [(50, '#2A8AFF'), (70, '#2A94E5')],
    'Maghrib': [(0, '#0F5CBA'), (50, '#1D31B6')],
    'Isha': [(0, '#000265'), (50, '#000066')],
    'Firstthird': [(0, '#00001a')],
    'Midnight': [(0, '#000000')],
    'Lastthird': [(0, '#000000')]}

def hex_to_rbg(h):
    return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

def Location():
    try:
        lat, lon = get("https://ipinfo.io/json").json()["loc"].split(",")
        return float(lat), float(lon)
    except: return None

def prayer_message(prayer):
    try: # maybe: https://dorar-hadith-api.herokuapp.com/api/search
        return '' # استدعاء أحاديث وفوائد لوضعها مع محتوى الإشعارات الإفتراضية
    except: return ''

_cache, default_data = None, {"font": ("", 15), "time format": (12, 24), "aladhan": [Location(), "int", 35], "backup": {}, "system": system, "style": (0, ("colors", "monochrome", "white", "black")), 
    "notifications": {key: [(0, f"وقت {prayer_times[key]}", prayer_message(prayer_times[key]))] for key in prayer_times if key not in exception_times}}
def read() -> dict:
    if _cache: return _cache
    try:
        with open(".settings") as file:
            data_payload = load(file)
            if not data_payload['aladhan'][0]: data_payload['aladhan'][0] = Location()
            for key, value in data_payload.items(): # تفكيك الصيغ المنصصة
                if isinstance(value, list): data_payload[key] = [globals().get(v, v) if isinstance(v, str) else v for v in value]
            return write(data_payload)
    except: return write(default_data)

def edit(new_section: dict) -> dict:
    data = read()
    for key, value in new_section.items():
        if key in default_data:
            data[key] = value
    return write(data)

def write(data: dict) -> dict: 
    global _cache
    if isinstance(data, dict) and data.keys() == default_data.keys():
        with open(".settings", "w") as file:
            dump(data, file, indent=4); _cache = data; return data
    return write(default_data)