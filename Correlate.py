import Gather
import Encrypt
import numpy as np
import time
from matplotlib.pylab import matshow
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter


'''
README.md
1. 
2. describe classes 
3. describe apply_association

TODO:
1. think about whether or not circular difference is a useful concept for this particular use case
2. 
'''

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
        for pixel in self.index_pixels:
            self.index_pixels_hash[pixel.index] = pixel

    def update_index_pixels_hash(self):
        for pixel in self.index_pixels:
            self.index_pixels_hash[pixel.index] = pixel

    def average_difference( index_pixel_fixed, index_pixel_orbit):
        
        if(len(index_pixel_fixed.data) != len(index_pixel_orbit.data)): 
            
            raise ValueError( 'Length of Fixed:', len(index_pixel_fixed.data), 'Length of Orbit:',len(index_pixel_orbit.data), 'Different Datasets')
        return np.sum(np.absolute(np.subtract(index_pixel_fixed.data, index_pixel_orbit.data))) / len(index_pixel_fixed.data)

    def variance_of_difference(index_pixel_fixed, index_pixel_orbit):
        if(len(index_pixel_fixed.data) != len(index_pixel_orbit.data)): 
            
            raise ValueError( 'Length of Fixed:', len(index_pixel_fixed.data), 'Length of Orbit:',len(index_pixel_orbit.data), 'Different Datasets')
        return np.var(np.absolute(np.subtract(index_pixel_fixed.data, index_pixel_orbit.data)))

    def apply_association(self, association_type = variance_of_difference):
        association_lists = []
        for index_pixel in range(self.index_pixels_length):
            association_lists.append([])

        for index_pixel_fixed in range(self.index_pixels_length):
            # auto add self associative function
            association_lists[index_pixel_fixed].append([0.0, self.index_pixels[index_pixel_fixed].index])

            for index_pixel_orbit in range(index_pixel_fixed+1, self.index_pixels_length):
                association_value = association_type(self.index_pixels[index_pixel_fixed],  self.index_pixels[index_pixel_orbit])
                association_lists[index_pixel_fixed].append([association_value, self.index_pixels[index_pixel_orbit].index])
                association_lists[index_pixel_orbit].append([association_value, self.index_pixels[index_pixel_fixed].index])

        for index_pixel in range(self.index_pixels_length):
            association_lists[index_pixel] = sorted(association_lists[index_pixel], key= lambda x:x[1])
            association_lists[index_pixel] = np.array(association_lists[index_pixel], dtype=object)
            self.index_pixels[index_pixel].integrate_association_list(association_lists[index_pixel])

        self.update_index_pixels_hash()


    def pixel_select_history_graph(self, index, association_type = variance_of_difference):
        # pass in a tuple ex. (3,4)
        animation_association_graph = []
        for index_pixel in range(self.index_pixels_length):
            animation_association_graph.append(np.zeros((self.height, self.width)))
            animation_association_graph[index_pixel][index[0]][index[1]] = 0
        frame_counter = 1
        for row in range(self.height):
            for col in range(self.width):
                if((row, col) != index):
                    for future_frame in range(frame_counter, self.index_pixels_length):
                        animation_association_graph[future_frame][row][col] = association_type(self.index_pixels_hash[index], self.index_pixels_hash[(row, col)])
                    frame_counter += 1
        
        # now go back and normalize the association to max value 
        max_val = 0 ; min_non_zero = 1
        for row in range(self.height):
            for col in range(self.width):
                current_index = animation_association_graph[self.index_pixels_length-1][row][col]
                if(current_index > max_val): max_val = current_index
                if(current_index < min_non_zero and current_index != 0): min_non_zero = current_index

        min_non_zero*=0.99 ; max_val -= min_non_zero
        print(max_val)
        for frame in range(self.index_pixels_length):
            for row in range(self.height):
                for col in range(self.width):
                    animation_association_graph[frame][row][col] -= min_non_zero
                    animation_association_graph[frame][row][col] /= max_val
                    if(animation_association_graph[frame][row][col] <= 0): animation_association_graph[frame][row][col] = min_non_zero
                    #print(animation_association_graph[frame][row][col])

                    
        animation_association_graph[self.index_pixels_length - 1][self.height-1][self.width-1] = animation_association_graph[self.index_pixels_length - 1][self.height-1][self.width-2]
        print('\nMAX VALUE:',max_val,'\nMin Value', min_non_zero)
        return animation_association_graph

    def animate_image_matrix(self,history_graph, name):
        def update_frames(frame):

            return history_graph[frame]
        plt.rcParams['animation.ffmpeg_path'] = '/usr/local/Cellar/ffmpeg/5.1.1/bin/ffmpeg'
        fig = plt.figure()
        plot_frame = plt.imshow(history_graph[self.index_pixels_length - 1])
        
        plt.title(name)
        metadata = dict(title='Pixel Association History Graph', artist='John Brown')
        writer = FFMpegWriter(fps = 64, metadata=metadata)
       
        with writer.saving(fig, 'pixel_association_history_graph.mp4', dpi=100):
            for x in range(self.index_pixels_length):
                
                plot_frame.set_data(history_graph[x])
                writer.grab_frame()


        

        
        
        
        
        
