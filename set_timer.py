from dotenv import load_dotenv
from pprint import pprint
from markupsafe import escape
import requests
import os


def get_timer(dev_ip):
    request_url = f'http://{dev_ip}/api/lfs/timer.bat'

    timer_data = requests.get(request_url)

    return timer_data


def line_form(line_nr, edit=True, delete=True, insert=True, etext="edit", dtext="delete", itext="insert oben"):

    t_out = ""

    if edit or delete or insert:
        t_out += f'<form action="/edit_line"><input type="hidden" value="{
            escape(line_nr)}">'

        if edit:
            t_out += f'<button type="submit" name="edit">{
                escape(etext)}</button>'

        if delete:
            t_out += f'<button type="submit" id="delete">{
                escape(dtext)}</button>'

        if insert:
            t_out += f'<button type="submit" id="insert">{
                escape(itext)}</button>'

        t_out += '</form>'
    return t_out


def get_table(text_in):

    text_out = "<tr><th>1</th><th>2</th><th>3</th><th>4</th></tr>"
    line_nr = 1
    for line in text_in.splitlines():

        hline = ""

        if line.find('addClockEvent') == 0:
            sline = line.split(" ")
            hline = f"<tr><td>{
                line_form(line_nr)}</td><td>{escape(sline[1])}</td><td>{escape(sline[2])}</td><td>{escape(sline[5])}</td></tr>"
            line_nr += 1
        # else:
        #     hline = f"<tr><td></td><td>{escape(line)}</td></tr>"

        text_out += hline

    text_out += f"<tr><td>{line_form(line_nr, edit=False, delete=False, itext="insert new")
                           }</td><td>2</td><td>3</td><td>4</td></tr>"

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
