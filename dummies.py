"""
Simple classes which stub out some of the features of prosumers without much smartness or connection with reality
These explorations are intended to extract the requirements and articulate the implicit design decisions we make in the process.

We have implemented different API's for these prosumers with the intention of eventually converging them

"""
import numpy as np
import random

class RandomWalk:
    """
    the random walk prosumer represents the challenge of a changing prosumption landscape
    Its implemented as a simple iterator which grows a history list
    There is no way to replay history, it just keeps going
    """
    def __init__(self, sigma):
        self.mean = 0
        self.sigma = sigma
        self.history = [0]

    def __iter__(self):
        return self

    def __next__(self):
        result = self.history[-1]
        self.history.append(result + random.normalvariate(self.mean, self.sigma))
        return result


class NormalProsumer:
    """
    the normal prosumer operates at a flat level of power prosumption with some noise which follows a normal distribution
    It might represent a dimmable streetlight or variable speed drive or some other controllable load
    It can be controlled by setting the "mean" property
    It operates at a given resolution for experimental reasons I guess
    Though it may have little or no effect, it actually ensures the uncertainty is correctly applied.
    Over long periods we can be very sure about what we will do (if the mean is not changed)
    """
    def __init__(self, mean, stdev, resolution):
        self.mean = mean
        self.stdev = stdev
        self.resolution = resolution # A timedelta object

    def _n_steps(self, td):
        """calculate number of steps to predict based on resolution and requested timestamp"""
        return int(td.total_seconds() / self.resolution.total_seconds())

    def prosumption(self, dt, td):
        return np.random.normal(self.mean, self.stdev, self._n_steps(td))

    def prediction(self, dt, td):
        return self.prosumption(dt, td).sum()



class FileLoopProsumer:
    """
    The file loop prosumer is an attempt to emulate something like the typical demand of a building (e.g. household or school)
    It operates according to a schedule taken from a file but has the ability to flex if necessary.
    Each hour of the day it has a core target, an uncertainty and an ability to flex.
    Within each hour, it might use a normal prosumer to make predictions
    The difference is that it is schedulable, within limits
    This currently does not take into account movement of load, it allows total prosumption to change

    This is untested so probably doesn't work
    """
    def __init__(self, file_path):
        with open(file_path, 'r') as f:
            self._data = np.array([row.split() for row in np.array(f.read().splitlines())])
        self._plan = [0] * len(self._data) # this is the actual flex to apply, it can change
        self.index = 0
        self.history = []

    def __len__(self):
        return len(self._data)

    @property
    def target(self):
         return float(self._data[self.index,0])

    @property
    def uncertainty(self):
         return float(self._data[self.index,1])

    @property
    def ability_to_flex(self):
         return float(self._data[self.index,2])

    @property
    def ability_to_flex(self):
         return float(self._data[self.index,2])

    @property
    def flex(self):
        return self._plan[self.index]

    @flex.setter
    def flex(self, value):
        if value > 0:
            self._plan[self.index] = min(self.ability_to_flex, value)
        else:
            self._plan[self.index] = max(self.ability_to_flex * -1, value)

    def plan(self, n_steps):
        return [self._plan[(self.index + step) % len(self._plan)] for step in range(n_steps)]

    def prediction(self, n_steps):
        indices = [(self.index + step) % len(self._plan) for step in range(n_steps)]
        return [self._plan[i] + float(self._data[i, 0]) for i in indices]

    def _step(self):
        self.index += 1
        self.index %= len(self._data)

    def __iter__(self):
        return self

    def __next__(self):
        self._step()
        noise = self.uncertainty * (random.random() - 0.5)
        result = self.target + self.flex + noise
        self.history.append(result)
        return result
