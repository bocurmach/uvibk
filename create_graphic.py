from datetime import datetime
from matplotlib import pyplot as plt


def create_image(measurements: list[float], timestamps: list[datetime]):
    bar_plot = plt.bar(timestamps, measurements)
    plt.savefig('plot')


def test(x: int):
    timestamps = list()
    measurements = list()

    for i in range(x):
        timestamps.append(datetime(2024, 7, 4, i, 0, 0))
        measurements.append(i*1.1)

    create_image(measurements, timestamps)


if __name__ == '__main__':
    test(5)
