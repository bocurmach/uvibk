import requests
import json
from datetime import datetime, timedelta
import telebot
import time
import create_graphic
from helper import API_URL_IBK, WEB_URL_IBK, TELEGRAM_TOKEN, CHANNEL_NAME
import logging
from urllib3.exceptions import MaxRetryError


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

            r = requests.get(API_URL_IBK)
        except MaxRetryError as err:
            print('MaxRetryError', err)
        except Exception as err:
            print(err)
        else:
            break

    content = json.loads(r.content.decode('utf-8'))

    uve = content['Innsbruck']['uve']

    measurements = uve['measurement']
    time_stamps = convert_time_stamps(uve['ts'])

    print(datetime.now(), time_stamps[-1], measurements[-1])

    return measurements, time_stamps


def send_to_bot(msg: str,
                cur_index: float,
                last_warning_msg: str,
                measurements: list[float],
                time_stamps: list[datetime]):

    warning_msg = uv_warning_message(cur_index)
    print(warning_msg)

    if warning_msg == last_warning_msg:
        return last_warning_msg

    msg += '\n' + warning_msg
    msg += f'\nInformation taken from:\n{WEB_URL_IBK}'
    bot = telebot.TeleBot(token=TELEGRAM_TOKEN)

    cur_img = create_graphic.create_image(measurements, time_stamps)

    if cur_img is not None:
        logging.info(cur_img)
        bot.send_photo(chat_id=CHANNEL_NAME, photo=cur_img, caption=msg)
    else:
        bot.send_message(chat_id=CHANNEL_NAME, text=msg)
    return warning_msg


def uv_warning_message(cur_index):
    warning_message: str

    if cur_index < 3:
        warning_message = 'uv currently not dangerous'
    elif cur_index < 6:
        warning_message = 'moderate uv, sunscreen appropriate'
    elif cur_index < 8:
        warning_message = 'high uv, try to stay in the shadows and better GET SUNSCREEN'
    elif cur_index < 10:
        warning_message = 'very high uv, stay in the shadows!'
    else:
        warning_message = 'EXTREME uv, stay indoors!'

    return warning_message


def update_message(last_warning_msg: str):
    measurements, time_stamps = get_data_from_api()
    info_str = ''

    measurement = measurements[-1]
    time_stamp = time_stamps[-1]

    info_str = f'{time_stamp}: {measurement:.2f} '

    logging.info(info_str)

    return send_to_bot(info_str, measurement, last_warning_msg, measurements, time_stamps)


def main():
    warning_msg = ""

    check_every_x_mins = 6

    while True:
        if datetime.now().hour >= 20:
            print('good night')
            hours_until_8 = 24 + 8 - datetime.now().hour
            time.sleep(60*60*hours_until_8)

        if datetime.now().minute % check_every_x_mins == 0:
            if datetime.now().second <= 5:
                time.sleep(6)
                warning_msg = update_message(warning_msg)
                time.sleep(check_every_x_mins*60-10)
        else:
            time.sleep(60)


if __name__ == '__main__':
    main()
