import Gather
import Encrypt
import Correlate
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from time import time
'''
TODO:
1. refactor out the self displays 
'''
cifar_test_key = "/Users/johnbrown/Desktop/Nelson/CSL/Correlation-Mapping/mapping_test.obj"


class node:
    def __init__(self, index, index_pixel, map_index, up = None, down = None, right = None, left = None):
        self.index = index ; self.map_index = map_index

        self.up = up ; self.down = down ; self.right = right ; self.left = left
        try:
            self.vh = index_pixel.vh_association_group
            self.diag = index_pixel.diag_association_group
        except:
            pass

    def has_connections_available(self):

        if(self.up != None and self.down != None and self.left != None and self.right != None):
            #print("NO CONNECTIONS AVAILABLE")
            return False
        #print("CONNECTIONS AVAILABLE")
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
        if(picture_pixel == None and anchor_index == None):
            self.map_hash = {}
            self.placement_hash = {}
            self.placement_list = []
            self.hash = {}
            return

        self.anchor_index = node(anchor_index, picture_pixel.index_pixels_hash[anchor_index], (0,0))
        self.anchor_index.right = node(self.anchor_index.vh[0][1],picture_pixel.index_pixels_hash[self.anchor_index.vh[0][1]],(0,1), left = self.anchor_index)
        self.placement_list = [self.anchor_index, self.anchor_index.right]
        self.placement_hash = {self.anchor_index.index:self.anchor_index , self.anchor_index.right.index : self.anchor_index.right}
        self.map_hash = {self.anchor_index.map_index: self.anchor_index , self.anchor_index.right.map_index : self.anchor_index.right}
        self.base_index = anchor_index
        self.picture = picture_pixel
        self.hash = picture_pixel.index_pixels_hash
        self.uncertain = False
        for node_index in self.hash:
            if(self.hash[node_index].vh_association_group[2][0] == 0.0):
                self.uncertain = True
                break
    

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

    def place_by_label(self, center_index, to_be_placed_index, direction):
        if(direction == 'up'): self.place_up(center_index, to_be_placed_index)    
        if(direction == 'down'): self.place_down(center_index, to_be_placed_index)  
        if(direction == 'left'): self.place_left(center_index, to_be_placed_index)  
        if(direction == 'right'): self.place_right(center_index, to_be_placed_index)  

    def place_by_map_index(self, to_be_placed_index, map_index_target, empty = False):
        if(map_index_target in self.map_hash):
            raise ValueError ('MAP INDEX ALREADY IN USE')
        if(empty):
            new_node = node(to_be_placed_index, None, map_index_target)
        else:
            new_node = node(to_be_placed_index, self.hash[to_be_placed_index], map_index_target)
        self.placement_hash[to_be_placed_index] = new_node
        self.placement_list.append(new_node)
        self.map_hash[map_index_target] = new_node
        self.connect_local(new_node)
        
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
        new_node = node(to_be_placed_index, self.hash[to_be_placed_index], (center_map_index[0], center_map_index[1] - 1),right = self.placement_hash[center_index] )
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
        print("DISPLAYING LATTICE\n")
        for x in self.map_hash:
            
            if(x[0] > max_row): max_row = x[0]
            if(x[0] < min_row): min_row = x[0]

            if(x[1] > max_col): max_col = x[1]
            if(x[1] < min_col): min_col = x[1]
        row_space = abs(min_row) + max_row ; col_space = abs(min_col) + max_col
        #print('ROW SPACE:',row_space,'COL SPACE:', col_space)
        #print('max row:', max_row, 'min row:',min_row,' max col:',max_col, 'min col:',min_col)
        grid = []
        for x in range(max_row, min_row - 1, -1):
            row = []
            for y in range(min_col, max_col + 1):
                try:
                    row.append(str(self.map_hash[(x,y)].index))
                except:
                    row.append(str(None))
            grid.append(row)
        s = [[str(e) for e in row] for row in grid]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in s]
        print('\n'.join(table))
        return (row_space + 1, col_space + 1)
        '''
        print(np.array(grid))
        plt.matshow(grid)
        plt.figure()
        string_grid = []
        for row in grid:
            string_row = ''
            for col in row:
                string_row += '\t'
                string_row += str(col)
            print(string_row)
        '''
    
    def instantiate_list_as_nodes(self, stage):
        nodes = []
        for x in stage:
            nodes.append(node(x[1],self.hash[x[1]]))
        return nodes

    def find_ring_bounds(self):
        # given a node, find the available connection adjacent to the most node
        row_min = 0; row_max = 0; col_min = 0 ; col_max = 0
        for pixel in self.map_hash:
            #print('map hash found node', pixel)
            if(row_min > pixel[0]): row_min = pixel[0]
            if(row_max < pixel[0]): row_max = pixel[0]
            if(col_min > pixel[1]): col_min = pixel[1]
            if(col_max < pixel[1]): col_max = pixel[1]
        #print('expanded row_min', row_min - 1,'\nexpanded row_max',row_max+1, '\nexpanded col_min',col_min-1,'\nexpanded col_max',col_max+1)
        return (row_min - 1, row_max + 1, col_min - 1, col_max + 1)

    def find_next_spot(self, link, bounds):
        link_row = self.placement_hash[link].map_index[0] ; link_col = self.placement_hash[link].map_index[1]
        available = self.placement_hash[link].find_available_connections()
        projected_indices = []
        if('up' in available): projected_indices.append([(link_row + 1, link_col), 'up'])
        if('down' in available): projected_indices.append([(link_row - 1, link_col), 'down'])
        if('left' in available): projected_indices.append([(link_row, link_col - 1), 'left'])
        if('right' in available): projected_indices.append([(link_row, link_col + 1), 'right'])
        #print('link index',(link_row, link_col) )
        #print('available ',available)
        #print('projected indices:',projected_indices)
        #print('bounds',bounds)
        for projected_index in projected_indices:
            if(projected_index[0][0] >= bounds[0] and projected_index[0][0] <= bounds[1]):
                if(projected_index[0][1] >= bounds[2] and projected_index[0][1] <= bounds[3]):
                    #print("FOUND POSSIBLE CONNECTION AT", projected_index)
                    return projected_index

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
    def expand_anchor_better(self):
        #self.display_self()
        vh_anchor = [ x[1] for x in self.hash[self.placement_list[0].index].vh_association_group]
        vh_right = [ x[1] for x in self.hash[self.placement_list[1].index].vh_association_group]
        print("VH of anchor", vh_anchor)
        print("VH of right of anchor", vh_right)
        for index_anchor in vh_anchor:
            vh_index_anchor = [ x[1] for x in self.hash[index_anchor].vh_association_group]
            for index_right in vh_right:
                vh_index_right = [ x[1] for x in self.hash[index_right].vh_association_group]
                if(index_anchor != self.placement_list[1].index and index_right != self.placement_list[0].index):
                    included = len(set(vh_index_anchor).intersection(set([index_right])))
                    print(index_anchor, index_right, set(vh_index_anchor).intersection(set([index_right])))
                    if(included):
                        print("VALID PAIR")
                        self.place_by_label(self.placement_list[0].index, index_anchor, 'up')
                        self.place_by_label(self.placement_list[1].index, index_right, 'up')
                        return

        # find first pair to place above

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

    def intersect_vh_groups(self, index_a, index_b):
        return self.filter_through_placed(set([x[1] for x in self.hash[index_a].vh_association_group]).intersection( set([x[1] for x in self.hash[index_b].vh_association_group])))

    def uncertain_expand_group(self):
        def compute_bond_value(link_a, vh_a,link_b,vh_b ):
            vh_a_index = 0 ; vh_b_index = 0
            bond_value = 0
            for index_a in range(len(vh_a)):
                if(link_b == vh_a[index_a]):
                    bond_value += self.hash[link_a].vh_association_group[index_a][0]
                    print('updating bond with link reference 1')
            for index_b in range(len(vh_b)):
                if(link_a == vh_b[index_b]): 
                    print('updating bond with link reference 2')
                    bond_value += self.hash[link_b].vh_association_group[index_b][0]
            
            for index_base in self.placement_list:
                for value in range(len(self.hash[index_base.index].vh_association_group)):
                    if(self.hash[index_base.index].vh_association_group[value][1] == link_a):
                        print('updating bond with core reference 1')
                        bond_value += self.hash[index_base.index].vh_association_group[value][0]
                    if(self.hash[index_base.index].vh_association_group[value][1] == link_b):
                        print('updating bond with core reference 2')
                        bond_value += self.hash[index_base.index].vh_association_group[value][0]    
            return bond_value
        def build_ring_group():

            print('uncertain expand group:\n')
            ring_group = []
            for placed_index in self.placement_list:
                if(placed_index.has_connections_available()):
                    ring_group += self.filter_through_placed([x[1] for x in self.hash[placed_index.index].vh_association_group])
                    print('indice:',placed_index.index,' group:',[x[1] for x in self.hash[placed_index.index].vh_association_group])
            ring_group = list(set(ring_group))
            return ring_group
        def find_two_groups_in_ring_group(ring_group):
        
            for link in ring_group:
                print(link, [x[1] for x in self.hash[link].vh_association_group])

            groups = []
            for link_a in ring_group:
                vh_a = self.filter_through_placed([x[1] for x in self.hash[link_a].vh_association_group])
                for link_b in ring_group:
                    vh_b = self.filter_through_placed([x[1] for x in self.hash[link_b].vh_association_group])
                    if(link_a in vh_b and link_b in vh_a):

                        bond_value = compute_bond_value(link_a, vh_a, link_b, vh_b)
                            
                        print('adding',link_a,link_b, 'with combined value: ', bond_value)
                        if(link_a > link_b):
                            groups.append((link_a, link_b, bond_value))
                        else:
                            groups.append((link_b, link_a, bond_value))

            groups = list(set(groups))
            groups = sorted(groups, key = lambda x:x[2])
            return groups
        def build_linked_sections(groups):
            growth_section_start_with_one = [groups[0][0]]
            growth_section_start_with_two = [groups[0][1]]
            for index in range(1, len(groups)):
                for sub_index in range(0,2):
                    print('roups[index][sub_index]',groups[index][sub_index],'growth_section_start_with_one[-1]',growth_section_start_with_two[-1])
                    if(groups[index][sub_index] == growth_section_start_with_one[-1] and groups[index][sub_index] not in growth_section_start_with_one):
                        
                        if(sub_index == 0): growth_section_start_with_one.append(groups[index][1])
                        else: growth_section_start_with_one.append(groups[index][0])
                    if(groups[index][sub_index] == growth_section_start_with_two[-1]):
                        print("INSERTING")
                        if(sub_index == 0 and groups[index][1] not in growth_section_start_with_two): growth_section_start_with_two.append(groups[index][1])
                        else:
                            if(sub_index == 1 and groups[index][0] not in growth_section_start_with_two): growth_section_start_with_two.append(groups[index][0])
            return growth_section_start_with_one, growth_section_start_with_two
        def output_max_sized_usable_section(growth_section_start_with_one,growth_section_start_with_two):
            print('starts with one', growth_section_start_with_one)
            print('starts with two', growth_section_start_with_two)
            print('Attempting section merge: intersection returns ',set(growth_section_start_with_one).intersection(set(growth_section_start_with_two)))
            growth = []
            if(len(set(growth_section_start_with_one).intersection(set(growth_section_start_with_two))) == 0):
                print("VOID INTERSECTION CAN APPEND ONE To TWO")
                
                for index in range(len(growth_section_start_with_one) -1, -1, -1):
                    growth.append(growth_section_start_with_one[index])
                for index in growth_section_start_with_two:
                    growth.append(index)
                print('growth: ', growth)
            else:
                if(len(growth_section_start_with_one) > len(growth_section_start_with_two)):
                    growth = growth_section_start_with_one
                else: growth = growth_section_start_with_two

            print('Growth group', growth)

            return growth
        ring_group = build_ring_group()
        groups = find_two_groups_in_ring_group(ring_group)
        
        growth_section_start_with_one, growth_section_start_with_two = build_linked_sections(groups)
        return output_max_sized_usable_section(growth_section_start_with_one, growth_section_start_with_two)
        

        
        

    def build_ring(self):
        if(self.uncertain):
            return self.uncertain_expand_group()
        ring_group = []
        for placed_index in self.placement_list:
            if(placed_index.has_connections_available()):
                ring_group += self.filter_through_placed([x[1] for x in self.hash[placed_index.index].vh_association_group])
        lock_link = list(set(ring_group))[0]
        non_corner_ring = list(set(ring_group))
        #print('lock link:',lock_link)
        corner_presence = []
        for link in ring_group:
            #print('vh of ',link,':',[x[1] for x in self.hash[link].vh_association_group])
            #print('ring group',ring_group)
            #print('', len(set(ring_group).intersection( set([x[1] for x in self.hash[link].vh_association_group]))))
            corner_presence.append([link, len(set(ring_group).intersection( set([x[1] for x in self.hash[link].vh_association_group])))])
            
        # corner presence indicates if an element has a corner element, if the corner presence is 1 it only has one neighbour
        # from the ring group, indicating it has an edge
        for link_a in corner_presence:
            for link_b in corner_presence:
                if(link_a[1] == 1 and link_b[1] == 1 and link_a[0] != link_b[0]):
                    #set([x[1] for x in self.hash[link_a[0]].vh_association_group]).intersection( set([x[1] for x in self.hash[link_b[0]].vh_association_group]))
                    additions = self.intersect_vh_groups(link_a[0], link_b[0])
                    #print('intersection of {link_a} and {link_b}:'.format(link_a = link_a[0], link_b = link_b[0]))
                    #print(self.intersect_vh_groups(link_a[0], link_b[0]))
                    ring_group += additions
        ring_group = list(set(ring_group))
        #print('length of ring:', len(ring_group))
        
        lock_index = False
        for x in range(len(ring_group)):
            if(ring_group[x] == lock_link): lock_index = x
        #print(lock_link, ring_group[lock_index])
        ring = [] ; ring_index = 0
        # this section makes sure that alpha and beta are both not corners
        lock_link_neighbours = list(set(ring_group).intersection( set([x[1] for x in self.hash[lock_link].vh_association_group])))
        if(lock_link_neighbours[1] in non_corner_ring): ring.append([lock_link, lock_link_neighbours])
        else: ring.append([lock_link, [lock_link_neighbours[1], lock_link_neighbours[0]]])
        
        #print('ring[0]',ring[0]) 
        
        
        # this section orders the ring so that the format is [current link, [previous link, next link]]
        while(len(ring) < len(ring_group)):

            

            try:
                new_link = ring[ring_index][1][1]
            except:
                print("ERROR WITH PLACING:",ring[ring_index][0] )
                print("Couldn't find next neighbour in this group. Lets look")
                for node_index in ring_group:
                    if(node_index not in ring[ring_index][1]):
                        print('examining', node_index, )
                        neighbours = list(set(ring_group).intersection( set([x[1] for x in self.hash[node_index].vh_association_group])))
                        print('neighbours:', neighbours)
                        if(ring[ring_index][0] in neighbours):
                            print('found a match at', node_index," group: ", neighbours)
                            ring[ring_index][1].append(node_index)


            new_neighbours = list(set(ring_group).intersection( set([x[1] for x in self.hash[new_link].vh_association_group])))
            #print('neighbours: ', new_neighbours)
            if(new_neighbours[0] == ring[ring_index][0]): ring.append([new_link, new_neighbours])
            else: ring.append([new_link, [new_neighbours[1], new_neighbours[0]]])
            ring_index += 1
        
        return ring        

    def uncertain_bind_section(self, section, animation = False):
        def copy_map_hash(self):
            copy = {}
            for x in self.map_hash:
                copy[x] = self.map_hash[x]
            return copy
        
        def possible_locations_generator(proximity_restrictions_section):
            #print('Examining', proximity_restrictions_section[0])
            possibles = []
            for prox_nec in proximity_restrictions_section[1]:
                map_index = self.placement_hash[prox_nec].map_index
               
                
                for row in range(-1,2):
                    for col in range(-1,2):
                        if((map_index[0] + row, map_index[1] + col) not in self.map_hash):
                            #print('possible:',(map_index[0] + row, map_index[1] + col),' from ',map_index)
                            possibles.append((map_index[0] + row, map_index[1] + col))
            return [proximity_restrictions_section[0], possibles]

        def possible_configurations_generator(possible_configurations):
            def add_conflict_free(index, previous_configuration, possible_configurations,global_configurations):
                if(index >= len(possible_configurations)):
                    if(previous_configuration not in global_configurations):
                        global_configurations.append(previous_configuration)
                    return
                    
                
                conflict_free_configurations = []
                for x in possible_configurations[index][1]:
                    if(x not in previous_configuration):
                        x_dif = abs(x[0] - previous_configuration[index-1][0]) ; y_dif = abs(x[1] - previous_configuration[index-1][1])
                        if(x_dif != y_dif and x_dif < 2 and y_dif < 2):
                            #_dif = abs(x[0] - previous_configuration[index-1][0]) ; y_dif = abs(x[1] - previous_configuration[index-1][1])
                            #difference = [x[0] + abs(x[1]) - abs(previous_configuration[index-1][0]) - abs(previous_configuration[index-1][1])
                            #print('x_dif',x_dif,'y_dif',y_dif)
                            temp = previous_configuration + [x]
                            add_conflict_free(index + 1,temp ,possible_configurations, global_configurations )
                
                
            conflict_free_configurations = []
            for x in possible_configurations[0][1]:
                add_conflict_free(1, [x], possible_configurations, conflict_free_configurations)
            return conflict_free_configurations

        def judge_configurations(conflict_free_configurations, section):
            judged_configurations = []
            print('Configuration Judgement\n')
            for conf in conflict_free_configurations:
                judge_value = 0
                print('JUDGING CONF', conf)
                for index in range(len(conf)):
                    print('desired_adjacency: ')
                    print(section[index], self.filter_through_placed([ x[1] for x in self.hash[section[index]].vh_association_group], reverse=True))
                    wanted_adjacency_list = self.filter_through_placed([ x[1] for x in self.hash[section[index]].vh_association_group], reverse=True)
                    for wanted_adjacency in wanted_adjacency_list:
                        map_index = self.placement_hash[wanted_adjacency].map_index
                        print(wanted_adjacency, 'at', map_index)
                        x_dif = abs(map_index[0] - conf[index][0]) ; y_dif = abs(map_index[1] - conf[index][1])
                        if(x_dif != y_dif and x_dif < 2 and y_dif < 2):
                            print('yay got a positive')
                            judge_value += 1
                judged_configurations.append([judge_value, conf])
            return sorted(judged_configurations, key= lambda x:x[0], reverse=True)
        
        print('Link Index, index vh group filtered through in-place')
        proximity_restrictions = []
        for link in section:
            proximity_restrictions.append([link, self.filter_through_placed([ x[1] for x in self.hash[link].vh_association_group], reverse=True)])
        
        possible_configurations = []
        for link_restrictions in proximity_restrictions:
            possible_configurations.append(possible_locations_generator(link_restrictions))
        
        if(section == None):
            return False

        conflict_free_configurations = possible_configurations_generator(possible_configurations)
        for x in conflict_free_configurations:
            print(x)
        judged = judge_configurations(conflict_free_configurations, section)
        for x in judged:
            print(x)
        print('arbitrarily picked from judged:', judged[0])
        best = judged[0][1]

        map_states = []
        if(animation): map_states = [copy_map_hash(self)]


        for index in range(len(best)):
            self.place_by_map_index(section[index], best[index])
            if(animation): map_states.append(copy_map_hash(self))

        
        if(animation): return map_states
        return None


        

    def bind_ring(self, ring, animation = False):
        if(self.uncertain):
            return self.uncertain_bind_section(ring, animation = animation)
        def neighbour_of(location_a, location_b):
            # receiver two map indices and determine if they are touching each other, include diagonals
            for row in range(-1, 2):
                for col in range(-1, 2):
                    if((location_a[0] + row, location_a[1] + col) == location_b):
                        return True
            return False
        def find_map_indices_from_options(current_map_index, options):
            locations = []
            if('up' in options): locations.append([(current_map_index[0] + 1, current_map_index[1]), 'up'])
            if('down' in options): locations.append([(current_map_index[0] - 1, current_map_index[1]), 'down'])
            if('left' in options): locations.append([(current_map_index[0], current_map_index[1] - 1), 'left'])
            if('right' in options): locations.append([(current_map_index[0], current_map_index[1] + 1),'right'])
            return locations

        def extract_direction_from_difference(difference_between_docks):
            if(difference_between_docks == (1,0)): return 'up'
            if(difference_between_docks == (-1,0)): return 'down'
            if(difference_between_docks == (0,-1)): return 'left'
            if(difference_between_docks == (0,1)): return 'right'

        def copy_map_hash(self):
            copy = {}
            for x in self.map_hash:
                copy[x] = self.map_hash[x]
            return copy

        bounds = self.find_ring_bounds()
        row_min = bounds[0] ; row_max = bounds[1] ; col_min = bounds[2] ; col_max = bounds[3]
        print('Bounds:', bounds)
        for link in ring:
            print(link)
        
        # place anchor
        alpha_link = ring[0][0] ; alpha_dock = False;  beta_link = ring[1][0] ; beta_dock = False
        for node_index in self.placement_list:
            if(alpha_link in [x[1] for x in self.hash[node_index.index].vh_association_group]): alpha_dock = node_index
            if(beta_link in [x[1] for x in self.hash[node_index.index].vh_association_group]): beta_dock = node_index
            
        print(alpha_link, ' being placed next to ', alpha_dock.index)
        print(beta_link, ' being placed next to ', beta_dock.index)
        difference_between_docks = (beta_dock.map_index[0] - alpha_dock.map_index[0] , beta_dock.map_index[1] - alpha_dock.map_index[1])
        print(difference_between_docks)
        # now i have the direction alpha will place beta

        # need to place alpha in correct position
        options = alpha_dock.find_available_connections()
        print(options)
        locations = find_map_indices_from_options(alpha_dock.map_index, options)
        print(locations)
        neighbour_choice = None
        for loc in locations:
            if(neighbour_of( loc[0], beta_dock.map_index)): neighbour_choice = loc
        
        print('chosen location: ', neighbour_choice)
        map_states = []
        if(animation): map_states = [copy_map_hash(self)]
        # place alpha 
        self.place_by_label(alpha_dock.index, alpha_link, neighbour_choice[1])
        if(animation): map_states.append(copy_map_hash(self))
        # place beta off alpha
        self.place_by_label( alpha_link, beta_link, extract_direction_from_difference(difference_between_docks))
        if(animation): map_states.append(copy_map_hash(self)) 
        print(ring[2])
        for link in range(2, len(ring)):
            print(link, bounds)
            
            location_direction = self.find_next_spot(ring[link][1][0], bounds) ; direction = location_direction[1]
            #print('index to be placed',ring[link][0],'location:', location_direction)
            self.place_by_label(ring[link][1][0], ring[link][0], direction)
            if(animation): map_states.append(copy_map_hash(self))
            #self.display_self()
        if(animation): return map_states
        return None

    
    def grow(self, animation = False):
        try:
            start = time()
            ring = self.build_ring()

            map_hash_stack = self.bind_ring(ring, animation=animation)
            #self.display_self()
            print("Finished growth in ", time() - start)
            
            return [map_hash_stack, True]
        except:
            dimensions = self.display_self()
            print("Made it this far before an error.", dimensions)
            
            return [dimensions, False]

    def lifecycle(self, animation = False):
        dimensions_life = [] ; alive = True
        animation_stack = []
        while(alive):
            dimensions_life = self.grow(animation=animation)
            alive = dimensions_life[1]
            if(animation): animation_stack += dimensions_life[0]
        if(animation and alive == False): 
            print("RETURNING ANIMATION STACK")
            return [animation_stack[x] for x in range(0, len(animation_stack) -2)]
        return dimensions_life[0]
    def update_map_index(self, map):
        # first reset
        self.map_hash = {}
        self.placement_hash = {}
        self.placement_list = []


        for map_index in map:
            self.place_by_map_index(map[map_index].index, map_index, True)
            

      def transform(self, picture, map_hash = None, show = True, use_background = False, base_index = (None, None), transformed_image_title = 'Mapped Output from Lattice'):
        if(map_hash == None):
            map_hash = self.map_hash
        else: 
            self.map_hash = map_hash
        #self.update_map_index(map_hash)
        #print('picture shape', picture.shape)
        blank = np.zeros((len(picture), len(picture[0]), len(picture[0][1])))
        if(use_background):
            for pix_row in range(len(picture)):
                for pix_col in range(len(picture[0])):
                    blank[pix_row][pix_col] = picture[pix_row][pix_col]
            
        if(base_index[0] == None):
            min_row = 0; min_col = 0
            
            base_index = (int(len(picture)/2)-2, int(len(picture[0])/2)-2)
        for x in self.map_hash:
            
            #print('map_hash[x].index[0]',map_hash[x].index[0],'map_hash[x].index[1]',map_hash[x].index[1],'self.base_index[0]',self.base_index[0],'self.base_index[1]',self.base_index[1],'x[0]',x[0],'x[1]',x[1])
            blank[base_index[0] + x[0]][base_index[1] + x[1]] = picture[self.map_hash[x].index[0]][self.map_hash[x].index[1]]
        if(show):
            plt.imshow(blank)
            plt.title(transformed_image_title)
            plt.show()
            plt.figure
            plt.imshow(picture)
            plt.title("Original Input")
            plt.show()
            plt.figure()
        
        return blank
    
    def raw_transform(self, picture, map_hash = None, show = True, use_background = False, base_index = (None, None),transformed_image_title = 'Mapped Output from Lattice'):
        if(map_hash == None):
            map_hash = self.map_hash
        self.update_map_index(self.map_hash)
        min_all_present_row = 0 ; max_all_present_row = 0
        min_all_present_col = 0 ; max_all_present_col = 0
        #define absolutes
        rows = {}
        cols = {}
        for index in map_hash:
            #print(index)
            if(index[0] not in rows):
                rows[index[0]] = []
            if(index[1] not in cols):
                cols[index[1]] = []

            if(index[0] < min_all_present_row): min_all_present_row = index[0]
            if(index[1] < min_all_present_col): min_all_present_col = index[1]
            if(index[0] > max_all_present_row): max_all_present_row = index[0]
            if(index[1] > max_all_present_col): max_all_present_col = index[1]

        #print('picture shape', picture.shape)
        print('col modified:',min_all_present_row, max_all_present_row, min_all_present_col, max_all_present_col)
        blank = np.zeros((abs(min_all_present_row) + max_all_present_row + 1, abs(min_all_present_col) + max_all_present_col + 1, len(picture[0][1])))
        if(use_background):
            for pix_row in range(len(blank)):
                for pix_col in range(len(blank[0])):
                    blank[pix_row][pix_col] = picture[pix_row][pix_col]
            
        base_index = (abs(min_all_present_row) , abs(min_all_present_col))
        for x in self.map_hash:
            
            #print('map_hash[x].index[0]',map_hash[x].index[0],'map_hash[x].index[1]',map_hash[x].index[1],'self.base_index[0]',self.base_index[0],'self.base_index[1]',self.base_index[1],'x[0]',x[0],'x[1]',x[1])
        
            blank[base_index[0] + x[0]][base_index[1] + x[1]] = picture[self.map_hash[x].index[0]][self.map_hash[x].index[1]]
        if(show):
            plt.imshow(blank)
            plt.title(transformed_image_title)
            plt.show()
            plt.figure
            plt.imshow(picture)
            plt.title("Original Input")
            plt.show()
            plt.figure()
        
        return blank
    
    def batch_transform(self, picture_set, map_hash = None, show = False):
        transformed_pictures = []
        for picture in picture_set:
            transformed_pictures.append(self.transform(picture, map_hash = map_hash, show = show))
        return transformed_pictures
    

