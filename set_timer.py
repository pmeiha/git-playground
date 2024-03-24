from dotenv import load_dorenv
from pprint import pprint
import requests
import os


def get_timer(dev_ip):
    request_url = f'http://{dev_ip}/api/lfs/timer.bat'

    timer_data = requests.get(request_url)

    return timer_data
