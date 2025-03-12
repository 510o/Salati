from json import load, dump
from requests import get

def Location() -> (list, None):
    try:
        lat, lon = get("https://ipinfo.io/json").json()["loc"].split(",")
        return float(lat), float(lon)
    except: return None

class Settings:
    _cache, default_data = None, {"font": [["", 15], ['white', 'black']], "aladhan": [Location(), int], "time format": [12, 24]} 
    @staticmethod
    def read() -> dict:
        if Settings._cache: return Settings._cache
        try:
            with open(".settings") as file:
                data_payload = load(file)
                if not data_payload['aladhan'][0]: data_payload['aladhan'][0] = Location()
                for key, value in data_payload.items():
                    data_payload[key] = [globals().get(v, v) if isinstance(v, str) else v for v in value] # تفكيك الصيغ المنصصة
                return Settings.write(data_payload)
        except: return Settings.write(Settings.default_data)
    
    @staticmethod
    def edit(section): pass # fonts.families())
    
    @staticmethod
    def write(data: dict) -> dict:
        with open(".settings", "w") as file:
            try:
                dump(data, file, default=lambda x: x.__name__ if isinstance(x, type) else x)  # تنصيص الصيغ المختلفة
                Settings._cache = data; return data
            except: return Settings.write(Settings.default_data)