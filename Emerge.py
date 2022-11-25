import Gather
import Encrypt
import Correlate
from Map import lattice
import Merge

import numpy as np
import matplotlib.pyplot as plt
import random
import pickle
import sys, os
import tqdm
from time import time


# Disable
def save_map(alpha, name):
    alpha.update_map_index(alpha.map_hash)
    map = {}
    for map_index in alpha.map_hash:
        map[map_index] = alpha.map_hash[map_index].index
    outfile = open(name,'wb')
    pickle.dump(map,outfile)
    outfile.close()
    
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

def show_extraction(transformed_image, base_image):
    # outputs a side by side of a transformed image and the removed from image

    #full_image = np.zeros((int(len(transformed_image)), int((2 + len(transformed_image[0]) + len(base_image[0]))), int(len(base_image[0][0]))))
    full_image = []


    for row in range(len(transformed_image)):
        new_row = []
    
        new_row += base_image[row].tolist() + [(0,0,0), (0,0,0)] + transformed_image[row].tolist()
        full_image.append(new_row)
         
    return np.array(full_image)
def print_alignment_options():
    print('if the images are aligned or you cant tell enter respond with done\n',
    'if the image need to be rotated clockwise respond with cw\n',
    'if the image needs to be rotated counter clockwise respond with ccw\n'
    ,'if the image needs to be vertically flipped respond with v')


def cut_to_min_dimensions(map):
    min_all_present_row = 0 ; max_all_present_row = 0
    min_all_present_col = 0 ; max_all_present_col = 0
    #define absolutes
    rows = {}
    cols = {}
    for index in map:
        #print(index)
        if(index[0] not in rows):
            rows[index[0]] = []
        if(index[1] not in cols):
            cols[index[1]] = []

        if(index[0] < min_all_present_row): min_all_present_row = index[0]
        if(index[1] < min_all_present_col): min_all_present_col = index[1]
        if(index[0] > max_all_present_row): max_all_present_row = index[0]
        if(index[1] > max_all_present_col): max_all_present_col = index[1]
        cols[index[1]].append(index[0])
        rows[index[0]].append(index[1])
    #print('Initial: cropped:',min_all_present_row, max_all_present_row, min_all_present_col, max_all_present_col)

    not_valid = True ; 
    min_c = 0 ; max_c = 0 ; min_r = 0 ; max_r = 0
    while(not_valid):
        min_all_present_col += min_c
        max_all_present_col -= max_c
        min_all_present_row += min_r
        max_all_present_row -= max_r

        min_c = 0 ; max_c = 0 ; min_r = 0 ; max_r = 0

        for r in range(min_all_present_row, max_all_present_row):
            if((r,min_all_present_col) not in map):
                min_c = 1
            if((r, max_all_present_col) not in map):
                max_c = 1
        for c in range(min_all_present_col, max_all_present_col):
            if((min_all_present_row, c) not in map):
                min_r = 1
            if((max_all_present_row, c) not in map):
                max_r = 1
        if(min_c + max_c + min_r + max_r == 0): not_valid = False
    
        
    
    cropped_map = {}
    #print('crop: col modified:',min_all_present_row, max_all_present_row, min_all_present_col, max_all_present_col)
    for index in map:
        #print(index, index[0], index[1])
        #print('row between:',min_all_present_row, max_all_present_row,'col between:',min_all_present_col, max_all_present_col)
        if(index[0] >= min_all_present_row and index[0] <= max_all_present_row and index[1] >= min_all_present_col and index[1] <= max_all_present_col):
            cropped_map[index] = map[index]
            #print('included')
        else:pass
            
            #print('cut out', index)
    return cropped_map


