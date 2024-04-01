from flask import Flask, render_template, request
from set_timer import scan_device, get_timer, save_timer, exec_timer, get_table, get_line, get_days
from waitress import serve

app = Flask(__name__)
dev_ip = ""
dev_name = ""
timer_text = []
device_list = []


@app.route('/')
@app.route('/index')
def index():
    global device_list
    device_list = scan_device("10.42.10", 10, 30)
    return render_template('index.html',
                           result="",
                           device_list=device_list
                           )


@app.route('/set_timer')
def edit_timer():
    global dev_ip
    global dev_name
    global timer_text
    global device_list

    dev_ip = request.args.get('dev_ip')
    for dev in device_list:
        if dev['ip'] == dev_ip:
            dev_name = dev['name']
    timer_data = get_timer(dev_ip)
    timer_text = timer_data.text.splitlines()
    return render_template(
        "timer.html",
        title=f'{dev_name} ({dev_ip})',
        rc_code=timer_data.status_code,
        current_timer=get_table(timer_text),
        device_list=device_list
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
            print("power: ", sline[5])
            pon = ""
            poff = "checked"
            if sline[5] == "on":
                pon = "checked"
                poff = ""
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
                device_list=device_list,
                side_table=get_table(
                    timer_text, without_action=True, spec_nr=line_nr)
            )
        elif action == "delete":
            timer_text.pop(line_nr)
            print("del timer_text :", timer_text)
            return render_template(
                "timer.html",
                title=f'{dev_name} ({dev_ip})',
                rc_code=200,
                current_timer=get_table(timer_text),
                device_list=device_list
            )

        elif action == "insert":
            timer_text.insert(
                line_nr, "addClockEvent 00:00:00 0xff 1 power off")
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
                device_list=device_list,
                side_table=get_table(
                    timer_text, without_action=True, spec_nr=line_nr)
            )
        else:
            print("unknown action", action)
            return render_template(
                "timer.html",
                title=f'{dev_name} ({dev_ip})',
                rc_code=timer_data.status_code,
                current_line=get_table(timer_text),
                device_list=device_list
            )
    else:
        # add new line
        timer_text.append("")


@app.route('/store_line')
def store_line():
    global dev_ip
    global dev_name
    global timer_text

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
    power = request.args.get('power', "off")

    print(type(mo))
    if daily == "on":
        days = "0xff"
    else:
        day_nr = int(mo) + int(di) + int(mi) + \
            int(do) + int(fr) + int(sa) + int(so)
        days = f'0x{day_nr:0>2x}'
    print("days: ", days)
    timer_text[int(line_nr)] = f'addClockEvent {
        time} {days} {line_nr} power {power}'

    return render_template(
        "timer.html",
        title=f'{dev_name} ({dev_ip})',
        rc_code=200,
        current_timer=get_table(timer_text),
        device_list=device_list
    )


@app.route('/create_new')
def create_new():
    global dev_ip
    global dev_name
    global timer_text

    timer_text = ["clearClockEvents", "listClockEvents"]
    return render_template(
        "timer.html",
        title=f'{dev_name} ({dev_ip})',
        rc_code=200,
        current_timer=get_table(timer_text),
        device_list=device_list
    )


@app.route('/store_file')
def store_file():
    global dev_ip
    global dev_name
    global timer_text

    file_text = ""
    nr = 0
    for line in timer_text:
        if line.find('addClockEvent') == 0:
            sline = line.split(" ")
            sline[4] = str(nr)
            line = " ".join(sline)
        file_text += line + "\n"
        nr += 1
    save_data = save_timer(file_text, dev_ip)

    if save_data.status_code == 200:
        print("save OK ", save_data.status_code)
        exec_data = exec_timer(dev_ip)
        print("exec timer result: ", exec_data.status_code)
    else:
        print("Not 200 ", save_data.status_code)

    return render_template('index.html',
                           result=f'Resultat des Speicherns {dev_name} ({dev_ip}) = speichern: {
                               save_data.status_code}, ausführen: {exec_data.status_code}',
                           device_list=device_list
                           )


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
