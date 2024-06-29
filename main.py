import requests
import json
from datetime import datetime, timedelta
import telebot
import time
import web_img
from helper import API_URL_IBK, WEB_URL_IBK, TELEGRAM_TOKEN, CHANNEL_NAME
import logging


def convert_time_stamps(time_stamps: list[str]):
    for i in range(len(time_stamps)):
        time_stamps[i] = datetime.strptime(
            time_stamps[i], '%Y-%m-%dT%H:%M:%S+0000') + timedelta(hours=2)

    return time_stamps


def get_data_from_api():
    r = requests.get(API_URL_IBK)

    content = json.loads(r.content.decode('utf-8'))

    uve = content['Innsbruck']['uve']

    max_expected = uve['max_expected_value']
    measurements = uve['measurement']
    time_stamps = uve['ts']
#    unit = uve['unit']
#    url_highres = uve['url_higres']

    time_stamps = convert_time_stamps(time_stamps)

    return max_expected, measurements, time_stamps


def send_to_bot(msg: str, cur_index: float, last_msg: str):

    msg += '\n' + uv_warning_message(cur_index)
    msg += f'\nInformation taken from:\n{WEB_URL_IBK}'
    print(TELEGRAM_TOKEN)
    bot = telebot.TeleBot(token=TELEGRAM_TOKEN)
    print(bot.get_me())
    cur_img = web_img.get_current_image()

    if msg != last_msg:
        if cur_img is not None:
            logging.info(cur_img)
            bot.send_photo(chat_id=CHANNEL_NAME, photo=cur_img, caption=msg)
        else:
            bot.send_message(chat_id=CHANNEL_NAME, text=msg)
    return msg


def uv_warning_message(cur_index):
    warning_message: str

    if cur_index < 3:
        warning_message = 'uv currently not dangerous'
    elif cur_index < 6:
        warning_message = 'moderate uv, better get sunscreen'
    elif cur_index < 8:
        warning_message = 'high uv, try to stay in the shadows and better GET SUNSCREEN'
    elif cur_index < 10:
        warning_message = 'very high uv, stay in the shadows!'
    else:
        warning_message = 'EXTREME uv, stay indoors!'

    return warning_message


def update_message(last_msg: str):
    max_expected, measurements, time_stamps = get_data_from_api()
    info_str = ''
    cur_index = -1

    for measurement, time_stamp in zip(measurements, time_stamps):
        relative_to_max = measurement/max_expected

        info_str = f'{time_stamp}: {measurement:.2f} of max {
            max_expected} ({relative_to_max*100:.0f}%)'

        logging.info(info_str)

    return send_to_bot(info_str, cur_index, last_msg)


def main():
    msg = update_message('')

    while True:
        if datetime.now().minute % 1 == 0:
            if datetime.now().second <= 5:
                time.sleep(6)
                msg = update_message(msg)
                time.sleep(50)
        else:
            time.sleep(1)

        if datetime.now().hour >= 20:
            logging.info('good night')
            time.sleep(60*60*10)


if __name__ == '__main__':
    main()
