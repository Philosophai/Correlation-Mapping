import Gather
import Encrypt
import Correlate
import pickle
import numpy as np

cifar_test_key = "/Users/johnbrown/Desktop/Nelson/CSL/Correlation-Mapping/mapping_test.obj"

'''
TODO:
1. refactor type(self.up) != type(None) to use some python syntax. looks messy.
'''
class node:
    def __init__(self, index, index_pixel, map_index, up = None, down = None, right = None, left = None):
        self.index = index ; self.map_index = map_index
        self.up = up ; self.down = down ; self.right = right ; self.left = left
        self.vh = index_pixel.vh_association_group
        self.diag = index_pixel.diag_association_group
    def has_connections_available(self):
        if(type(self.up) != type(None) and type(self.down) != type(None) and type(self.left) != type(None) and type(self.right) != type(None)): return False
        return True


class lattice:

    def __init__(self, picture_pixel, anchor_index):
        self.anchor_index = node(anchor_index, picture_pixel.index_pixels_hash[anchor_index], (0,0))
        self.anchor_index.right = node(self.anchor_index.vh[0][1],picture_pixel.index_pixels_hash[self.anchor_index.vh[0][1]],(0,1), left = self.anchor_index)
        self.placement_list = [self.anchor_index, self.anchor_index.right]
        self.placement_hash = {self.anchor_index.index:self.anchor_index , self.anchor_index.right.index : self.anchor_index.right}
        self.map_hash = {self.anchor_index.map_index: self.anchor_index , self.anchor_index.right.map_index : self.anchor_index.right}
        self.base_index = anchor_index
        self.picture = picture_pixel
        self.hash = picture_pixel.index_pixels_hash
       
    def connect_local(self, placed_node):
        up_code = (1, 0) ; down_code = (-1, 0) ; right_code = (0, 1) ; left_code = (0, -1)
        map_index = placed_node.map_index
        for row in range(-1, 2):
            for col in range(-1, 2):
                if( (row + map_index[0], col + map_index[1]) in self.map_hash and not ( col == row and col == 0 )):
                    #print('found node', (row + map_index[0], col + map_index[1]), 'from :',placed_node.map_index)
                    if((row,col) == up_code):
                        self.connect_up(placed_node,(row + map_index[0], col + map_index[1]))
                        #print('connected up')
                    if((row,col) == down_code):
                        self.connect_down(placed_node,(row + map_index[0], col + map_index[1]))
                        #print('connected down')
                    if((row,col) == right_code):
                        self.connect_right(placed_node,(row + map_index[0], col + map_index[1]))
                        #print('connected right')
                    if((row,col) == left_code):
                        self.connect_left(placed_node,(row + map_index[0], col + map_index[1]))
                        #print('connected left')
                                      
    def place_up(self, center_index, to_be_placed_index):
        center_map_index = self.placement_hash[center_index].map_index
        new_node = node(to_be_placed_index, self.hash[to_be_placed_index], (center_map_index[0] + 1, center_map_index[1]), down = self.placement_hash[center_index] )
        self.placement_hash[center_index].up = new_node
        self.placement_hash[to_be_placed_index] = new_node
        self.placement_list.append(new_node)
        self.map_hash[(center_map_index[0] + 1, center_map_index[1])] = new_node
        self.connect_local(new_node)

    def connect_up(self, new_node, index_to_be_connected_to):
        new_node.up = self.map_hash[index_to_be_connected_to]
        self.map_hash[index_to_be_connected_to].down = new_node

    def place_down(self, center_index, to_be_placed_index):
        center_map_index = self.placement_hash[center_index].map_index
        new_node = node(to_be_placed_index, self.hash[to_be_placed_index], (center_map_index[0] - 1, center_map_index[1]),up = self.placement_hash[center_index] )
        self.placement_hash[center_index].down = new_node
        self.placement_hash[to_be_placed_index] = new_node
        self.placement_list.append(new_node)
        self.map_hash[(center_map_index[0] - 1, center_map_index[1])] = new_node
        self.connect_local(new_node)

    def connect_down(self, new_node, index_to_be_connected_to):
        new_node.down = self.map_hash[index_to_be_connected_to]
        self.map_hash[index_to_be_connected_to].up = new_node
        
    def place_right(self, center_index, to_be_placed_index):
        center_map_index = self.placement_hash[center_index].map_index
        new_node = node(to_be_placed_index, self.hash[to_be_placed_index],(center_map_index[0] , center_map_index[1] + 1), left = self.placement_hash[center_index] )
        self.placement_hash[center_index].right = new_node
        self.placement_hash[to_be_placed_index] = new_node
        self.placement_list.append(new_node)
        self.map_hash[(center_map_index[0], center_map_index[1] + 1)] = new_node
        self.connect_local(new_node)

    def connect_right(self, new_node, index_to_be_connected_to):
        new_node.right = self.map_hash[index_to_be_connected_to]
        self.map_hash[index_to_be_connected_to].left = new_node
        
    def place_left(self, center_index, to_be_placed_index):
        center_map_index = self.placement_hash[center_index].map_index
        new_node = node(to_be_placed_index, self.hash[to_be_placed_index], (center_map_index[0], center_map_index[1] - 1),left = self.placement_hash[center_index] )
        self.placement_hash[center_index].left = new_node
        self.placement_hash[to_be_placed_index] = new_node
        self.placement_list.append(new_node)
        self.map_hash[(center_map_index[0], center_map_index[1] - 1)] = new_node
        self.connect_local(new_node)

    def connect_left(self, new_node, index_to_be_connected_to):
        new_node.left = self.map_hash[index_to_be_connected_to]
        self.map_hash[index_to_be_connected_to].right = new_node
        
    def display_self(self):
        max_row = 0;min_row = 0;  max_col = 0; min_col = 0
        for x in self.map_hash:
            print(x)
            if(x[0] > max_row): max_row = x[0]
            if(x[0] < min_row): min_row = x[0]

            if(x[1] > max_col): max_col = x[1]
            if(x[1] < min_col): min_col = x[1]
        row_space = abs(min_row) + max_row ; col_space = abs(min_col) + max_col
        print(row_space, col_space)
        grid = []
        for x in range(row_space +1, -2, -1):
            row = []
            for y in range(-1, col_space + 2):
                if( (x - min_row, y - min_col) in self.map_hash):
                    row.append(self.map_hash[(x - min_row, y - min_col)].index)
                else:
                    row.append(('~','~'))
            grid.append(row)
        for x in grid:
            print(x)
    
    def instantiate_list_as_nodes(self, stage):
        nodes = []
        for x in stage:
            nodes.append(node(x[1],self.hash[x[1]]))
        return nodes

    def mutually_included(self, stage):
        number_of_stages = len(stage)
        if(number_of_stages <= 1): return stage
        elements_in_all_examined = {}
        for element in range(len(stage[0])):
            print(stage[0][element][1])
            elements_in_all_examined[stage[0][element][1]] = 1
        
        for stage_n in range(1, number_of_stages):
            for element in stage[stage_n]:
                if(element[1] in elements_in_all_examined): elements_in_all_examined[element[1]] += 1

        final = []
        for element in elements_in_all_examined:
            if(elements_in_all_examined[element] == number_of_stages): final.append(element)

        return final
    def filter_through_placed(self, stage):
        # takes a list of indices and checks if they have been placed or not
        passed = []
        for staged_item in stage:
            in_placed = False
            for placed in self.placement_list:
                if(placed.index == staged_item): 
                    in_placed = True ; break
            if(not in_placed):
                passed.append(staged_item)
        return passed

    def expand_anchor(self):
        # now i have self.anchor and self.anchor.up
        total_vh_group = []
        anchor_vh = self.filter_through_placed([x[1] for x in self.anchor_index.vh])
        anchor_right_vh = self.filter_through_placed([x[1] for x in self.anchor_index.right.vh])
        #print(anchor_vh,'\n',anchor_right_vh)
        groups = []
        for index in anchor_vh:
            index_vh = [x[1] for x in self.hash[index].vh_association_group]
            #print(index_vh)
            for indice_in_index_vh in index_vh:
                for indice_in_anchor_right_vh in anchor_right_vh:
                    if(indice_in_index_vh == indice_in_anchor_right_vh and sorted([indice_in_index_vh, indice_in_anchor_right_vh]) not in groups):
                        groups.append( sorted([index, indice_in_anchor_right_vh]) )
        
        
        #print(groups)
        #print("STARTING FIRST ADDITION")
        self.place_up(self.anchor_index.index, groups[0][0])
        #print(self.map_hash)
        #print("STARTING SECOND ADDITION",self.anchor_index.right.index)
        self.place_up(self.anchor_index.right.index, groups[0][1])
        #print(self.map_hash)
    def find_corners(self, total_vh_group):
        print(total_vh_group)
        twice_present_nodes = []
        for index_outer in range(len(total_vh_group)):
            outer_group = self.hash[total_vh_group[index_outer]].vh_association_group
            print('\nGroup based on index',total_vh_group[index_outer],':',outer_group)
            for index_inner in range(len(total_vh_group)):
                if(index_outer != index_inner):
                    inner_group = self.hash[total_vh_group[index_inner]].vh_association_group
                    print('Subgroup based on index',total_vh_group[index_inner],':',inner_group)
                    for element_outer in range(4):
                        for element_inner in range(4):
                            if(outer_group[element_outer][1] == inner_group[element_inner][1]):
                                print('found corner:',outer_group[element_outer][1],inner_group[element_inner][1] )
                                twice_present_nodes.append(outer_group[element_outer][1])
        twice_present_nodes = self.filter_through_placed(set(twice_present_nodes))
        print(twice_present_nodes)
    def grow(self):
        total_vh_group = []
        for node in self.placement_list:
            vh_indices = [x[1] for x in node.vh]
            print(vh_indices)
            total_vh_group += self.filter_through_placed(vh_indices)
        total_vh_group = list(set(total_vh_group))
        self.find_corners(total_vh_group)




def save_test():
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='cifar10', size = 300)
    picture_test = Correlate.picture_pixel(test_data)
    picture_test.apply_association()
    outfile = open(cifar_test_key,'wb')
    pickle.dump(picture_test,outfile)

def load_test():
    infile = open(cifar_test_key,'rb')
    new_test = pickle.load(infile)
    print(type(new_test))

def working_test():
    if(type(None) != type(None)): print("weeee")
    infile = open(cifar_test_key,'rb')
    picture_test = pickle.load(infile)
    lattice_test = lattice(picture_test, (13,13))

    lattice_test.expand_anchor()
    lattice_test.display_self()
    lattice_test.grow()
working_test()
