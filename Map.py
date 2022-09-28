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
        if(self.up is None and self.down is None and self.left is None and self.right is None): return False
        return True

    def find_available_connections(self):
        # this makes no fucking sense but it works...
        open = []
        if(type(self.up) ==  type(None)): open.append('up')
        if(type(self.down) ==  type(None)): open.append('down')
        if(type(self.right) ==  type(None)): open.append('right')
        if(type(self.left) ==  type(None)): open.append('left')
        return open

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
        print('ROW SPACE:',row_space,'COL SPACE:', col_space)
        grid = []
        for x in range(row_space +1, -2, -1):
            row = []
            for y in range(-1, col_space + 2):
                if( (x + min_row, y - min_col) in self.map_hash):
                    row.append(self.map_hash[(x + min_row, y - min_col)].index)
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
            #print(stage[0][element][1])
            elements_in_all_examined[stage[0][element][1]] = 1
        
        for stage_n in range(1, number_of_stages):
            for element in stage[stage_n]:
                if(element[1] in elements_in_all_examined): elements_in_all_examined[element[1]] += 1

        final = []
        
        for element in elements_in_all_examined:
            if(elements_in_all_examined[element] == number_of_stages): final.append(element)

        return final
    def filter_through_placed(self, stage, reverse = False):
        # takes a list of indices and checks if they have been placed or not
        passed = []
        for staged_item in stage:
            in_placed = False
            for placed in self.placement_list:
                if(placed.index == staged_item): 
                    in_placed = True ; break

            if(not reverse):
                if(not in_placed):
                    passed.append(staged_item)
            else:
                if(in_placed):
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
            #print('\nGroup based on index',total_vh_group[index_outer],':',outer_group)
            for index_inner in range(len(total_vh_group)):
                if(index_outer != index_inner):
                    inner_group = self.hash[total_vh_group[index_inner]].vh_association_group
                    #print('Subgroup based on index',total_vh_group[index_inner],':',inner_group)
                    for element_outer in range(4):
                        for element_inner in range(4):
                            if(outer_group[element_outer][1] == inner_group[element_inner][1]):
                                #print('found corner:',outer_group[element_outer][1],inner_group[element_inner][1] )
                                twice_present_nodes.append(outer_group[element_outer][1])
        twice_present_nodes = self.filter_through_placed(set(twice_present_nodes))
        return twice_present_nodes
    
    def build_ring(self):
        total_vh_group = []
        for node in self.placement_list:
            if(node.has_connections_available()):
                vh_indices = [x[1] for x in node.vh]
                print(vh_indices)
                total_vh_group += self.filter_through_placed(vh_indices)
        total_vh_group = list(set(total_vh_group))
        total_vh_group += self.find_corners(total_vh_group)
        ring = []
        for node_index in total_vh_group:

            #print('\nmutual',self.mutually_included( [  self.hash[node_index].vh_association_group,[(0,x) for x in total_vh_group] ]))
            ring.append([node_index,self.mutually_included( [  self.hash[node_index].vh_association_group,[(0,x) for x in total_vh_group] ]) ])
        return ring

    def find_ring_receivers(self):
        for node_outer in self.placement_list:
            #print('\n\n\n')
            if(node_outer.has_connections_available()):
                
                for node_inner in self.placement_list:
                    if(node_inner.has_connections_available() and node_inner.index != node_outer.index):
                        #print('node inner index', node_inner.index)
                        #print('node outer index', node_outer.index)
                        outer_vh = [x[1] for x in self.hash[node_outer.index].vh_association_group]
                        inner_vh = [x[1] for x in self.hash[node_inner.index].vh_association_group]
                        #print('\nouter vh:',outer_vh,'\ninner vh:',inner_vh)
                        if(node_inner.index in outer_vh and node_outer.index in inner_vh):
                            
                            return node_inner.index, node_outer.index
    def attach_locks_to_receivers(self, alpha_receiver, alpha_lock, beta_receiver, beta_lock, direction):
        direction_function = False
        print(direction)
        if(direction == 'up'): direction_function = self.place_up
        if(direction == 'down'): direction_function = self.place_down
        if(direction == 'left'): direction_function = self.place_left
        if(direction == 'right'): direction_function = self.place_right

        direction_function(alpha_receiver , alpha_lock)
        direction_function(beta_receiver, beta_lock)
        
    def is_ring_placed(self, ring):
        nodes = [x[0] for x in ring]
        to_be_placed = len(self.filter_through_placed(nodes))
        print('number of nodes to be placed:',to_be_placed)
        if(to_be_placed == 0):
            return True
        return False
    
    def sort_ring_by_alpha(self, ring, alpha_lock, beta_lock):
        
        alpha_ring = []
        print('\nring[0]',ring[0])
        for link in ring:
            if(link[0] == alpha_lock):
                print('prechange',link)
                link_index = link[0]
                if(link[1][0] == beta_lock):
                    alpha_ring = [link_index, [link[1][0], link[1][1]] ]
                else:

                    alpha_ring = [link_index, [link[1][1], link[1][0]]]
        
        print('post change:', alpha_ring)

        new_ring = [alpha_ring] ; insertion_counter = 0
        while(new_ring[insertion_counter][1][1] != alpha_lock):
            new_link = []
            new_link_index = new_ring[insertion_counter][1][1]
            for link in ring:
                if(link[0] == new_link_index):
                    print('prechange', link)
                    if(link[1][0] == new_ring[insertion_counter][0]):
                        new_link = link
                    else:
                        new_link = [link[0], [link[1][1], link[1][0]]]
            print('post change:', new_link)
            new_ring.append(new_link) ; insertion_counter += 1
        for link in new_ring:
            print(link)
        print("DONE NEW RING")
    def grow(self, ring):
        ring_receiver_alpha, ring_receiver_beta = self.find_ring_receivers()
        print('ring:',ring, '\nring[0]',ring[0])
        alpha_vh = [] ; beta_vh = []
        print('self.hash[ring_lock_alpha].vh_association_group:',self.hash[ring_receiver_alpha].vh_association_group,'\nself.hash[ring_lock_beta].vh_association_group',self.hash[ring_receiver_beta].vh_association_group)
        # find out which indices in the ring are in the ring lock groups for attachment
        for link in ring:
            if(link[0] in [ x[1] for x in self.hash[ring_receiver_alpha].vh_association_group]):
                alpha_vh.append(link[0])
            if(link[0] in [ x[1] for x in self.hash[ring_receiver_beta].vh_association_group]):
                beta_vh.append(link[0])
        
        # find out which of the nodes in alpha_vh and beta_vh are associated with each other

        for alpha_lock in alpha_vh:
            for beta_lock in beta_vh:
                if(alpha_lock in [ x[1] for x in self.hash[beta_lock].vh_association_group] and beta_lock in [ x[1] for x in self.hash[alpha_lock].vh_association_group]):
                    print('\nFound Linked Nodes:',alpha_lock, beta_lock)
                    break
        print('alpha_vh:',alpha_vh,'\nbeta_vh',beta_vh)
        print('ring lock alpha', alpha_lock, 'ring lock beta', beta_lock)
        print('ring receiver alpha',ring_receiver_alpha,'ring receiver beta', ring_receiver_beta)
        #print('open connections alpha:',self.placement_hash[ring_lock_alpha].find_available_connections(),'\nopen connections beta:', self.placement_hash[ring_lock_beta].find_available_connections())
       
        # this is not readable but is simple, the mutually_included function was built for processing tuples by the second index. thats all this does.
        mutual_availability = self.mutually_included( [ [ (0,x) for x in self.placement_hash[ring_receiver_alpha].find_available_connections()  ] , [(0,x) for x in self.placement_hash[ring_receiver_beta].find_available_connections()]])
        print('mutual availability:', mutual_availability)
        if(len(mutual_availability) > 1):
            print('\n\n\n\n FAILED PLACEMENT. DONE EXPANSION \n\n')
            return False
        self.is_ring_placed(ring)
        self.attach_locks_to_receivers(ring_receiver_alpha, alpha_lock, ring_receiver_beta, beta_lock, mutual_availability[0])
        self.is_ring_placed(ring)
        self.sort_ring_by_alpha(ring, alpha_lock, beta_lock)
        











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
    lattice_test.grow(lattice_test.build_ring())
    lattice_test.display_self()
working_test()
