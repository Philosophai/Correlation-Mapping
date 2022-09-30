import Gather
import Encrypt
import Correlate
import pickle
import numpy as np
import matplotlib.pyplot as plt
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
        self.vh = index_pixel.vh_association_group
        self.diag = index_pixel.diag_association_group

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

    def place_by_label(self, center_index, to_be_placed_index, direction):
        if(direction == 'up'): self.place_up(center_index, to_be_placed_index)    
        if(direction == 'down'): self.place_down(center_index, to_be_placed_index)  
        if(direction == 'left'): self.place_left(center_index, to_be_placed_index)  
        if(direction == 'right'): self.place_right(center_index, to_be_placed_index)  

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

    def build_ring(self):

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


    def bind_ring(self, ring):
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
        # place alpha 
        self.place_by_label(alpha_dock.index, alpha_link, neighbour_choice[1])
        # place beta off alpha
        self.place_by_label( alpha_link, beta_link, extract_direction_from_difference(difference_between_docks))

        print(ring[2])
        for link in range(2, len(ring)):
            print(link, bounds)
            
            location_direction = self.find_next_spot(ring[link][1][0], bounds) ; direction = location_direction[1]
            #print('index to be placed',ring[link][0],'location:', location_direction)
            self.place_by_label(ring[link][1][0], ring[link][0], direction)
            #self.display_self()
        pass

    
    def grow(self):
        try:
            start = time()
            ring = self.build_ring()
            self.bind_ring(ring)
            #self.display_self()
            print("Finished growth in ", time() - start)
            return [0, True]
        except:
            dimensions = self.display_self()
            print("Made it this far before an error.", dimensions)
            return [dimensions, False]

    def lifecycle(self):
        dimensions_life = [] ; alive = True
        while(alive):
            dimensions_life = self.grow()
            alive = dimensions_life[1]
        return dimensions_life[0]

    def transform(self, picture):
        blank = np.zeros((len(picture), len(picture[0]) , len(picture[0][1])))
        print(blank.shape)
        for x in self.map_hash:
            print(x, (self.base_index[0] + x[0],self.base_index[1] + x[1]) , self.map_hash[x].index)
            blank[self.base_index[0] + x[0]][self.base_index[1] + x[1]] = picture[self.map_hash[x].index[0]][self.map_hash[x].index[1]]
        plt.imshow(blank)
        plt.show()
        plt.figure
        plt.imshow(picture)
        plt.show()
        plt.figure()


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
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='cifar10', size = 1000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    decrypted_data = Encrypt.decrypt_batch(encrypted_test_data, random_arrangement_grid)
    
    picture_test = Correlate.picture_pixel(test_data)
    picture_test.apply_association()
    dimensions = []
    latti = []
    for row in range(0, 31):
        for col in range(0,31):
            print('running iteration ',(row-12)*(col-12) + col - 12, 'on :',row,col)
            lattice_test = lattice(picture_test, (row,col))
            lattice_test.expand_anchor_better()
            dimensions.append(lattice_test.lifecycle())
            latti.append(lattice_test)
    latti[0].display_self()
    latti[1].display_self()
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
   
def another_test():
    np.random.seed = 1
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='cifar10', size = 3000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    print(random_arrangement_grid[14][12], random_arrangement_grid[14][13],random_arrangement_grid[14][14])
    print(random_arrangement_grid[13][12], random_arrangement_grid[13][13],random_arrangement_grid[13][14] )
    print(random_arrangement_grid[12][12], random_arrangement_grid[12][13],random_arrangement_grid[12][14] )
    # encrypt data
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    decrypted_data = Encrypt.decrypt_batch(encrypted_test_data, random_arrangement_grid)
    picture_test = Correlate.picture_pixel(decrypted_data)
    picture_test.apply_association()
    lattice_test = lattice(picture_test, (13,14))
    lattice_test.expand_anchor_better()
    lattice_test.display_self()
    
    print(lattice_test.lifecycle())
    

    
def lattice_transform_test():
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='cifar10', size = 1000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    picture_test = Correlate.picture_pixel(encrypted_test_data)
    picture_test.apply_association()
    lattice_test = lattice(picture_test, (14,13))
    lattice_test.expand_anchor_better()
    lattice_test.lifecycle()
    print("Starting Transform:")
    lattice_test.transform(encrypted_test_data[0])
    plt.imshow(test_data[0])
    plt.show()
    plt.figure()

lattice_transform_test()