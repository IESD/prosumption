"""charging the battery is negative prosumption, draining the battery is positive prosumption"""

import logging
import numpy as np
from datetime import timedelta

log = logging.getLogger()


class Battery:
    def __init__(self, max_capacity, capacity, max_charge_rate, max_discharge_rate):
        self.max_capacity = max_capacity
        self.capacity = capacity
        self.max_charge_rate = max_charge_rate
        self.max_discharge_rate = max_discharge_rate
        self.current_rate = 0
        self.elapsed = timedelta(seconds=0)
        self.history = []
        self.capacity_history = []

    @property
    def actual_rate(self):
        return -min(max(self.current_rate, self.max_discharge_rate), self.max_charge_rate)

    @property
    def percent_full(self):
        return 1 - (self.capacity / self.max_capacity)

    @property
    def reservoir(self):
        return self.max_capacity - self.capacity

    def prediction(self, td):
        count = int(td.total_seconds() / 3600) # one hour max
        result = np.zeros(count)
        result.fill(self.actual_rate)
        cusum = result.cumsum()
        result[np.where(result > self.capacity)] = 0
        # result[np.where(result < 0)] = 0
        return result

    def charge(self):
        self.current_rate = self.max_charge_rate

    def discharge(self):
        self.current_rate = self.max_discharge_rate

    def __call__(self, td):
        """
        Operates for timedelta

        This means we need to know when it is, how far since we were initialised
        So we need to increment our elapsed time
        """
        self.elapsed += td
        planned_prosumption = self.prediction(td)      # e.g. -5
        total_prosumption = planned_prosumption.sum()  # e.g. -5
        would_be_capacity = self.capacity - total_prosumption # e.g. 45
        if 0 <= would_be_capacity <= self.max_capacity:
            self.capacity -= total_prosumption
        else:
            log.debug("hit limit")
            self.current_rate = 0
            planned_prosumption = self.prediction(td)
        self.history.append(sum(planned_prosumption))
        self.capacity_history.append(self.capacity)
        return planned_prosumption

    def __repr__(self):
        return "Battery({}, {:.0%} ({:+.02f}))".format(self.elapsed, self.percent_full, self.actual_rate)


if __name__ == "__main__":
    """
    Operate a battery one step (one hour) at a time
    the demand on the battery is a clipped random walk (we cannot demand more than the battery can provide)
    """
    from datetime import datetime, timedelta
    from random import random

    logging.basicConfig(level=logging.INFO)

    battery = Battery(10000, 5000, 10, -20)
    step = timedelta(hours=1)
    year = []
    years = []
    try:
        while True:
            battery.current_rate = battery.actual_rate + (random() - 0.5)
            hour = battery(step)

            # record some data
            year.extend(hour)
            if len(year) >= 365 * 24:
                years.append(sum(year))
                year = []
                log.info(battery)

    except KeyboardInterrupt:
        print("")
        print("years: {}".format(len(years)))
        print("year: {}".format(len(year)))