def animate_image_matrix(history_graph, name, fps):
    def update_frames(frame):

        return history_graph[frame]
    plt.rcParams['animation.ffmpeg_path'] = '/usr/local/Cellar/ffmpeg/5.1.1/bin/ffmpeg'
    fig = plt.figure()
    plot_frame = plt.imshow(history_graph[len(history_graph) - 1])
    
    plt.title(name)
    metadata = dict(title=name, artist='John Brown')
    writer = FFMpegWriter(fps = fps, metadata=metadata)
    
    with writer.saving(fig, name+'.mp4', dpi=100):
        for x in range(len(history_graph)):
            
            plot_frame.set_data(history_graph[x])
            writer.grab_frame()
        
def save_test():
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='cifar10', size = 1000)
    picture_test = Correlate.picture_pixel(test_data)
    picture_test.apply_association()
    outfile = open(cifar_test_key,'wb')
    pickle.dump(picture_test,outfile)

def load_test():
    infile = open(cifar_test_key,'rb')
    new_test = pickle.load(infile)
    print(type(new_test))

def working_test():
   
    infile = open(cifar_test_key,'rb')
    picture_test = pickle.load(infile)
    lattice_test = lattice(picture_test, (13,13))

    lattice_test.expand_anchor()

    lattice_test.display_self()
    

    print('Total Elapsed Time: ', time)
    
