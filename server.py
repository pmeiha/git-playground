from flask import Flask, render_template, request
from set_timer import get_timer, get_table, get_line
from waitress import serve

app = Flask(__name__)
dev_ip = ""
timer_text = []


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/set_timer')
def edit_timer():
    global dev_ip
    global timer_text

    dev_ip = request.args.get('dev_ip')
    timer_data = get_timer(dev_ip)
    timer_text = timer_data.text.splitlines()
    return render_template(
        "timer.html",
        title=dev_ip,
        rc_code=timer_data.status_code,
        current_timer=get_table(timer_text)
    )


@app.route('/edit_line')
def edit_line():
    global dev_ip
    global timer_text
    line_nr = int(request.args.get('line_nr'))
    action = request.args.get('action')
    print("request.args: ", request.args)
    print("timer_text: ", timer_text[line_nr])
    print("line_nr: ", line_nr, "len(timer_text)", len(timer_text))
    print("action: ", action)
    if line_nr < len(tabeltext):
        # line_nr in valid range

        if action == "edit":
            return render_template(
                "edit_line.html",
                title=dev_ip,
                line_nr=line_nr,
                current_line=get_line(timer_text, line_nr)
            )
        elif action == "delete":
            timer_text = timer_text.remove(timer_text[line_nr])
            return render_template(
                "timer.html",
                title=dev_ip,
                rc_code=timer_data.status_code,
                current_line=get_table(timer_text)
            )

        elif action == "insert":
            return render_template(
                "edit_line.html",
                title=dev_ip,
                line_nr=line_nr,
                current_line=get_line(timer_text, line_nr)
            )
        else:
            print("unknown action", action)
            return render_template(
                "timer.html",
                title=dev_ip,
                rc_code=timer_data.status_code,
                current_line=get_table(timer_text)
            )


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
