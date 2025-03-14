from json import load, dump
from requests import get

def Location() -> (list, None):
    try:
        lat, lon = get("https://ipinfo.io/json").json()["loc"].split(",")
        return float(lat), float(lon)
    except: return None

_cache, default_data = None, {"font": [["", 15], ['white', 'black']], "time format": [12, 24], "aladhan": [Location(), int]} 
def read() -> dict:
    if _cache: return _cache
    try:
        with open(".settings") as file:
            data_payload = load(file)
            if not data_payload['aladhan'][0]: data_payload['aladhan'][0] = Location()
            for key, value in data_payload.items():
                data_payload[key] = [globals().get(v, v) if isinstance(v, str) else v for v in value] # تفكيك الصيغ المنصصة
            data_payload["system"] = __import__('platform').system()
            return write(data_payload)
    except: return write(default_data)

def edit(section): pass

def write(data: dict) -> dict:
    with open(".settings", "w") as file:
        try:
            dump(data, file, default=lambda x: x.__name__ if isinstance(x, type) else x)  # تنصيص الصيغ المختلفة
            _cache = data; return data
        except: return write(default_data)