def index_distribution_test():
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='cifar10', size = 5000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    decrypted_data = Encrypt.decrypt_batch(encrypted_test_data, random_arrangement_grid)
    
    picture_test = Correlate.picture_pixel(test_data)
    picture_test.apply_association()
    dimensions = []
    latti = []
    for row in range(0, 28):
        for col in range(0,28):
            print('running iteration ',(row-12)*(col-12) + col - 12, 'on :',row,col)
            lattice_test = lattice(picture_test, (row,col))
            lattice_test.expand_anchor_better()
            dimensions.append(lattice_test.lifecycle())
            latti.append(lattice_test)

    row_av = 0 ; col_av = 0 ; data_inc = 0
    
    # not including anything smaller than 4
    for data in range(len(dimensions)):
        print(data,':',dimensions[data])
        if(dimensions[data][0] > 2 and dimensions[data][1] > 2):
            row_av += dimensions[data][0] 
            col_av += dimensions[data][1]
            data_inc +=1
    print('len dimensions', len(dimensions))
    print('average row of :',row_av/data_inc,'\naverage col of :', col_av/data_inc,'\nincluded samples: ',data_inc / len(dimensions))
    print(len(encrypted_test_data), len(decrypted_data))
    print(random_arrangement_grid[0])
    test_norm_pic = Correlate.picture_pixel(test_data)
    test_enc_pic = Correlate.picture_pixel(encrypted_test_data)
    test_norm_pic.apply_association() ; test_enc_pic.apply_association()
    print("PRINTING VH NODES")
    print(test_norm_pic.index_pixels_hash[(0,0)].vh_association_group)
    print(test_enc_pic.index_pixels_hash[(random_arrangement_grid[0][0][0],random_arrangement_grid[0][0][1])].vh_association_group)
    
    print(test_data[0][0][0])
    print(encrypted_test_data[0][random_arrangement_grid[0][0][0]][random_arrangement_grid[0][0][1]])
    grid = []
    for x in range(27, -1, -1):
        row = []
        for y in range(0, 28):
            try:
                row.append(str(dimensions[x*28 +y]))
            except:
                row.append(str(None))
        grid.append(row)
    s = [[str(e) for e in row] for row in grid]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))
    
   
