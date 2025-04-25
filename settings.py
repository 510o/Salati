from subprocess import Popen, DEVNULL, check_call
import os, socket, importlib.util, json
from sys import executable, platform
from copy import deepcopy
from signal import SIGKILL

app_name, venv_path = "صلاتي", executable
folder_path = __import__('pathlib').Path(__file__).parent
app_path, data_path, notifi_path, icon_path = ((folder_path/file_name).as_posix() for file_name in [app_name + ".py", ".settings", "notifications.py", "icon.png"])
folder_path = folder_path.as_posix()

def external_libraries(lib: str):
    if not importlib.util.find_spec(lib): check_call([venv_path, "-m", "pip", "install", lib])
external_libraries("psutil");from psutil import process_iter, AccessDenied, NoSuchProcess

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

def hex_to_rgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

def deduplicate(index):
    for proc in process_iter(['pid', 'name', 'cwd', 'cmdline']):
        try:
            if proc.pid != os.getpid():
                for arg in proc.info['cmdline']:
                    path = os.path.realpath(os.path.join(proc.info['cwd'], arg))
                    if (not index and path != notifi_path and os.path.dirname(path) == folder_path) or (index and path == notifi_path):
                        os.kill(proc.pid, SIGKILL)
        except (NoSuchProcess, AccessDenied, IndexError, TypeError): continue

def get(host, path):
    try:
        with __import__("ssl").create_default_context().wrap_socket(socket.create_connection((host, 443), timeout=5), server_hostname=host) as secure_socket:
            secure_socket.send(f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())
            response = b""
            while chunk := secure_socket.recv(1<<10): response += chunk
            response = response.decode()
            if 'application/json' in response: return json.loads(response[response.find("{"):response.rfind("}")+1])
            elif int(response.split("\n")[0].split()[1]) in [301, 302]:
                return get(host, next((line for line in response.split('\n') if line.lower().startswith('location: ')), None).split()[1])
    except (TimeoutError, socket.gaierror): pass

def Location():
    if ipconfig := get('ipwho.is', '/'): return float(ipconfig['latitude']), float(ipconfig['longitude'])

def prayer_message(prayer): return ""

_cache, default_data = {}, {"font": None, "time format": {'format': 12, 'eastern': True}, "aladhan": {"location": Location(), "method": None, "elapsed time": 35}, "backup": {}, "style": (1, "colors", "monochrome", "white", "black"), 
    "notifications": [True, {key: [] if key in exception_times else [{"enabled": True, "offset": 0, "title": f"وقت {prayer_times[key][0]}", "message": prayer_message(prayer_times[key])}] for key in prayer_times}]}

def data_manager(data: dict = None, new_section: dict = None) -> dict: 
    global _cache
    if not data:
        try:
            with open(data_path) as file: data = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError): data = default_data
    if isinstance(data, dict) and data.keys() == default_data.keys():
        if new_section: data.update(new_section)
        if not data['aladhan']['location']: data['aladhan']['location'] = Location()
        if data == _cache:  return data
        with open(data_path, "w") as file: json.dump(data, file, indent=4)
        _cache = deepcopy(data); return deepcopy(data)
    return data_manager(default_data)