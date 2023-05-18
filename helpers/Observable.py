import astropy.units as u
import re
import numpy as np
from astropy.time import Time
from datetime import datetime
from helpers.ArrayCoordinate import MidPositions, LowPositions
from astropy.coordinates import AltAz, EarthLocation, SkyCoord, ICRS, Longitude
from helpers.TimeRange import TimeRange
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

class Observable:

    """Turn into a single Command

    Observable(array,target_dict,start_time,obs_period, obs_period_unit)

    Basic function of single command
    - Do a Rise/Set plot
    - Give Rise/Set times for sources

    Extensions... (or from the helpers alone)
    - read an SB JSON and make the plot.

    """

    def __init__(self, array: str, target_dict: dict, start_time: str = 'now', 
                 obs_period: float = 24.0,  obs_period_unit: str = 'h'):
        self.array = array
        self.target_dict = target_dict
        self.start_time = start_time
        self.obs_period = obs_period
        self.obs_period_unit = obs_period_unit

    def generate_observability_data(self):
        """Generate observability data"""
        desired_array = self.array

        """ Array config """
        
        if desired_array == 'Mid':
            print("Array:"+desired_array+"\nUsing only SKA dishes ")
            dishes = MidPositions('AncillData/mid_array_coords.dat','SKA')
            average_position = dishes.array_ave_position()
            geographic_location = EarthLocation.from_geocentric(average_position['ave_x'],
                                                                average_position['ave_y'],
                                                                average_position['ave_z'],unit=u.m)
            utcoffset = +2#*u.hour
            time_now = Time(datetime.utcnow(), scale='utc') - utcoffset
            time_zone = '[SAST]'
            
        elif desired_array == 'Low':
            print("Array:"+desired_array)
            station = LowPositions('AncillData/low_array_coords.dat')
            average_position = station.array_ave_position()
            geographic_location = EarthLocation.from_geocentric(average_position['ave_x'],
                                                                average_position['ave_y'],
                                                                average_position['ave_z'],unit=u.m)
            utcoffset = +8#*u.hour
            time_now = Time(datetime.utcnow(), scale='utc') - utcoffset
            time_zone = '[AWST]'
        else:
            print("That is not an SKA Telescope ")

        """ Time Stuff """
        print(self.obs_period, self.obs_period_unit)
        obs_time = TimeRange(obs_period_start = self.start_time, 
                              obs_period_length = self.obs_period, 
                              obs_period_unit = self.obs_period_unit, 
                              utcoffset= utcoffset,
                              plotsteps = int(self.obs_period*10.))

        # obs_time_delta = obs_time.obs_period_delta()
        return obs_time, geographic_location, time_zone

    def provide_plot(self):
        target_dict = self.target_dict

        obs_time, geographic_location, time_zone = self.generate_observability_data()

        obs_time_delta = obs_time.obs_period_delta()

        fig_rs = plt.figure(1, figsize=(12,8))
        ax_rs = fig_rs.add_subplot(111)

        #-- set up the 
        ax_rs.set_xlabel('Local Time '+time_zone)
        ax_rs.set_ylabel('Altitude [deg]')
        ax_rs.hlines(y = 15.0, xmin = 0, xmax = len(obs_time_delta), linestyle = '--', color = 'k', label='elevation limit')
        ax_rs.set_xlim([0.0,len(obs_time_delta)])
        ax_rs.set_ylim([0.0,90.0])

        for target_name, target_coord in target_dict.items():
            """Conver coords to astropy Skycoord instance"""
            target_coord_sky = SkyCoord(target_coord, frame = 'icrs', unit = (u.hourangle, u.deg))
            """Convert target coords to Az_el (called AltAz in astropy)"""
            target_azel = target_coord_sky.transform_to(AltAz(obstime = obs_time_delta,
                                                    location = geographic_location))
            """Plot"""
            ax_rs.plot(obs_time_delta.value,
                    target_azel.alt,
                    label = target_name)

        tick_spacing = 20
        ax_rs.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing+1))
        ax_rs.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol = len(target_dict)+1
                    , fontsize = 16.0)
        plt.gcf().autofmt_xdate()
        plt.show()

    def provide_rise_set(self):
        target_dict = self.target_dict
        obs_time, geographic_location, time_zone = self.generate_observability_data()
        obs_time_delta = obs_time.obs_period_delta()
        ellim = 15.0

        for target_name, target_coord in target_dict.items():
            """Conver coords to astropy Skycoord instance"""
            target_coord_sky = SkyCoord(target_coord, frame = 'icrs', unit = (u.hourangle, u.deg))
            """Convert target coords to Az_el (called AltAz in astropy)"""
            target_azel = target_coord_sky.transform_to(AltAz(obstime = obs_time_delta,
                                                    location = geographic_location))
            
            
        
            print(target_name)
            index_above_ellim = np.where(np.asarray(target_azel.alt.value) >= ellim)[0]

            if len(index_above_ellim) == len(np.asarray(target_azel.alt.value)):
                print("Source never goes below elevation limit for specified time")
            elif len(index_above_ellim) == 0:
                print("Source never goes above elevation limit for specified time")
            else:                                 
                for idx in index_above_ellim:
                    if idx + 1 >= len(obs_time_delta.value):
                        print("Next source Set/Rises after specificed time range")
                    else:
                        if target_azel.alt.value[idx - 1] < ellim:
                            print("rising between: "+str(obs_time_delta.value[idx - 1])+" and "+obs_time_delta.value[idx])
                            # dx = (obs_time_delta[idx] - obs_time_delta[idx - 1])*(24.*60.)*u.min   #--- Minutes
                            # dy = target_azel.alt.value[idx - 1] - target_azel.alt.value[idx] #--- Degrees
                        elif target_azel.alt.value[idx + 1] < ellim:
                            print("setting between: "+str(obs_time_delta.value[idx])+" and "+obs_time_delta.value[idx + 1])

            




########------------------------------###########
"""                TEST LINES                 """
########------------------------------###########


# target_dict = {'1646-50': "21:08:46.86357 -50:44:48.37", 
#                '1934-638': "19:39:25.026 -63:42:45.63", 
#                '1921-293': "19:24:51.055957 -29:14:30.121150",
#                'sdc335': "16:30:58.638 -48:43:51.70"}

# test_Obs = Observable('Mid',target_dict,'2023-7-5 10:00:01',102.0, 'h')
# print(test_Obs.provide_rise_set())


# obs_time = TimeRange(obs_period_start = '2023-7-5 10:00:01', 
#                               obs_period_length = 24.0, 
#                               obs_period_unit = 'h', 
#                               utcoffset= -2.0,
#                               plotsteps = 200)

# print(obs_time)