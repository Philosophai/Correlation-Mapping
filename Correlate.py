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

def diagonal_difference_hypothesis_test(dataset = 'cifar10', index = (14,14), is_subroutine = False):
    # edit to choose dataset and center index
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset=dataset, size = 2000)
    picture_test = picture_pixel(test_data)
    #picture_test.apply_association()
    if(not is_subroutine):
        print("CREATING INDICES for diagonal difference Hypothesis test\n")
    center = picture_test.index_pixels_hash[index]
    row = index[0] ; col = index[1]

    VH_up = picture_test.index_pixels_hash[(row + 1, col)]
    VH_down = picture_test.index_pixels_hash[(row - 1,col)]
    VH_left = picture_test.index_pixels_hash[(row,col - 1)]
    VH_right = picture_test.index_pixels_hash[(row,col + 1)]
    VH = [VH_up, VH_down, VH_left, VH_right] ; VH_av = 0 ; VH_diff = []

    diag_ul = picture_test.index_pixels_hash[(row + 1,row - 1)]
    diag_ur = picture_test.index_pixels_hash[(row + 1,col + 1)]
    diag_dl = picture_test.index_pixels_hash[(row - 1,col - 1)]
    diag_dr = picture_test.index_pixels_hash[(row - 1,col + 1)]
    diag = [diag_ul, diag_ur, diag_dl, diag_dr] ; diag_av = 0 ; diag_diff = []

    outer_VH_up = picture_test.index_pixels_hash[(row + 2,col)]
    outer_VH_down  = picture_test.index_pixels_hash[(row - 2,col)]
    outer_VH_left= picture_test.index_pixels_hash[(row,col - 2)]
    outer_VH_right = picture_test.index_pixels_hash[(row, col + 2)]
    outer_VH = [outer_VH_up, outer_VH_down, outer_VH_left, outer_VH_right] ; outer_VH_av = 0 ; outer_VH_diff = []

    inner_diag_ul = picture_test.index_pixels_hash[(row+2,col - 1)]
    inner_diag_ur = picture_test.index_pixels_hash[(row + 2,col + 1)]
    inner_diag_dl = picture_test.index_pixels_hash[(row - 2,col - 1)]
    inner_diag_dr = picture_test.index_pixels_hash[(row - 2, col + 1)]
    inner_diag = [inner_diag_ul, inner_diag_ur, inner_diag_dl, inner_diag_dr] ; inner_diag_av = 0 ; inner_diag_diff = []

    outer_diag_ul = picture_test.index_pixels_hash[(row + 2,col - 2)]
    outer_diag_ur = picture_test.index_pixels_hash[(row + 2,col + 2)]
    outer_diag_dl = picture_test.index_pixels_hash[(row - 2,col - 2)]
    outer_diag_dr = picture_test.index_pixels_hash[(row - 2,col + 2)]
    outer_diag = [outer_diag_ul, outer_diag_ur, outer_diag_dl, outer_diag_dr] ; outer_diag_av = 0 ; outer_diag_diff = []

    for x in range(4):
        VH_diff.append(picture_pixel.variance_of_difference(center, VH[x]))
        VH_av += VH_diff[x]

        outer_VH_diff.append(picture_pixel.variance_of_difference(center, outer_VH[x]))
        outer_VH_av += outer_VH_diff[x]

        diag_diff.append(picture_pixel.variance_of_difference(center, diag[x]))
        diag_av += diag_diff[x]

        inner_diag_diff.append(picture_pixel.variance_of_difference(center, inner_diag[x]))
        inner_diag_av += inner_diag_diff[x]

        outer_diag_diff.append(picture_pixel.variance_of_difference(center, outer_diag[x]))
        outer_diag_av += outer_diag_diff[x]

    VH_diff = sorted(VH_diff) ; outer_VH_diff = sorted(outer_VH_diff) ; diag_diff = sorted(diag_diff) ; inner_diag_diff = sorted(inner_diag_diff) ; outer_diag_diff = sorted(outer_diag_diff)

    VH_av /= 4 ; outer_VH_av /= 4 ; diag_av /= 4; inner_diag_av /= 4 ; outer_diag_av /= 4
    if(not is_subroutine):
        print('AVERAGE VARIANCE OF:\nVH group:',VH_av,'\ndiag group',diag_av,'\nouter_VH group',outer_VH_av,'\ninner_diag group',inner_diag_av,'\nouter_diag group',outer_diag_av)
        print('\nVH group:',VH_diff,'\ndiag group:',diag_diff,'\nouter_VH group:',outer_VH_diff,'\ninner_diag group:',inner_diag_diff,'\nouter_diag group:',outer_diag_diff)
    return (VH_diff, diag_diff, outer_VH_diff, inner_diag_diff, outer_diag_diff)

def distributed_diagonal_difference_hypothesis_test(dataset = 'cifar10'):

    VH_diff_collection, diag_diff_collection, outer_VH_diff_collection, inner_diag_diff_collection, outer_diag_diff_collection = [],[],[],[],[]
    collections = [VH_diff_collection, diag_diff_collection, outer_VH_diff_collection, inner_diag_diff_collection, outer_diag_diff_collection]
    print('Starting distributed diagonal difference hypothesis...\n')
    start = time.time()
    for row in range(8,22):
        if(row == 9):
            print('estimated time to complete based off one iteration:', (time.time() - start)*12)
            row_interval = (time.time() - start)
        if(row > 9):
            print('estimated time to complete:',row_interval*(22 - row - 1))

        for col in range(8, 22):
            new_input = diagonal_difference_hypothesis_test(dataset = dataset, index = (row, col), is_subroutine=True)
            for insertion in range(0,5):
                collections[insertion].append(new_input[insertion])
    
    VH_mean = np.mean(collections[0], axis = 0) ; diag_mean = np.mean(collections[1], axis = 0) ; outer_VH_mean = np.mean(collections[2], axis = 0); inner_diag_mean = np.mean(collections[3], axis = 0); outer_diag_mean = np.mean(collections[4], axis = 0)
    mean_collections = [VH_mean, diag_mean, outer_VH_mean, inner_diag_mean, outer_diag_mean]
    print("\nAVERAGE VH group by rank", VH_mean,'\nAVERAGE diag group by rank',diag_mean, '\nAVERAGE outer_VH group by rank',outer_VH_mean,'\nAVERAGE inner_diag group by rank',inner_diag_mean,'\nAVERAGE outer_diag group by rank',outer_diag_mean)
    
distributed_diagonal_difference_hypothesis_test()
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

#animate_pixel_select_history_test()



