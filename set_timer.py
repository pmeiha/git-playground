from dotenv import load_dotenv
from pprint import pprint
import requests
import os


def get_timer(dev_ip):
    request_url = f'http://{dev_ip}/api/lfs/timer.bat'

    timer_data = requests.get(request_url)

    return timer_data


def get_table(text_in):

    text_out = "<tr><th>line_nr</th><th>command</th></tr>"
    line_nr = 1
    for line in text_in.splitlines():

        if line.find('addClockEvent') == 0:
            hline = f"<tr><td>{line_nr}</td><td>{line}</td></tr>"
            line_nr += 1
        else:
            hline = f"<tr><td></td><td>{line}</td></tr>"

        text_out += hline

    return text_out


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
