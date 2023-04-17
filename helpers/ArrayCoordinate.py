import numpy as np
import astropy.units as u
from astropy.coordinates import EarthLocation

def getAntennaOffset(this_dict, ave_x, ave_y):
    "Calculates antenna offset from array average position"
    this_dict["offset"] ={}
    dz_arr = []
    for ix in range(len(this_dict['arr_x'])):
            dx = this_dict['arr_x'][ix] - ave_x
            dy = this_dict['arr_y'][ix] - ave_y
            dz = np.sqrt((dx*dx)+(dy*dy))
            dz_arr.append(dz)
    this_dict["offset"] = dz_arr
    return this_dict


class MidPositions:
    """ Class to deal with array properties for MID          """
    """ Expectation of data in x,y,z earth centric coordsys  """

    def __init__(self, datafile: str, dish_type: str = '', max_range: float = -1.0):
        self.datafile = datafile
        if self.datafile == '':
            print('No Array Coordinate initalised, using default of AncillData/mid_array_coords.dat')
            self.datafile = 'AncillData/mid_array_coords.dat'  # -- Expectation of data in x,y,z earth centric coordsys
        self.dish_type = dish_type  # -- MK or SKA dishes
        self.max_range = max_range # -- distance from geographic centre for 'core' type calcs
    
    def array_dict(self):
        mid_positions = np.genfromtxt(self.datafile, 
                            names = ['arr_x','arr_y','arr_z','diam','station'], 
                            dtype = 'f8,f8,f8,f8,U6')

        #--- Separate MK & SKA dishes as required
        dishes = {}
        names = ['arr_x','arr_y','arr_z','diam','station']

        if self.dish_type == '': #--- use both MK and SKA dishes.
            for name in names:
                dishes[name] = [mid_positions[name][x] for x in range(len(mid_positions['station']))]
        else: #--- use either MK or SKA dishes based on value of dish_type
            for name in names:
                dishes[name] = [mid_positions[name][x] for x in range(len(mid_positions['station'])) 
                                if mid_positions['station'][x].startswith(self.dish_type)]
        
        #--- Average position from whole array of selected dishes.
        ave_arr_x = np.average(dishes['arr_x'])
        ave_arr_y = np.average(dishes['arr_y'])
        ave_arr_z = np.average(dishes['arr_z'])

        #--- Calculate and add offset from whole array average position (x,y only)
        getAntennaOffset(dishes, ave_arr_x, ave_arr_y)

        if self.max_range == -1.0: #--- use full extent
            return_dishes = dishes
        else: #--- limit to dishes within a radius of max_range from full array average position
            core_dishes = {}
            names = ['arr_x','arr_y','arr_z','diam','station','offset']
            for name in names:
                core_dishes[name] = [dishes[name][x] for x in range(len(dishes['station']))
                                    if dishes['offset'][x] < self.max_range]    
            return_dishes = core_dishes

        return return_dishes
    
    
    def array_ave_position(self):
        dish_dict = self.array_dict()
        ave_arr_x = np.average(dish_dict['arr_x'])
        ave_arr_y = np.average(dish_dict['arr_y'])
        ave_arr_z = np.average(dish_dict['arr_z'])

        return {'ave_x': ave_arr_x, 'ave_y': ave_arr_y, 'ave_z': ave_arr_z}


class LowPositions:
    """ Class to deal with array properties for LOW          """
    """ Expect Lat, Long coords. converts to Geocentric xyz  """

    def __init__(self, datafile: str, max_range: float = -1.0):
        self.datafile = datafile
        if self.datafile == '':
            print('No Array Coordinate initalised, using default of AncillData/low_array_coords.dat')
            self.datafile = '../AncillData/low_array_coords.dat'  # -- Expectation of data in x,y,z earth centric coordsys
        self.max_range = max_range # -- distance from geographic centre for 'core' type calcs

    def array_dict(self):
        print(self.datafile)
        low_positions = np.genfromtxt(self.datafile, 
                            names = ['station_id','station_label','lon','lat'], 
                            dtype = 'i4,U5,f8,f8')
        
        #--- convert lat lon to x,y,z
        stations = {}
        names = ['station_id','station_label','lat','lon']

        for name in names:
            stations[name] = [low_positions[name][x] for x in range(len(low_positions['station_id']))]

        x_arr = []
        y_arr = []
        z_arr = []
        for ix in range(len(low_positions['station_id'])):
            val = EarthLocation.from_geodetic(low_positions['lon'][ix]*u.deg,
                                              low_positions['lat'][ix]*u.deg,
                                              300.0*u.m)
            x_arr.append(val.x.value)
            y_arr.append(val.y.value)
            z_arr.append(val.z.value)

        stations["arr_x"] = x_arr
        stations["arr_y"] = y_arr
        stations["arr_z"] = z_arr
        
        #--- Average position from whole array of selected stations.
        ave_arr_x = np.average(stations['arr_x'])
        ave_arr_y = np.average(stations['arr_y'])
        ave_arr_z = np.average(stations['arr_z'])
        
        #--- Calculate and add offset from whole array average position (x,y only)
        getAntennaOffset(stations, ave_arr_x, ave_arr_y)

        if self.max_range == -1.0: #--- use full extent
            return_stations = stations
        else: #--- limit to dishes within a radius of max_range from full array average position
            core_stations = {}
            names = ['station_id','station_label','lat','lon','arr_x','arr_y','arr_z','offset']
            for name in names:
                core_stations[name] = [stations[name][x] for x in range(len(stations['station_id']))
                                    if stations['offset'][x] < self.max_range]    
            return_stations = core_stations

        return return_stations

    def array_ave_position(self):
        stat_dict = self.array_dict()
        ave_arr_x = np.average(stat_dict['arr_x'])
        ave_arr_y = np.average(stat_dict['arr_y'])
        ave_arr_z = np.average(stat_dict['arr_z'])

        return {'ave_x': ave_arr_x, 'ave_y': ave_arr_y, 'ave_z': ave_arr_z}



