from set_timer import scan_device, get_tz, save_tz, exec_tz
import time
import os

actual_tz = time.strftime("%z")
actual_tz = f'{actual_tz[0:3]}:{actual_tz[3:]}'

device_list = scan_device("10.42.10", 10, 30)
# device_list = [{'ip': '10.42.10.19', 'name': 'st03'}]

for dev in device_list:
    changed = False
    tz_data = get_tz(dev['ip'])
    if tz_data.status_code == 200:
        file_text = tz_data.text

        if file_text.split()[1] != actual_tz:

            # tz not actual
            file_text = f'ntp_timeZoneOfs {actual_tz}'
            changed = True

    else:
        # set new tz file
        file_text = f'ntp_timeZoneOfs {actual_tz}'
        changed = True

    if changed:
        save_data = save_tz(file_text, dev['ip'])
        exec_data = exec_tz(dev['ip'])
        print(f'{time.strftime("%Y.%m.%d %H:%M:%S")} save file: content: <{file_text}> on {dev["name"]} ({dev["ip"]}) status_code {save_data.status_code} {exec_data.status_code}')