def animation_test():
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='cifar10', size = 3000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    print(random_arrangement_grid[14][12], random_arrangement_grid[14][13],random_arrangement_grid[14][14])
    print(random_arrangement_grid[13][12], random_arrangement_grid[13][13],random_arrangement_grid[13][14] )
    print(random_arrangement_grid[12][12], random_arrangement_grid[12][13],random_arrangement_grid[12][14] )
    # encrypt data
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    decrypted_data = Encrypt.decrypt_batch(encrypted_test_data, random_arrangement_grid)
    picture_test = Correlate.picture_pixel(encrypted_test_data)
    picture_test.apply_association()

    lattice_test = lattice(picture_test, (random_arrangement_grid[13][13][0], random_arrangement_grid[13][13][1]))
    lattice_test.expand_anchor_better()
    image_matrix = lattice_test.grow(animation=True)[0]
    lattice_test.display_self()
    print('Image Matrix',image_matrix)
    transformed_pictures = []
    for map_hash in image_matrix:
        transformed_pictures.append(lattice_test.transform(test_data[0], map_hash, use_background=True))
    
    #animate_image_matrix(image_matrix, 'ring bind function example', 5)
def show_extraction(map_hash, transformed_image, base_image):
    # outputs a side by side of a transformed image and the removed from image
    reverse_image = base_image

    unit_length = len(transformed_image[0])
    #full_image = np.zeros((int(len(transformed_image)), int((2 + len(transformed_image[0]) + len(base_image[0]))), int(len(base_image[0][0]))))
    full_image = []
    for x in map_hash:
        base_image[map_hash[x].index[0]][map_hash[x].index[1]] = np.zeros((3))
    for row in range(len(transformed_image)):
        new_row = []
    
        new_row += base_image[row].tolist()
        full_image.append(new_row)
    return np.array(full_image)
    '''
    for row in range(len(full_image)):
        for col in range(len(full_image[row])):
            if(col < unit_length):
                full_image[row][col] = transformed_image[row][col]
            else: 
                if(col- unit_length < 2):
                    pass
                else:
                    
                    full_image[row][col] = base_image[row][col - unit_length - 2]
    for row in range(len(transformed_image)):
        for col in range(unit_length):
            full_image[row][col] = transformed_image[row][col]
    '''
    
