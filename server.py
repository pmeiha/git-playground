from flask import Flask, render_template, request
from set_timer import scan_device, set_state, get_state, get_timer, save_timer, exec_timer, get_table, get_line, get_days, search_config
from waitress import serve
from markupsafe import escape
import os
import sys

app = Flask(__name__)
dev_ip = ""
dev_name = ""
timer_text = []
device_list = []
startedit = False

# check if file readable
config_file = 'check_openbeken.conf'

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

@app.route('/')
@app.route('/index')
def index():
    global device_list

    return render_template('index.html',
                           result="",
                           timeout=0
    )

@app.route('/get_dev')
def get_dev():
    global device_list
    global startedit

    startedit = False

    scan_list = search_config(config_file_content, 'server', 'scan' ).split()
    if len(scan_list) < 3:
        scan_list=['1.2.3', '4', '5']

    device_list = scan_device(scan_list[0], int(scan_list[1]), int(scan_list[2]))
    return render_template('get_dev.html',
                           result="",
                           device_list=device_list
    )


@app.route('/edit_timer')
def edit_timer(arg_ip = ""):
    global dev_ip
    global dev_name
    global timer_text
    global device_list
    global startedit

    if arg_ip == "":
        dev_ip = request.args.get('dev_ip')
    else:
        dev_ip = arg_ip    
    for dev in device_list:
        if dev['ip'] == dev_ip:
            dev_name = dev['name']
    rc_code = 200        
    if not startedit:        
        timer_data = get_timer(dev_ip,search_config(config_file_content, 'server', 'save' ))
        timer_text = timer_data['text'].splitlines()
        rc_code = timer_data['status_code']
        modified = ""
    else:
        modified = "(edited) "    
    power_state = get_state(dev_ip)
    print(power_state)

    return render_template(
        "timer.html",
        title=f'{dev_name} ({dev_ip})',
        rc_code=rc_code,
        current_timer=get_table(timer_text),
        current_state=f'toggle ({power_state})',
        dev_ip=dev_ip,
        device_list=device_list,
        startedit = escape(modified)
    )


@app.route('/edit_line')
def edit_line():
    global dev_ip
    global dev_name
    global timer_text

    line_nr = int(request.args.get('line_nr'))
    action = request.args.get('action')
    print("request.args: ", request.args)
    print("line_nr: ", line_nr, "len(timer_text)", len(timer_text))
    print("action: ", action)
    print("timer_text: ", timer_text)
    if line_nr < len(timer_text):
        # line_nr in valid range
        sline = timer_text[line_nr].split(" ")
        print("sline: ", sline)
        disabled = sline[0][0] == "#"
        print('Disabled: ',disabled)
            
        if action == "edit":
            print("time: ", sline[1])
            print("day: ", sline[2])
            daily = get_days(sline[2])
            print(len(daily))
            # day_val = sline[2]
            # base = 10
            # if day_val[0:2].lower() == '0x':
            #     base = 16
            # day_str = f'{int(day_val, base):0>8b}'
            # daily = ["", "", "", "", "", "", "", ""]
            # i = 0
            # for bit in day_str:
            #     if bit == "1":
            #         daily[i] = "checked"
            #     i += 1
            print("power: ", sline[4])
            pon = ""
            poff = "checked"
            if sline[4] == "P_on":
                pon = "checked"
                poff = ""
            if disabled:
                don = "checked"
                doff = ""
            else:
                don = ""
                doff = "checked"        
            return render_template(
                "edit_line.html",
                title=f'{dev_name} ({dev_ip})',
                line_nr=line_nr,
                time_value=sline[1],
                daily=daily[0],
                so=daily[7],
                mo=daily[6],
                di=daily[5],
                mi=daily[4],
                do=daily[3],
                fr=daily[2],
                sa=daily[1],
                on=pon,
                off=poff,
                don = don,
                doff = doff,
                device_list=device_list,
                side_table=get_table(
                    timer_text, without_action=True, spec_nr=line_nr)
            )
        elif action == "delete":
            startedit = True
            timer_text.pop(line_nr)
            print("del timer_text :", timer_text)
            power_state = get_state(dev_ip)
            return render_template(
                "timer.html",
                title=f'{dev_name} ({dev_ip})',
                rc_code=200,
                current_timer=get_table(timer_text),
                current_state=f'toggle ({power_state})',
                dev_ip=dev_ip,
                device_list=device_list,
                startedit = escape("(edited) ")
            )

        elif action == "insert":
            timer_text.insert(
                line_nr, "addClockEvent 00:00 0xff 1 P_off")
            return render_template(
                "edit_line.html",
                title=f'{dev_name} ({dev_ip})',
                line_nr=line_nr,
                current_line=get_line(timer_text, line_nr),
                time_value="00:00:00",
                daily="checked",
                mo="",
                di="",
                mi="",
                do="",
                fr="",
                sa="",
                so="",
                on="",
                off="checked",
                don="",
                doff="checked",
                device_list=device_list,
                side_table=get_table(
                    timer_text, without_action=True, spec_nr=line_nr)
            )
        else:
            print("unknown action", action)
            if startedit:
                modified = "(edited) "
            power_state = get_state(dev_ip)
            return render_template(
                "timer.html",
                title=f'{dev_name} ({dev_ip})',
                rc_code=timer_data.status_code,
                current_line=get_table(timer_text),
                current_state=f'toggle ({power_state})',
                dev_ip=dev_ip,
                device_list=device_list,
                startedit = escape(modified)
            )
    else:
        # add new line
        timer_text.append("")


