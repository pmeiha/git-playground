from flask import url_for
from dotenv import load_dotenv
from pprint import pprint
from markupsafe import escape
import requests
import dns.resolver
import os
import sys

###################################################################################
# search config according "tag" and "dev" 
# if no dev specific availabel it will return the "all" value
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



def scan_device(ip_prefix, start, end):

    ip_list = []
    device_list = []
    dnsresolver = dns.resolver.Resolver(configure=False)
    dnsresolver.nameservers = ["10.42.10.1"]

    for i in range(start, end+1):
        ip = f'{ip_prefix}.{i}'
        request_url = f'http://{ip}'
        try:
            scan_data = requests.get(request_url, timeout=1)
            if b'OpenBK7231T' in scan_data.content:
                found = True

        except:
            found = False

        if found:
            ip_list.append(ip)

    for ip in ip_list:
        n = dns.reversename.from_address(ip)
        try:
            res = dnsresolver.query(n, 'PTR')
        except:
            res = []
        device_list.append({'ip': ip, 'name': str(res[0]).split(".")[0]})
    return device_list

def set_state(dev_ip):

    request_url = f'http://{dev_ip}/cm'

    ret_data = requests.post(request_url, data = {'cmnd' : "power toggle"} )

    if ret_data.status_code != 200:
        retVal = "NOK"
    else:
        retVal = ret_data.json()['POWER']    

    return retVal

def get_state(dev_ip):

    request_url = f'http://{dev_ip}/cm'

    ret_data = requests.post(request_url, data = {'cmnd' : 'power'})

    if ret_data.status_code != 200:
        retVal = "NOK"
    else:
        retVal = ret_data.json()['POWER']    

    return retVal


def get_timer(dev_ip, filename=""):

    request_url = f'http://{dev_ip}/api/lfs/timer.bat'
    timer_ret = {'status_code': 0, 'text': ''}

    timer_data = requests.get(request_url)

    if timer_data.status_code != 200:

        if filename == "":
            #filename = "save/{device}_timer.bat"
            return timer_ret

        filename = filename.format(device = dev_ip)
        print('get filename',filename)

        if not os.access(filename, os.R_OK):
            print(sys.argv[0],":",filename,"is not readable")
        else:    
            f = open(filename,'r')
            timer_ret['text'] = f.read()
            f.close()
            timer_ret['status_code'] = 200
    else:
        timer_ret['status_code'] = timer_data.status_code
        timer_ret['text'] = timer_data.text

    return timer_ret


def get_tz(dev_ip):
    request_url = f'http://{dev_ip}/api/lfs/tz.bat'

    timer_data = requests.get(request_url)

    return timer_data


def get_autoexec(dev_ip):
    return requests.get(f'http://{dev_ip}/api/lfs/autoexec.bat')


def save_timer(file_text, dev_ip, filename="",local=True):

    if local:
      if filename == "":
          filename = "save/{device}_timer.bat"
      filename = filename.format(device = dev_ip)
      f = open(filename,'w')
      f.write(file_text)
      f.close()

    request_url = f'http://{dev_ip}/api/lfs/timer.bat'
    
    if len(file_text) > 1:
      ret_data = requests.post(request_url, file_text)

    else:
      ret_data = requests.get(request_url)    

    return ret_data


def save_tz(file_text, dev_ip):
    request_url = f'http://{dev_ip}/api/lfs/tz.bat'

    ret_data = requests.post(request_url, file_text)

    return ret_data

def save_autoexec(file_text, dev_ip):
    return requests.post(f'http://{dev_ip}/api/lfs/autoexec.bat', file_text)


def exec_timer(dev_ip):
    request_url = f'http://{dev_ip}/api/cmnd'

    ret_data = requests.post(request_url, "exec timer.bat")

    return ret_data


def exec_tz(dev_ip):
    request_url = f'http://{dev_ip}/api/cmnd'

    ret_data = requests.post(request_url, "exec tz.bat")

    return ret_data

def exec_autoexec(dev_ip):
    return requests.post(f'http://{dev_ip}/api/cmnd', "exec autoexec.bat")


def line_form(line_nr, edit=True, delete=True, insert=True, etext="edit", dtext="delete", itext="oben einfügen"):

    t_out = ""

    if edit or delete or insert:
        t_out += f'<form action="{url_for("edit_line")}" method="get"><input type="hidden" id="line_nr" name="line_nr" value="{escape(line_nr)}">'

        if edit:
            t_out += f'<button type="submit" id="edit" name="action" value="edit">{escape(etext)}</button>'

        if delete:
            t_out += f'<button type="submit" id="delete" name="action" value="delete">{escape(dtext)}</button>'

        if insert:
            t_out += f'<button type="submit" id="insert" name="action" value="insert">{escape(itext)}</button>'

        t_out += '</form>'
    return t_out


def get_table(text_in, without_action=False, spec_nr=0):

    if without_action:
        text_out = "<tr><th></th><th></th><th></th></tr>"
    else:
        text_out = "<tr><th></th><th></th><th></th><th></th></tr>"

    line_nr = 1

    for line in text_in:
        print("line : ", line, " find: ", line.find('addClockEvent'))

        hline = ""
        spec_tag = ""
        if line_nr == spec_nr:
            spec_tag = ' class="specal" '

        if line.find('addClockEvent') == 0:
            sline = line.split(" ")
            if without_action:
                hline = f'<tr{spec_tag}><td>&nbsp;{escape(sline[1])}</td><td>&nbsp;{escape(get_days(sline[2], True))}</td><td>&nbsp;{escape(sline[5])}</td></tr>'
            else:
                hline = f'<tr{spec_tag}><td>{line_form(line_nr)}</td><td>&nbsp;{escape(sline[1])}</td><td>&nbsp;{escape(get_days(sline[2], True))}</td><td>&nbsp;{escape(sline[5])}</td></tr>'
            line_nr += 1

        text_out += hline

    if without_action:
        text_out += f'<tr><td></td><td></td><td></td></tr>'
    else:
        text_out += f'<tr><td>{line_form(line_nr, edit=False, delete=False, itext="Zeile anhängen")}</td><td></td><td></td><td></td></tr>'

    return text_out


def get_line(text_in, line_nr):
    text_out = ""
    if line_nr < len(text_in):
        text_out = text_in[line_nr]
    return "test_in " + text_out + " Line " + str(line_nr)


def get_days(day_val=0, return_name=False):
    daily = ["", "", "", "", "", "", "", ""]
    dailyn = ["all", "Sa", "Fr", "Do", "Mi", "Di", "Mo", "So"]
    daily_name = ""

    base = 10
    if day_val[0:2].lower() == '0x':
        base = 16
    day_str = f'{int(day_val, base):0>8b}'
    i = 0
    for bit in day_str:
        if bit == "1":
            daily[i] = "checked"
            daily_name += dailyn[i] + ", "
        i += 1
    if return_name:
        if "all" in daily_name:
            daily_name = "all"
        return daily_name.rstrip(", ")
    else:
        return daily


if __name__ == "__main__":
    print("\n*** get timer_data ***\n")

    # dev_ip = input("Please enter the IP of the device: ")
    dev_ip = "10.42.10.19"

    timer_data = get_timer(dev_ip)

    if not timer_data.status_code == 200:
        print()

    print("*** iter_lines ***")
    for c in timer_data.iter_lines():
        print(c)
    print("***\n")
    print(timer_data.status_code)
