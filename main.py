from datetime import datetime
import telebot
import time
import requests
from create_graphic import create_image, IMG_PATH
from helper import TELEGRAM_TOKEN, CHANNEL_NAME, NTFY_TOPIC, WEB_URL_IBK, NFTY_IMG
import logging
from uibkapi import get_data_from_api
import os.path
from pprint import pprint

STARTING_HOUR = 7


def send_out(msg: str,
             cur_index: float,
             last_warning_msg: str,
             measurements: list[float],
             time_stamps: list[datetime]):

    warning_msg = uv_warning_message(cur_index)
    print(warning_msg)

    if warning_msg == last_warning_msg:
        return last_warning_msg

    create_image(measurements, time_stamps)

    send_via_telegram_bot(msg, warning_msg)
    # send_via_ntfy(msg, warning_msg)

    return warning_msg


def send_via_telegram_bot(msg: str, warning_msg: str):
    bot = telebot.TeleBot(token=TELEGRAM_TOKEN)

    msg += '\n' + warning_msg
    msg += '\n' + WEB_URL_IBK

    if os.path.exists(IMG_PATH):
        bot.send_photo(chat_id=CHANNEL_NAME, photo=open(IMG_PATH, 'rb'), caption=msg)
    else:
        bot.send_message(chat_id=CHANNEL_NAME, text=msg)


def send_via_ntfy(msg: str, warning_msg: str):
    print(open(IMG_PATH, 'rb'))

    response = requests.put(NFTY_IMG,
                            data=open(IMG_PATH, 'rb'),
                            headers={'Filename': IMG_PATH}
                            )
    pprint(response.__dict__)
    headers = {
        # "Click": WEB_URL_IBK,
        'Title': warning_msg,
        }

    if response.status_code == 200:
        attach_path = response.json()
        attach_path = attach_path['attachment']['url']
        headers['Attach'] = attach_path

    response = requests.post(NTFY_TOPIC,
                             data=msg,
                             headers=headers
                             )


def uv_warning_message(cur_index):
    warning_message: str

    cur_index = round(cur_index, 1)

    if cur_index < 3:
        warning_message = 'LOW: If you burn easy, cover up and use sunscreen.'
    elif cur_index < 6:
        warning_message = 'MODERATE: Cover up and use sunscreen if you are outside.'
    elif cur_index < 8:
        warning_message = 'HIGH: Protection is needed! Cover up and use sunscreen. Reduce time outside.'
    elif cur_index < 10:
        warning_message = 'VERY HIGH: Be extra careful! Unprotected skin will be damaged and can burn quickly.'
    else:
        warning_message = 'EXTREME: Unprotected skin can burn in minutes. Avoid the sun, seek shade, wear a hat and sunglasses and use sunscreen.'

    return warning_message


def update_message(last_warning_msg: str):
    measurements, time_stamps = get_data_from_api()
    info_str = ''

    if len(measurements) > 0 and len(time_stamps) > 0:
        measurement = measurements[-1]
        time_stamp = time_stamps[-1]

        info_str = f'{time_stamp}: {measurement:.2f} '

        logging.info(info_str)

        return send_out(info_str, measurement, last_warning_msg, measurements, time_stamps)
    else:
        return last_warning_msg


def main():
    warning_msg = ""

    warning_msg = update_message(warning_msg)

    check_every_x_mins = 6

    while True:
        if datetime.now().hour >= 20:
            hours_until_start = 24 + STARTING_HOUR - datetime.now().hour

            print(f'good night, see you in {hours_until_start} hours')
            time.sleep(60*60*hours_until_start)
        elif datetime.now().hour < STARTING_HOUR:
            hours_until_start = STARTING_HOUR - datetime.now().hour

            print(f'good night, see you in {hours_until_start} hours')
            time.sleep(60*60*hours_until_start)

        if datetime.now().minute % check_every_x_mins == 0:
            if datetime.now().second <= 5:
                time.sleep(6)
                warning_msg = update_message(warning_msg)
                time.sleep(check_every_x_mins*60-10)
        else:
            time.sleep(60)


if __name__ == '__main__':
    main()
