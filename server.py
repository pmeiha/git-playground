from flask import Flask, render_template, request
from set_timer import get_timer, get_table
from waitress import serve

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/set_timer')
def edit_timer():
    dev_ip = request.args.get('dev_ip')
    timer_data = get_timer(dev_ip)
    return render_template(
        "timer.html",
        title=dev_ip,
        rc_code=timer_data.status_code,
        current_timer=get_table(timer_data.text)
    )


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
