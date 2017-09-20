"""
Operate a battery one step (one hour) at a time with a FileLoopProsumer using a household pattern
The battery can soften peaks and troughs, but only if it is used with knowledge of what to expect from the household
The household can also flex as necessary.


1. Charge the battery during low consumption times - i.e. pull more from the grid
2. Discharge the battery during high consumption times - i.e. pull less from the grid

"""
import logging
from datetime import datetime, timedelta
from random import random

from matplotlib import pyplot as plt

from battery import Battery
from dummies import FileLoopProsumer

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

max_capacity = 40
capacity = 40
max_charge_rate = 5
max_discharge_rate = -5

# randomise the battery a bit
battery = Battery(max_capacity, capacity, max_charge_rate, max_discharge_rate)

step = timedelta(hours=1)
household = FileLoopProsumer('data/household.txt')

thresholds = []
grid = []
battery_charge = []


try:
    for household_prosumption in household:
        log.info(battery.elapsed)

        # not-so-clever smarts set the battery charging threshold
        # when demand is below this, charge the battery, otherwise discharge
        # this could be more dynamic
        threshold = (sum(household.prediction(24)) / 24) * (battery.percent_full * 2)

        # control the battery based on the threshold
        battery.current_rate = household_prosumption - threshold

        # get the battery prosumption
        battery_prosumption = battery(step)

        # get some data for reporting
        thresholds.append(threshold) # a bit pointless with a static threshold
        battery_charge.append(battery.percent_full)

        # grid needs to balance the household
        grid.append(-(household_prosumption + battery_prosumption.sum()))

except KeyboardInterrupt:
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
    # fig, ax1 = plt.subplots(211)
    # ax2 = ax1.twinx()
    ax1.plot(household.history, color='red', alpha=0.5, lw=1, label="household") # this is the repeating pattern from the file
    ax1.plot(battery.history, color='black', alpha=0.5, lw=1, label="battery")   # this is the battery prosumption
    ax1.plot(thresholds, color='green', lw=0.5, label="threshold")    # this is the control threshold
    ax2.plot(grid, color='blue', lw=2, alpha=0.5, label="grid")       # this is the grid provision necessary to meet the total
    ax3.plot(battery_charge, color="black", lw=1, label="battery charge")
    ax1.legend()
    ax2.legend()
    ax3.legend()
    plt.show()
