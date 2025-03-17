from json import load, dump; from requests import get

app_icon, app_title = 'icon.png', 'صلاتي'

prayer_times, exception_times = {
        'Fajr':('الفجر', 'ﺮﺠﻔﻟﺍ', 'Sunrise'), 'Sunrise': ('الشروق', 'ﻕﻭﺮﺸﻟﺍ', 'Dhuhr'), 'Dhuhr': ('الظهر', 'ﺮﻬﻈﻟﺍ', 'Asr'),
        'Asr': ('العصر', 'ﺮﺼﻌﻟﺍ', 'Maghrib'), 'Maghrib': ('المغرب', 'ﺏﺮﻐﻤﻟﺍ', 'Isha'), 'Isha': ('العشاء', 'ءﺎﺸﻌﻟﺍ', 'Firstthird'),
        'Firstthird': ('الثلث الأول', 'ﻝﻭﺄﻟﺍ ﺚﻠﺜﻟﺍ', 'Midnight'), 'Midnight': ('منتصف الليل', 'ﻞﻴﻠﻟﺍ ﻒﺼﺘﻨﻣ', 'Lastthird'),
        'Lastthird': ('الثلث الآخر', 'ﺮﺧﺂﻟﺍ ﺚﻠﺜﻟﺍ', 'Fajr')}, ['Firstthird', 'Midnight', 'Lastthird'],

def Location():
    try:
        lat, lon = get("https://ipinfo.io/json").json()["loc"].split(",")
        return float(lat), float(lon)
    except: return None

def prayer_message(prayer):
    try: # maybe: https://dorar-hadith-api.herokuapp.com/api/search
        return '' # استدعاء أحاديث وفوائد لوضعها مع محتوى الإشعارات الإفتراضية
    except: return ''

_cache, default_data = None, {"font": [("", 15), ('white', 'black')], "time format": (12, 24), "aladhan": [Location(), "int"], "backup": {},
    "system": str(__import__('platform').system()), "notifications": {key: [0, prayer_message(prayer_times[key])] for key in prayer_times if key not in exception_times}}
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

def edit(new_section: dict):
    data = read()
    for key, value in new_section.items():
        if key in default_data:
            data[key] = value
    return write(data)

def write(data: dict) -> dict: 
    if isinstance(data, dict) and data.keys() == default_data.keys():
        with open(".settings", "w") as file:
            dump(data, file, indent=4); _cache = data; return data
    return write(default_data)