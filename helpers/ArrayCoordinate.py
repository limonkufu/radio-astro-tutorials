import numpy as np

def getAntennaOffset(this_dict, ave_x, ave_y):
    "Calculates antenna offset from array average position"
    this_dict["offset"] ={}
    dz_arr = []
    for ix in range(len(this_dict['station'])):
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
        print(self.datafile)
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


# ska_dishes = MidPositions(datafile='',dish_type='SKA',max_range=1000.0)

# print(ska_dishes.array_ave_position())

