from json import load, dump; from requests import get

app_name, system = "صلاتي", __import__('platform').system()
folder_path = __import__('pathlib').Path(__file__).parent
app_path, data_path, icon_path = (str(folder_path/file_name) for file_name in [app_name + ".py", ".settings", "icon.png"])
if __name__ == "__main__": exec(open(app_path).read()); raise SystemExit

prayer_times, exception_times,  = {
    'Fajr':('الفجر', 'ﺮﺠﻔﻟﺍ'), 'Sunrise': ('الشروق', 'ﻕﻭﺮﺸﻟﺍ'), 'Dhuhr': ('الظهر', 'ﺮﻬﻈﻟﺍ'),
    'Asr': ('العصر', 'ﺮﺼﻌﻟﺍ'), 'Maghrib': ('المغرب', 'ﺏﺮﻐﻤﻟﺍ'), 'Isha': ('العشاء', 'ءﺎﺸﻌﻟﺍ'),
    'Firstthird': ('الثلث الأول', 'ﻝﻭﻷﺍ ﺚﻠﺜﻟﺍ'), 'Midnight': ('منتصف الليل', 'ﻞﻴﻠﻟﺍ ﻒﺼﺘﻨﻣ'),
    'Lastthird': ('الثلث الآخر', 'ﺮﺧﻵﺍ ﺚﻠﺜﻟﺍ')}, ['Firstthird', 'Midnight', 'Lastthird']

sky_colors = [ # https://coolors.co/color-picker
    (-90, "#0A0A0A"), (0, '#141414'), 
    (10, '#4096D7'), (50, '#31A2FF'),
    (70, '#44C4FF'), (90, '#00B6F8')] # ∠90 التعامد

def hex_to_rgb(h):
    return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

def Location():
    try:
        lat, lon = get("https://ipinfo.io/json").json()["loc"].split(",")
        return float(lat), float(lon)
    except: return None

def prayer_message(prayer):
    try: # maybe: https://dorar-hadith-api.herokuapp.com/api/search
        return ' ' # استدعاء أحاديث وفوائد لوضعها مع محتوى الإشعارات الإفتراضية
    except: return ''

_cache, default_data = None, {"font": None, "time format": {'format': 12, 'eastern': True}, "aladhan": [Location(), "int", 35], "backup": {}, "system": system, "style": (1, "colors", "monochrome", "white", "black"), 
    "notifications": {key: [] if key in exception_times else [(0, f"وقت {prayer_times[key][0]}", prayer_message(prayer_times[key]))] for key in prayer_times}}
def read() -> dict:
    if _cache: return _cache
    try:
        with open(data_path) as file:
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
        with open(data_path, "w") as file:
            dump(data, file, indent=4); _cache = data; return data
    return write(default_data)