def lattice_transform_test():
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='cifar10', size = 4000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    picture_test = Correlate.picture_pixel(encrypted_test_data)
    picture_test.apply_association()

    lattice_test = lattice(picture_test, (random_arrangement_grid[17][17][0], random_arrangement_grid[17][17][1]))
    #lattice_test = lattice(picture_test, (13,13))
    lattice_test.expand_anchor_better()
    map_hash_stack = lattice_test.lifecycle(animation=True)
    print("Starting Transform: check for animation")

    transformed_pictures = []
    
    for map_hash in map_hash_stack:
        image = lattice_test.transform(encrypted_test_data[0], map_hash, show = False, base_index= (14,14))
        transformed_pictures.append(image)

    
    
    animate_image_matrix(transformed_pictures, 'Lattice Construction Extraction Visualization (17,17): Encrypted data', 64)
    
    image = lattice_test.transform(encrypted_test_data[0], map_hash_stack[20], show = False, base_index= (14,14))
    plt.imshow(show_extraction(map_hash_stack[20], image, encrypted_test_data[0]))
    plt.show()
    plt.figure()

def lattice_manual_creation():
    pass
  #lattice_test.display_self()

def mnist_test():
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='mnist', size = 3000)
   
    
    picture_test = Correlate.picture_pixel(test_data)
    picture_test.apply_association()

    lattice_test = lattice(picture_test, (13,13))

    
    print("UNCERTAIN: ", lattice_test.uncertain)
    lattice_test.expand_anchor_better()
    
    ring = lattice_test.build_ring()
    print('outputted ring: ',ring)
    lattice_test.display_self()
    lattice_test.bind_ring(ring)
    lattice_test.grow(animation=True)
    lattice_test.grow(animation=True)


#lattice_transform_test()
