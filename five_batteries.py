"""
Operate five batteries one step (one hour) at a time with a random walk prosumer
The batteries absorb most of the consumption and pass on a flat line to the grid where they can.
"""
import logging
from datetime import datetime, timedelta
from random import random

from matplotlib import pyplot as plt

from battery import Battery
from dummies import RandomWalk

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

max_capacity = 100000
max_charge_rate = 10
max_discharge_rate = -10

batteries = [Battery(max_capacity, random() * max_capacity, random() * max_charge_rate, random() * max_discharge_rate) for i in range(5)]
step = timedelta(hours=1)
result = []
walk = RandomWalk(0.1)
try:
    for demand in walk:
        if demand < 0:
            batteries.sort(key=lambda battery: battery.capacity)
        else:
            batteries.sort(key=lambda battery: battery.reservoir)
        for i, battery in enumerate(batteries):
            battery.current_rate = demand
            hour = battery(step)
            demand -= hour.sum()
        log.info(batteries)
        result.append(demand)

except KeyboardInterrupt:
    fig, ax1 = plt.subplots()
    for b in batteries:
        ax1.plot(b.capacity_history, color='black', lw=0.5)
    ax2 = ax1.twinx()
    ax2.plot(walk.history, color='red', lw=2)
    ax2.plot(result, color='blue', lw=2)
    plt.show()
