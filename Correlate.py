import Gather
import Encrypt
import numpy as np

class index_pixel:
    def __init__(self, index):
        self.index = index

    def collect_data(self, data):
        self.data = []
        for picture in data:
            self.data.append(picture[self.index[0]][self.index[1]])
        self.data = np.array(self.data)
    

class picture_pixel:
    def __init__(self, data):
        self.pixels = []
        dimension_sample = Gather.pull_sample(data, picture_only=True)
        for row in range(len(dimension_sample)):
            for col in range(len(dimension_sample[row])):
                new_index_pixel = index_pixel((row, col))
                new_index_pixel.collect_data(data)
                self.pixels.append[new_index_pixel]

    def average_difference(index_pixel_fixed, index_pixel_orbit):
        
        if(len(index_pixel_fixed.data) != len(index_pixel_orbit.data)): 
            
            raise ValueError( 'Length of Fixed:', len(index_pixel_fixed.data), 'Length of Orbit:',len(index_pixel_orbit.data), 'Different Datasets')
        return np.sum(np.absolute(np.subtract(index_pixel_fixed.data, index_pixel_orbit.data))) / len(index_pixel_fixed.data)
           
    def apply_association(association_type = average_difference):
        pass
        



def working_test():
    # pull in data 
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(size = 500)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    # encrypt data
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    encrypted_validation_data = Encrypt.encrypt_batch(validation_data, random_arrangement_grid)
    # Correlation Testing
    test_index_pixel_1 = index_pixel((0,0))
    test_index_pixel_2 = index_pixel((10,10))
    test_index_pixel_1.collect_data(test_data[0:500])
    test_index_pixel_2.collect_data(test_data[0:500])



        


working_test()