print('UPDATED TWICE')

                



def pixel_association_test():
    # pull in data 
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='mnist', size = 3000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    # encrypt data
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    encrypted_validation_data = Encrypt.encrypt_batch(validation_data, random_arrangement_grid)
    # Correlation Testing
    picture_test = picture_pixel(test_data)
    #picture_test.apply_association()
    index_pixel_1 = picture_test.index_pixels_hash[(14,14)]
    index_pixel_2 = picture_test.index_pixels_hash[(14,13)]
    index_pixel_3 = picture_test.index_pixels_hash[(18,13)]
    index_pixel_4 = picture_test.index_pixels_hash[(14,12)]
    index_pixel_5 = picture_test.index_pixels_hash[(14,15)]
    print("MNIST PIXEL TEST:\nSIZE OF DATA: 3000\nFIXED PIXEL INDEX (14,14)\nSIMILAR PIXEL INDEX (14,13)\n",
            'VERY DIFFERENT PIXEL (18,13)\nOUTSIDE SIMILAR PIXEL (14,12)\nOTHER SIMILAR PIXEL (14,15)')
    print("\nSIMILAR PIXELS VS FIXED DIFFERENCE TEST")
    similar_average = picture_pixel.average_difference(index_pixel_1, index_pixel_2)
    similar_variance = picture_pixel.variance_of_difference(index_pixel_1, index_pixel_2)
    print(similar_average)
    print(similar_variance)

    print('\nVERY DIFFERENT PIXELS VS FIXED DIFFERENCE TEST')
    different_average = picture_pixel.average_difference(index_pixel_1, index_pixel_3)
    different_variance = picture_pixel.variance_of_difference(index_pixel_1, index_pixel_3)
    print(different_average)
    print(different_variance)

    print("RATIO OF DIFFERENCE in SIMILAR TO VERY DIFFERENT PIXELS\nAverage:",different_average/similar_average,
            '\nVariance:',different_variance/similar_variance)

    print("\nOUTSIDE SIMILAR VS FIXED DIFFERENCE TEST")
    
    outside_similar_average = picture_pixel.average_difference(index_pixel_1, index_pixel_4)
    outside_similar_variance = picture_pixel.variance_of_difference(index_pixel_1, index_pixel_4)
    print(outside_similar_average)
    print(outside_similar_variance)

    print("RATIO OF DIFFERENCE in SIMILAR TO OUTSIDE SIMILAR PIXELS\nAverage:",outside_similar_average/similar_average,
            '\nVariance:',outside_similar_variance/similar_variance)

    print('\nOTHER SIMILAR PIXEL VS FIXED TEST')
    other_similar_average = picture_pixel.average_difference(index_pixel_1, index_pixel_5)
    other_similar_variance = picture_pixel.variance_of_difference(index_pixel_1, index_pixel_5)
    print(other_similar_average)
    print(other_similar_variance)
    print('RATIO OF DIFFERENCE BETWEEN SIMILAR AND OTHER SIMILAR PIXELS\nAVERAGE:',other_similar_average/similar_average,
            '\nVARIANCE:',other_similar_variance/similar_variance)

    print('\t--------------------------------------------------\n',
        '\t--------------------------------------------------\n')
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='cifar10', size = 3000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    # encrypt data
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    encrypted_validation_data = Encrypt.encrypt_batch(validation_data, random_arrangement_grid)
    # Correlation Testing
    picture_test = picture_pixel(test_data)
    #picture_test.apply_association()
    index_pixel_1 = picture_test.index_pixels_hash[(14,14)]
    index_pixel_2 = picture_test.index_pixels_hash[(14,13)]
    index_pixel_3 = picture_test.index_pixels_hash[(18,13)]
    index_pixel_4 = picture_test.index_pixels_hash[(14,12)]
    index_pixel_5 = picture_test.index_pixels_hash[(14,15)]

    print("CIFAR PIXEL TEST:\nSIZE OF DATA: 3000\nFIXED PIXEL INDEX (14,14)\nSIMILAR PIXEL INDEX (14,13)\n",
            'VERY DIFFERENT PIXEL (18,13)\nOUTSIDE SIMILAR PIXEL (14,12)\nOTHER SIMILAR PIXEL (14,15)')
    print("\nSIMILAR PIXELS VS FIXED DIFFERENCE TEST")
    similar_average = picture_pixel.average_difference(index_pixel_1, index_pixel_2)
    similar_variance = picture_pixel.variance_of_difference(index_pixel_1, index_pixel_2)
    print(similar_average)
    print(similar_variance)

    print('\nVERY DIFFERENT PIXELS VS FIXED DIFFERENCE TEST')
    different_average = picture_pixel.average_difference(index_pixel_1, index_pixel_3)
    different_variance = picture_pixel.variance_of_difference(index_pixel_1, index_pixel_3)
    print(different_average)
    print(different_variance)

    print("RATIO OF DIFFERENCE in SIMILAR TO VERY DIFFERENT PIXELS\nAverage:",different_average/similar_average,
            '\nVariance:',different_variance/similar_variance)

    print("\nOUTSIDE SIMILAR VS FIXED DIFFERENCE TEST")
    
    outside_similar_average = picture_pixel.average_difference(index_pixel_1, index_pixel_4)
    outside_similar_variance = picture_pixel.variance_of_difference(index_pixel_1, index_pixel_4)
    print(outside_similar_average)
    print(outside_similar_variance)

    print("RATIO OF DIFFERENCE in SIMILAR TO OUTSIDE SIMILAR PIXELS\nAverage:",outside_similar_average/similar_average,
            '\nVariance:',outside_similar_variance/similar_variance)

    print('\nOTHER SIMILAR PIXEL VS FIXED TEST')
    other_similar_average = picture_pixel.average_difference(index_pixel_1, index_pixel_5)
    other_similar_variance = picture_pixel.variance_of_difference(index_pixel_1, index_pixel_5)
    print(other_similar_average)
    print(other_similar_variance)
    print('RATIO OF DIFFERENCE BETWEEN SIMILAR AND OTHER SIMILAR PIXELS\nAVERAGE:',other_similar_average/similar_average,
            '\nVARIANCE:',other_similar_variance/similar_variance)

def animate_pixel_select_history_test():
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='cifar10', size = 2000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    # encrypt data
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    picture_test_data = picture_pixel(test_data)
    picture_test_data.apply_association()

    index = (5,5)
    test_data_animation_association_graph = picture_test_data.pixel_select_history_graph(index)

    picture_test_data.animate_image_matrix(test_data_animation_association_graph, 'cifar10 pixel association graph (5,5)')

animate_pixel_select_history_test()



