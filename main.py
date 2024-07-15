from datetime import datetime
import telebot
import time
from create_graphic import create_image, IMG_PATH
from helper import WEB_URL_IBK, TELEGRAM_TOKEN, CHANNEL_NAME
import logging
from uibkapi import get_data_from_api
import os.path

STARTING_HOUR = 7

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

    create_image(measurements, time_stamps)

    if os.path.exists(IMG_PATH):
        bot.send_photo(chat_id=CHANNEL_NAME, photo=open(IMG_PATH,'rb'), caption=msg)
    else:
        bot.send_message(chat_id=CHANNEL_NAME, text=msg)
    return warning_msg


def uv_warning_message(cur_index):
    warning_message: str

    cur_index = round(cur_index, 1)

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

    if len(measurements) > 0 and len(time_stamps) > 0:
        measurement = measurements[-1]
        time_stamp = time_stamps[-1]

        info_str = f'{time_stamp}: {measurement:.2f} '

        logging.info(info_str)

        return send_to_bot(info_str, measurement, last_warning_msg, measurements, time_stamps)
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
