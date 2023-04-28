import astropy.units as u
import re
import numpy as np
from astropy.time import Time
from datetime import datetime


class TimeRange:
    """ Class to handle time ranges for RiseSet plots         """
    """ All inputs sould be in UTC but are converted to Local """

    def __init__(self, obs_period_start: str = 'now', obs_period_length: float = 24.0, 
                 obs_period_unit: str = 'h', utcoffset: float = 0.0, plotsteps: int = 100):
        self.obs_period_unit = obs_period_unit
        self.utcoffset = utcoffset
        self.obs_period_start = obs_period_start
        self.plotsteps = plotsteps

        if self.obs_period_unit == 'h':
            self.obs_period_length = obs_period_length*u.hour
        elif self.obs_period_unit == 'm':
            self.obs_period_length = obs_period_length*u.minute

        if obs_period_start == 'now':
            self.obs_period_start = Time(datetime.utcnow(), scale='utc') + self.utcoffset*u.hour
        else:
            date_regex = re.compile(r'\d\d\d\d-\d-\d \d\d:\d\d:\d\d|\d\d\d\d-\d\d-\d \d\d:\d\d:\d\d|\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d')
            match_data = date_regex.match(self.obs_period_start)
            if match_data:
                self.obs_period_start = Time(self.obs_period_start) + self.utcoffset*u.hour

    def obs_period_delta(self):
        obs_start =  self.obs_period_start# LOCAL
        obs_end = obs_start + self.obs_period_length       

        #-- generate linear time steps to plot over
        steps = self.plotsteps
        delta = obs_end-obs_start

        obs_period_delta = obs_start + delta * np.linspace(0.,1., steps)
        return obs_period_delta
