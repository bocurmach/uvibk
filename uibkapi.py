import time
import json
from urllib3.exceptions import MaxRetryError
import requests
API_URL_IBK = 'https://uv-data.i-med.ac.at/public/data/?site=Innsbruck'
from datetime import datetime, timedelta


def convert_time_stamps(time_stamps: list[str]):
    for i in range(len(time_stamps)):
        time_stamps[i] = datetime.strptime(
            time_stamps[i], '%Y-%m-%dT%H:%M:%S+0000') + timedelta(hours=2)

    return time_stamps


def get_data_from_api():
    retry_count = 0
    while True:
        try:
            time.sleep(retry_count**2)
            retry_count += 1

            print(datetime.now(), 'send request to', API_URL_IBK)
            r = requests.get(API_URL_IBK)
        except MaxRetryError as err:
            print('MaxRetryError', err)
        except Exception as err:
            print(err)
        else:
            break

    try:
        content = json.loads(r.content.decode('utf-8'))
        uve = content['Innsbruck']['uve']

        measurements = uve['measurement']

        time_stamps = convert_time_stamps(uve['ts'])
    except:
        measurements = []
        time_stamps = []

    return measurements, time_stamps

