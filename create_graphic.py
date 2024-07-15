from datetime import datetime
from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import norm
from typing import List

palette = {
    0: '#4eb400',
    1: '#4eb400',
    2: '#a0ce00',
    3: '#f7e400',
    4: '#f8b600',
    5: '#f88700',
    6: '#f85900',
    7: '#e82c0e',
    8: '#d8001d',
    9: '#ff0099',
    10: '#b54cff',
    11: '#998cff'
}

TIME_START = 5
TIME_STOP = 21
TIME_STEP = 0.5
TIME_MEAS_NUM = int((TIME_STOP - TIME_START)/TIME_STEP)

IMG_PATH = './plot.png'


hline_values = [3, 6, 8, 10]

annotations = {
    'LOW': ((6, 1.25), 2),
    'MODERATE': ((6, 4.25), 4),
    'HIGH': ((6, 6.75), 7),
    'VERY HIGH': ((6, 8.75), 9),
    'EXTREME': ((6, 11), 11)
}

gauss_max_values = {
    7: 9,
    8: 8.5
}


def create_gauss(hours: List[float]):
    mu = 13.35
    sigma = 2.59

    gauss_max = gauss_max_values[datetime.now().month]

    gaussian: np.ndarray = np.array([])

    for hour in hours:
        gaussian = np.append(gaussian, norm.pdf(hour, loc=mu, scale=sigma))

    gaussian = gaussian / max(gaussian) * gauss_max

    return gaussian


def make_default_hours():
    timestamps = list()
    for i in np.arange(TIME_START, TIME_STOP, TIME_STEP):
        timestamps.append(i + 0.25)
    return timestamps


def fix_measurements(measurements):
    fixed_measurements = np.zeros((TIME_MEAS_NUM,))

    for i in range(len(measurements)):
        fixed_measurements[i] = measurements[i]

    return fixed_measurements


def make_hours(timestamps: List[datetime]):
    hours: List[float] = list()

    for timestamp in timestamps:
        hours.append(timestamp.hour + timestamp.minute/60)

    return hours


def prepare_data(data_measurements: List[float],
                 data_timestamps: List[datetime]):

    data_hours = make_hours(data_timestamps)

    prep_measurements: List[float] = [0]*TIME_MEAS_NUM
    prep_hours: List[float] = make_default_hours()

    for i in range(len(prep_hours)):

        cur_hour = prep_hours[i]

        try:
            data_pos = data_hours.index(cur_hour)
            prep_measurements[i] = data_measurements[data_pos]
        except ValueError as err:
            prep_measurements[i] = 0

    return prep_measurements, prep_hours


def make_colorlist(values: List[float]):
    colorlist: List[str] = list()

    for value in values:

        c_index = int(value)

        if c_index > 11:
            c_index = 11

        colorlist.append(palette[c_index])

    return colorlist


def create_image(data_measurements: list[float], data_timestamps: list[datetime]):

    measurements, hours = prepare_data(data_measurements, data_timestamps)

    gauss_hours = np.linspace(start=hours[0], stop=hours[-1], num=len(hours)*4)
    gaussian = create_gauss(gauss_hours)

    fig, ax = plt.subplots(figsize=(6, 3), dpi=300)

    ax.fill_between(x=gauss_hours, y1=gaussian, color='#DDDDDD', zorder=0)
    ax.plot(gauss_hours, gaussian, color='#AAAAAA', zorder=1)
    ax.bar(hours, measurements, color=make_colorlist(
        measurements), width=0.45, zorder=2)

    for hline_val in hline_values:
        ax.axhline(hline_val, color=palette[hline_val])

    for annotation, ann_info in annotations.items():
        xy = ann_info[0]
        color = palette[ann_info[1]]
        plt.annotate(annotation, xy, color=color)

    plt.suptitle(f"Innsbruck {datetime.now().strftime('%d.%m.%Y')}")

    max_yval = max(*measurements, *gaussian)
    plt.yticks([y for y in range(0, int(max_yval)+2)])

    plt.xticks([x for x in range(int(TIME_START), int(TIME_STOP)+1)])
    ax.set_xlim(left=hours[0]-0.25, right=hours[-1]+0.25)

    plt.grid(alpha=0.3)

    plt.xlabel('Time')
    plt.ylabel('UV-Index')

    # plt.tight_layout()

    plt.savefig(IMG_PATH, pad_inches=0.1, bbox_inches='tight')


def test(x: int):
    from uibkapi import get_data_from_api

    measurements, timestamps = get_data_from_api()

    create_image(measurements, timestamps)


if __name__ == '__main__':
    test(11)