@app.route('/store_line')
def store_line():
    global dev_ip
    global dev_name
    global timer_text
    global startedit 

    print("request.args: ", request.args)

    line_nr = request.args.get('line_nr')
    time = request.args.get('time')
    daily = request.args.get('daily', "off")
    mo = request.args.get('mo', "0")
    di = request.args.get('di', "0")
    mi = request.args.get('mi', "0")
    do = request.args.get('do', "0")
    fr = request.args.get('fr', "0")
    sa = request.args.get('sa', "0")
    so = request.args.get('so', "0")
    power = f'P_{request.args.get("power", "off")}'
    disable = request.args.get('disable')

    print(type(mo))
    if daily == "on":
        days = "0xff"
    else:
        day_nr = int(mo) + int(di) + int(mi) + \
            int(do) + int(fr) + int(sa) + int(so)
        days = f'0x{day_nr:0>2x}'
    print("days: ", days)
    timer_text[int(line_nr)] = f'{disable}addClockEvent {time} {days} {line_nr} {power}'

    startedit = True
    power_state = get_state(dev_ip)

    return render_template(
        "timer.html",
        title=f'{dev_name} ({dev_ip})',
        rc_code=200,
        current_timer=get_table(timer_text),
        current_state=f'toggle ({power_state})',
        dev_ip=dev_ip,
        device_list=device_list,
        startedit = escape("(edited) ")
    )


@app.route('/create_new')
def create_new():
    global dev_ip
    global dev_name
    global timer_text
    global startedit

    startedit = True
    power_state = get_state(dev_ip)

    timer_text = ["clearClockEvents", "listClockEvents"]
    return render_template(
        "timer.html",
        title=f'{dev_name} ({dev_ip})',
        rc_code=200,
        current_timer=get_table(timer_text),
        current_state=f'toggle ({power_state})',
        dev_ip=dev_ip,
        device_list=device_list,
        startedit = escape("(edited) ")
    )


@app.route('/store_file')
def store_file():
    global dev_ip
    global dev_name
    global timer_text
    global startedit

    startedit = False

    file_text = ""
    nr = 0
    for line in timer_text:
        if line.find('addClockEvent') >= 0:
            sline = line.split(" ")
            sline[3] = str(nr)
            line = " ".join(sline)
        file_text += line + "\n"
        nr += 1
    save_data = save_timer(file_text, dev_ip, search_config(config_file_content, 'server', 'save' ))

    if save_data.status_code == 200:
        print("save OK ", save_data.status_code)
        exec_data = exec_timer(dev_ip)
        print("exec timer result: ", exec_data.status_code)
    else:
        print("Not 200 ", save_data.status_code)

    return render_template('index.html',
                           result=f'Resultat des Speicherns {dev_name} ({dev_ip}) = speichern: {save_data.status_code}, ausführen: {exec_data.status_code}',
                           timeout=5
    )

@app.route('/toggle_power')
def toggle_power():
    
    #print('hallo',dev_ip)
    set_state(dev_ip)
    return edit_timer(dev_ip)



if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
