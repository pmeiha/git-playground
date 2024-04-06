from set_timer import scan_device, get_tz, save_tz, exec_tz, get_autoexec, save_autoexec, exec_autoexec, search_config
import time
import os
import sys
import argparse

###################################################################################
# add a config tag to the device list
def add_config(device_list=[], config_list=[], tag=""):

    ret_list = []

    for dev in device_list: 
        dev[tag] = search_config(config_file_content, tag, dev['name'] )
        ret_list.append(dev)

    return ret_list    

###################################################################################
# get thew content of a file
# if not exist or not readable return an empty string
def get_file(filename):

    content = ''
    if not os.access(filename, os.R_OK):
        print(sys.argv[0],":",filename,"is not readable")
    
    else:
        f = open(filename,"r")
        content = f.read()

    return content    

###################################################################################
# compare file with a given content
# return True if content equal
def check_file(filename,content=""):

    return get_file(filename) == content

###################################################################################
# main
###################################################################################

parser = argparse.ArgumentParser(description='Check/Set autoexec.bat and tz.bat to openBeken devices')
parser.add_argument('-c','--config',help='config file name',default='check_openbeken.conf')
args = parser.parse_args()

# check if file readable
config_file = args.config

config_file_content = []
if not os.access(config_file, os.R_OK):
    print(sys.argv[0],":",config_file,"is not readable")
    
else:
    # read config file
    c = open(config_file,"r")
    for line in c:
        comment = line.find("#")
        if comment > 0:
            config_file_content.append(line[0:comment].strip())
        elif comment == -1 and len(line.split(':')) >= 3:    
            config_file_content.append(line.strip())

# get actual tz value
actual_tz = time.strftime("%z")
actual_tz = f'{actual_tz[0:3]}:{actual_tz[3:]}'

# scan for devices 
scan_list = search_config(config_file_content, 'server', 'scan' ).split()
if len(scan_list) < 3:
    scan_list=['10.42.10', '10', '30']
device_list = scan_device(scan_list[0], int(scan_list[1]), int(scan_list[2]))
# device_list = [{'ip': '10.42.10.19', 'name': 'st03'}]

device_list = add_config(device_list, config_file_content, 'autoexec')

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

    changed = False
    auto_data = get_autoexec(dev['ip'])
    if auto_data.status_code == 200:

        if not check_file(dev['autoexec'],auto_data.text):

            file_text = get_file(dev['autoexec'])
            changed = True

    else:
        # set new tz file
        file_text = get_file(dev['autoexec'])
        changed = True

    if changed:
        save_data = save_autoexec(file_text, dev['ip'])
        exec_data = exec_autoexec(dev['ip'])
        print(f'{time.strftime("%Y.%m.%d %H:%M:%S")} save file: content: {dev["autoexec"]} on {dev["name"]} ({dev["ip"]}) status_code {save_data.status_code} {exec_data.status_code}')

