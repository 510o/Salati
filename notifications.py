from settings import external_libraries, deduplicate, data_manager, prayer_times, platform, os, icon_path, app_name
from prayerutils import datetime, format_time; from time import sleep

if platform == "darwin": external_libraries("pync"); from pync import Notifier; notification_sender = lambda notifi: Notifier.notify(notifi["message"], title=notifi["title"], appIcon=icon_path, sender=app_name)
elif platform.startswith("linux"): notification_sender = lambda notifi: os.system(f'notify-send -i "{icon_path}" -a "{app_name}" "{notifi["title"]}" "{notifi["message"]}"')
else: external_libraries("plyer"); from plyer import notification; notification_sender = lambda notifi: notification.notify(title=notifi["title"], message=notifi["message"], timeout=10)

deduplicate(1)

while True:
    data = data_manager()
    if (notifis := data['notifications'][1] if data['notifications'][0] else None):
        for prayer in prayer_times.keys():
            for notifi in notifis[prayer]:
                if notifi["enabled"] and (times := data['backup'].get('timings')) and (now := datetime.now()):
                    if round(int(format_time(times[prayer], 3600, True))/60, 2) + notifi["offset"] == round(now.hour*60 + now.minute + (now.second + now.microsecond/1e6)/60, 2):
                        notification_sender(notifi); sleep(0.5)
                    # else: print(round(now.hour*60 + now.minute + (now.second + now.microsecond/1e6)/60 - int(format_time(data['backup'].get('timings', {})[prayer], 3600, True))/60, 2))
    sleep(0.1)