class Emerge():
    def __init__(self, picture_pixel, num_anchors, pic):
        self.pixels = picture_pixel.index_pixels_hash
        self.lattices = {}
        self.lattice_dimensions = []
        self.picture_pixel = picture_pixel
        # build lattices
        # start from the biggest lattice and align every node it touches to it.
        random_anchors = random.sample(list(self.pixels.keys()), num_anchors)
        for anchor in tqdm.tqdm((random_anchors), desc=' anchors completed ', leave=True):
            #print(anchor)
            blockPrint()
            self.lattices[anchor] = lattice(picture_pixel, anchor)
            self.lattices[anchor].expand_anchor_better()
            dimensions = self.lattices[anchor].lifecycle()
            #self.lattices[anchor].transform(pic)
            self.lattice_dimensions.append((anchor, dimensions))
            enablePrint()
        self.lattice_dimensions = sorted(self.lattice_dimensions, key= lambda x:x[1], reverse = True)
        #for x in self.lattice_dimensions[:10]:
        #    print(x)
        #    self.lattices[x[0]].transform(pic)

    def Merge_until_satisfied(self, sample_picture, lattices_to_merge = 25):
        if(type(lattices_to_merge) != type(5) ):
            if(lattices_to_merge == 'full'):
                lattices_to_merge = len(self.lattice_dimensions) - 1
        base_index = self.lattice_dimensions[0][0]
        index_to_be_merged_counter = 1
        transformed_image = self.lattices[base_index].raw_transform(sample_picture, show = False)

        
        map = self.lattices[base_index].map_hash
        new_lattice = lattice(self.picture_pixel,base_index )
        
        for map_index in map:
            if(map_index not in new_lattice.map_hash):
                new_lattice.place_by_map_index(map[map_index].index, map_index)

        
        original_image = new_lattice.raw_transform(sample_picture,show = False)
        for r in tqdm.tqdm(range(min(lattices_to_merge, len(self.lattice_dimensions))), desc = 'maps merged', leave=True):

            current_indices = Merge.pull_indice_list(new_lattice.map_hash)

            new_indices = Merge.pull_indice_list(self.lattices[self.lattice_dimensions[index_to_be_merged_counter][0]].map_hash)

            check_if_overlap = list(filter(lambda x: x not in current_indices , new_indices))

            if(len(check_if_overlap) == 0):
                continue
            rotate_aligned = Merge.rotate_align(new_lattice.map_hash, {self.lattice_dimensions[index_to_be_merged_counter][0]:self.lattices[self.lattice_dimensions[index_to_be_merged_counter][0]].map_hash} , current_indices)
            
            central_aligned = Merge.central_align(new_lattice.map_hash, rotate_aligned, current_indices)

            try:
                addition = central_aligned[self.lattice_dimensions[index_to_be_merged_counter][0]]
                for map_index in addition:
                    if(map_index not in new_lattice.map_hash):
                        new_lattice.place_by_map_index(addition[map_index].index, map_index)

            except:
                # means no overlap with current lattice and the new lattice
                pass

            index_to_be_merged_counter += 1

        map = new_lattice.map_hash
        print_alignment_options()
        plt.imshow(show_extraction(transformed_image[:len(sample_picture)][:len(sample_picture[0])] , sample_picture))
        plt.show()
        alignment = input()

        new_map = {}
        
        total_turns = 0 ; invert = 0
        while(alignment != 'done'):
            if(alignment == 'cw'): 
                new_map = Merge.rotate_map(map, 1)
                total_turns += 1
            if(alignment == 'ccw'): 
                new_map = Merge.rotate_map(map, -1)
                total_turns -= 1
            if(alignment == 'v'): 
                new_map = Merge.vertically_invert_map(map)
                invert += 1
            new_map = cut_to_min_dimensions(new_map)
            new_lattice.update_map_index(new_map)
            map = new_map
            transformed_image = new_lattice.raw_transform(sample_picture, map_hash = new_map, show = False)
            plt.imshow(show_extraction(transformed_image, sample_picture))
            plt.show()
            print_alignment_options()
            alignment = input()

            plt.figure()

        #print(new_map[(1,0)].index, new_lattice.map_hash[(1,0)].index)

        t = new_lattice.raw_transform(sample_picture, show=True)
        
        return new_lattice



        

            

def working_test():
    start = time()
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='cifar10', size = 5000)
    import_time = time() - start
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    picture_test = Correlate.picture_pixel(encrypted_test_data)
    picture_test.apply_association()
    #a = lattice(picture_test, (13,13))
    #a.expand_anchor_better()
    #map_hash_stack = a.lifecycle(animation=False)
    #a.transform(test_data[0])
    e = Emerge(picture_test,picture_test.index_pixels_length, encrypted_test_data[0])
    test = e.Merge_until_satisfied(encrypted_test_data[0], 'full')
    test.raw_transform(encrypted_test_data[10])
    print(len(test.map_hash))
    save_map(test, 'final_lattice.obj')
    outfile = open('15pic.obj','wb')
    pickle.dump(encrypted_test_data[:15],outfile)
    outfile.close()



def load_frame_optimization():

    infile = open('final_lattice.obj','rb')
    emerged_map = pickle.load(infile)
    test = lattice(None, None)
    for map_index in emerged_map:
        test.place_by_map_index(emerged_map[map_index], map_index, True)
    infile.close()
    infile = open('15pic.obj','rb')
    pic_sample = pickle.load(infile)
    infile.close()
    new_map = cut_to_min_dimensions(test.map_hash)
    test.update_map_index(new_map)
    test.raw_transform(pic_sample[13])
    
working_test()
load_frame_optimization()
