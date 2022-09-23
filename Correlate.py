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

    def integrate_association_list(self, association_list):
        self.association_list = association_list

class picture_pixel:
    def __init__(self, data):
        self.index_pixels = [] ; self.index_pixels_hash = {}
        self.height, self.width, self.depth = Gather.pull_sample(data, picture_only=True).shape
        
        for row in range(self.height):
            for col in range(self.width):
                new_index_pixel = index_pixel((row, col))
                new_index_pixel.collect_data(data)
                self.index_pixels.append(new_index_pixel)
        self.index_pixels = np.array(self.index_pixels)
        self.index_pixels_length = len(self.index_pixels)

    def update_index_pixels_hash(self):
        for pixel in self.index_pixels:
            self.index_pixels_hash[pixel.index] = pixel

    def average_difference(index_pixel_fixed, index_pixel_orbit):
        
        if(len(index_pixel_fixed.data) != len(index_pixel_orbit.data)): 
            
            raise ValueError( 'Length of Fixed:', len(index_pixel_fixed.data), 'Length of Orbit:',len(index_pixel_orbit.data), 'Different Datasets')
        return np.sum(np.absolute(np.subtract(index_pixel_fixed.data, index_pixel_orbit.data))) / len(index_pixel_fixed.data)
           
    def apply_association(self, association_type = average_difference):
        
        for index_pixel_fixed in range(self.index_pixels_length):
            association_list = []
            for index_pixel_orbit in range(0, self.index_pixels_length):
                association_list.append([association_type(self.index_pixels[index_pixel_fixed],  self.index_pixels[index_pixel_orbit]), self.index_pixels[index_pixel_orbit].index])
            association_list = np.array(association_list, dtype=object)
            self.index_pixels[index_pixel_fixed].integrate_association_list(association_list)

        self.update_index_pixels_hash()


        
    
                



def working_test():
    # pull in data 
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(size = 500)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    # encrypt data
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    encrypted_validation_data = Encrypt.encrypt_batch(validation_data, random_arrangement_grid)
    # Correlation Testing
    '''
    test_index_pixel_1 = index_pixel((0,0))
    test_index_pixel_2 = index_pixel((10,10))
    test_index_pixel_1.collect_data(test_data[0:500])
    test_index_pixel_2.collect_data(test_data[0:500])
    '''
    test_picture_pixel = picture_pixel(test_data)
    test_picture_pixel.apply_association()
    print(test_picture_pixel.index_pixels[0].association_list[0:40], '\n',test_picture_pixel.index_pixels_hash[(0,0)].association_list)

    specific_pixel_0_0 = test_picture_pixel.index_pixels_hash[(0,0)]
    specific_pixel_0_1 = test_picture_pixel.index_pixels_hash[(0,1)]
    print(specific_pixel_0_0.association_list[0:5],'\n',specific_pixel_0_1.association_list[0:5])


        


working_test()


