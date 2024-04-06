from set_timer import scan_device, get_tz, save_tz, exec_tz, get_autoexec, save_autoexec, exec_autoexec
import time
import os
import sys
import argparse

def search_config(config=[], tag="", dev=""):
    f = ""
    for c in config:
        e = c.split(':')
        #print(e[0].lower().strip(), tag.lower(), e[1].lower().strip(), dev.lower())
        if e[0].lower().strip() == tag.lower() and e[1].lower().strip() == dev.lower():
            return e[2].strip()
        elif e[0].lower().strip() == tag.lower() and e[1].lower().strip() == "all":
            #print('all',e[2])
            f = e[2].strip()
    return f         

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
    print('get_file',filename)
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

parser = argparse.ArgumentParser(description='Check/Set autoexec.bat and tz.bat to openBeken devices')
parser.add_argument('-c','--config',help='config file name',default='check_openbeken.conf')
args = parser.parse_args()


# check if file readable
config_file = args.config

config_file_content = []
if not os.access(config_file, os.R_OK):
    print(sys.argv[0],":",config_file,"is not readable")
    
else:
    c = open(config_file,"r")
    for line in c:
        comment = line.find("#")
        if comment > 0:
            config_file_content.append(line[0:comment].strip())
        elif comment == -1 and len(line.split(':')) >= 3:    
            config_file_content.append(line.strip())

print(config_file_content)

print('st03', search_config(config_file_content, "autoexec", "ST03" ))
print('st04', search_config(config_file_content, "autoexec", "ST04" ))
print('st05', search_config(config_file_content, "autoexec", "ST05" ))


# autoexec autoexec.bat devicename
# autoexec autoexec_all all
# autoexec autoexec_ST03 ST03


actual_tz = time.strftime("%z")
actual_tz = f'{actual_tz[0:3]}:{actual_tz[3:]}'

device_list = scan_device("10.42.10", 10, 30)
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

