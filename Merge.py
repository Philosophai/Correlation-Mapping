from operator import inv
from symbol import and_test
from tracemalloc import start
import math
import Gather
import Encrypt
import Correlate
import Map

# I know the code is long as fuck, fuck it.


def show_map( map_example, non_indexed = False):
    max_row = 0;min_row = 0;  max_col = 0; min_col = 0
    print("DISPLAYING LATTICE")
    for x in map_example:
        
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
                if(non_indexed):
                    row.append(str(map_example[(x,y)]))
                
                else: row.append(str(map_example[(x,y)].index))
            except:
                row.append(str(None))
        grid.append(row)
    s = [[str(e) for e in row] for row in grid]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))
    return (row_space + 1, col_space + 1)

def rotate_map(map, turns):
    def rotate(origin, point, angle):

        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return round(qx), round(qy)
    #show_map(map)
    new_map = {}
    
    for index in map:
        #print(index, 'turned', turns,' :', rotate((0,0) , index,  math.radians(90*turns)))
        new_map[rotate((0,0) , index,  math.radians(90*turns))] = map[index]
    #show_map(new_map)
    return new_map

def vertically_invert_map(map):
    new_map = {}
    #show_map(map)
    for index in map:
        new_map[(index[0], -1 * index[1])] = map[index]
    #show_map(new_map)
    return new_map

class orientation_node():
    def __init__(self, index):
        self.index = index
        self.map_index =  None
        self.up = None
        self.down = None
        self.left = None
        self.right = None
        self.upright = None
        self.downleft = None
        self.upleft = None
        self.downright = None
        self.relation = [self.up, self.upright, self.right, self.downright, self.down, self.downleft, self.left, self.upleft]
        self.relations = []
    def map_orient(self, map):
        
        for map_index in map:
            if(map[map_index].index == self.index):
                self.map_index = map_index
        try:
            self.up = map[(self.map_index[0] + 1, self.map_index[1])].index
        except:
            self.up = None
        try:
            self.down = map[(self.map_index[0] - 1, self.map_index[1])].index
        except:
            self.down = None
        try:
            self.left = map[(self.map_index[0] , self.map_index[1] - 1)].index
        except:
            self.left = None
        try:
            self.right = map[(self.map_index[0] , self.map_index[1] + 1)].index
        except:
            self.right = None

        try:
            self.upright = map[(self.map_index[0] + 1, self.map_index[1] + 1)].index
        except:
            self.upright = None
        try:
            self.downleft = map[(self.map_index[0] - 1, self.map_index[1] - 1)].index
        except:
            self.downleft = None
        try:
            self.upleft = map[(self.map_index[0] + 1 , self.map_index[1] - 1)].index
        except:
            self.upleft = None
        try:
            self.downright = map[( 1- self.map_index[0] , self.map_index[1] + 1)].index
        except:
            self.downright = None
        return [self.up, self.upright, self.right, self.downright, self.down, self.downleft, self.left, self.upleft]
        
    
    def orientation_analyze(self, new_map):
        base = self.orient_compare(new_map)
        turn_90 = self.orient_compare(rotate_map(new_map, 1))
        turn_180 = self.orient_compare(rotate_map(new_map, 2))
        turn_270 = self.orient_compare(rotate_map(new_map, 3))
        inverted_map = vertically_invert_map(new_map)
        base_invert = self.orient_compare(inverted_map)
        inverted_90 = self.orient_compare(rotate_map(inverted_map, 1))
        inverted_180 = self.orient_compare(rotate_map(inverted_map, 2))
        inverted_270 = self.orient_compare(rotate_map(inverted_map, 3))
        #print("INVERTED 270 vs 270")
        #print("INVERTED")
        #show_map(rotate_map(inverted_map, 3))
        #rint("RIGHT")
        #how_map(rotate_map(new_map, 3))
        print("Orientation Similarity: base:",base,'\n90:',turn_90,'\n180:', turn_180, '\n270:', turn_270,"base:",base_invert,'\ninv 90:',inverted_90,'\ninv 180:', inverted_180, '\ninv 270:', inverted_270)
        turns = [base, turn_90, turn_180, turn_270, base_invert, inverted_90, inverted_180, inverted_270 ]
        print(turns)
        index = turns.index(max(turns))
        if(index > 3):
            # true for vertically invert
            return [True, index - 4]
        return [False, index]

    def orient_compare(self, new_map):
        map_index = None
        up = None
        down = None
        left = None
        right = None
        upright = None
        downleft = None
        upleft = None
        downright = None

        similarity = 0

        for new_map_index in new_map:
            if(new_map[new_map_index].index == self.index):
                map_index = new_map_index
        try:
            up = new_map[(map_index[0] + 1, map_index[1])].index
            if(up == self.up):
                similarity += 1
            if( up != self.up and up != None and self.up != None):
                similarity -= 1

        except:
            up = None
        
        try:
            down = new_map[(map_index[0] - 1, map_index[1])].index
            if(down == self.down ): similarity += 1
            if( down != self.down and down != None and self.down != None):
                similarity -= 1

        except:
            down = None
        try:
            left = new_map[(map_index[0] , map_index[1] - 1)].index
            if(left== self.left ): similarity += 1
            if( left != self.left and left != None and self.left != None):
                similarity -= 1
        except:
            left = None
        try:
            right = new_map[(map_index[0] , map_index[1] + 1)].index
            if(right == self.right ): similarity += 1
            if( right != self.right and right != None and self.right != None):
                similarity -= 1
        except:
            right = None

        try:
            upright = new_map[(map_index[0] + 1, map_index[1] + 1)].index
            if(upright == self.upright ): similarity += 1
            if( upright != self.upright and upright != None and self.upright != None):
                similarity -= 1
        except:
            upright = None
        try:
            downleft = new_map[(map_index[0] - 1, map_index[1] - 1)].index
            if(downleft == self.downleft ): similarity += 1
            if( downleft != self.downleft and downleft != None and self.downleft != None):
                similarity -= 1
        except:
            downleft = None
        try:
            upleft = new_map[(map_index[0] + 1 , map_index[1] - 1)].index
            if(upleft == self.upleft ): similarity += 1
            if( upleft != self.upleft and upleft != None and self.upleft != None):
                similarity -= 1
        except:
            upleft = None
        try:
            downright = new_map[( 1- map_index[0] , map_index[1] + 1)].index
            if(downright== self.downright ): similarity += 1
            if( downright != self.downright and downright != None and self.downright != None):
                similarity -= 1
        except:
            downright = None
        
        return similarity
        '''
        show_map(new_map)
        print('SIMILARITY OF BASE ORIENTATION: ', similarity)
        one_turn_90 = [left, upleft, up, upright, right, downright, down, downleft] ; sim_90 = 0
        one_turn_180 = [down, downleft, left, upleft, up, upright, right, downright] ; sim_180 = 0
        one_turn_270 = [right, downright, down, downleft, left, upleft, up, upright] ; sim_270 = 0
        for node in range(8):
            print(self.relation[node],one_turn_90[node],one_turn_180[node],one_turn_270[node] )
            if(self.relation[node] != None and self.relation[node] == one_turn_90[node]): sim_90 += 1
            if(self.relation[node] != None and self.relation[node] == one_turn_180[node]): sim_180 += 1
            if(self.relation[node] != None and self.relation[node] == one_turn_270[node]): sim_270 += 1
        print("SIMILARITIES OF ROTATIONS:\n90:",sim_90,'\n180:',sim_180,'\n270:',sim_270)
        '''
               
    def collect_orientations(self, map_list):
        def new_addition_test(old_set, new_member):
            different_test = []
            print('relation')
            for unique in old_set:
                print('unique')
                unique_test = []
                for start_shift in range(0,8):
                    print(start_shift)
                    same = True
                    for element in range(0,8):
                        print((start_shift + element)%8)
                        print(new_member[(start_shift + element)%8], unique[(start_shift + element)%8] )
                        if(new_member[(start_shift + element)%8]!= unique[(start_shift + element)%8] and new_member[(start_shift + element)%8] != None and unique[(start_shift + element)%8] != None):
                            same = False
                    unique_test.append(same)
                print(unique_test)
                different_test.append(max(unique_test))
            return max(different_test)
            
        node_in = []
        relations = []
        print("COLLECTING ORIENTATIONS")
        for map in map_list:
            for index in map_list[map]:
                if(map_list[map][index].index == self.index):
                    node_in.append([map, index])
                    relations.append(self.map_orient(map_list[map]))
        for x in range(len(relations)):
            print(node_in[x], relations[x])

        unique_relations = [relations[0]] ; new_added = []
        print(unique_relations[0])
        new_added = []
        for relation in range(1, len(relations)):
            same = new_addition_test(unique_relations, relations[relation])
            print('function difference test',same)
            if(not same):
                new_same = False
                if(len(new_added) > 0):
                    new_same = new_addition_test(new_added, relations[relation])
                if(new_same == False):
                    new_added.append(relations[relation])
        for new in new_added:
            print("NEW ADDITION: ",new)
        self.relations.append(relations[0])
        for new in new_added:
            self.relations.append(new)

        for r in self.relations:
            print(r)
        
    def find_orientation(self):
        pass

                

def central_align(anchor_map, map_set, indice_list):
    print("CENTRAL ALIGNMENT")
    print(anchor_map) 
    shift_set = {}
    for map_example in map_set:
        new_map = {}
        print(map_example) ; shift = []
        for other_index in map_set[map_example]:
            if(map_set[map_example][other_index].index in indice_list):
                print("FOUND ",map_set[map_example][other_index].index,' in anchor! from ', map_example)
                print("Map index: ", other_index)
                for anchor_index in anchor_map:
                    if(anchor_map[anchor_index].index == map_set[map_example][other_index].index):
                        print("FOUND MATCHING NODE IN ANCHOR ", anchor_map[anchor_index].index)
                        print("other index: ", other_index, 'anchor_index: ', anchor_index)
                        difference = (anchor_index[0] - other_index[0], anchor_index[1] - other_index[1])
                        print(difference,'applied to other_node = ', (other_index[0] + difference[0],other_index[1] + difference[1]) )     
        for other_index in map_set[map_example]:
            new_map[(other_index[0] + difference[0],other_index[1] + difference[1])] = map_set[map_example][other_index]
        shift_set[map_example] = new_map
    return shift_set

                

                    



        



def rotate_align(anchor_map, map_set, indice_list):
    # I want them all to be the same orientation
    oriented_maps = {}
    orientation_node_set = []
    for map_example in map_set:
        node_in_anchor = []
        for index in map_set[map_example]:
            if(map_set[map_example][index].index in indice_list):
                node_in_anchor.append([index, map_set[map_example][index].index])
        orientation_node_set.append([map_example, node_in_anchor])
    
    relations = []
    print("ORIENTATION")
    for x in orientation_node_set:
        print(x)
        nodes_to_be_oriented = [y[1] for y in x[1]]
        for node in nodes_to_be_oriented:
            print(node)
            new_node = orientation_node(node)
            new_node.map_orient(anchor_map)
            print(x)
            #show_map(map_set[x[0]])
            invert_turns = new_node.orientation_analyze(map_set[x[0]])
            print("VERTICALLY INVERT:", invert_turns[0],' ROTATE:', invert_turns[1])
            if(invert_turns[0]):
                print('VERTICALLY INVERTED')
                oriented_maps[x[0]] = rotate_map(vertically_invert_map( map_set[x[0]]), invert_turns[1] )
            else:
                oriented_maps[x[0]] = rotate_map(map_set[x[0]], invert_turns[1])
            print("ANCHOR")
            show_map(anchor_map)
            print("ORIGINAL")
            show_map(map_set[x[0]])
            print("TRANSFORMED")
            show_map(oriented_maps[x[0]])
    print("ANCHOR")
    show_map(anchor_map)
    print("SHOWING ALL THE NON_ORIENTED VS OREINTED ")

    
    return oriented_maps

def pull_indice_list(map):
    indice_list = []
    for x in map:
        indice_list.append(map[x].index)
    return indice_list

        
class Overlaid_Lattice():
    def __init__(self):
        self.map = {}
    def initiate_map(self, anchor_set):
        base_key = list(anchor_set.keys())[0]
        for x in anchor_set[base_key]:
            if(x not in self.map):
                self.map[x] = {}
        for key in anchor_set:
            for index in anchor_set[key]:
                if(anchor_set[key][index].index not in self.map[index]):
                    self.map[index][anchor_set[key][index].index] = 1
                else:
                    self.map[index][anchor_set[key][index].index] += 1
        
    def generate_current_map(self):
        minimum_map_row = 0 ; maximum_map_row = 0;
        minimum_map_col = 0 ; maximum_map_col = 0;
        for key in self.map:
            if(key[0] < minimum_map_row): minimum_map_col = key[0]
            if(key[1] < minimum_map_col): minimum_map_col = key[1]
            if(key[0] > maximum_map_row): maximum_map_row = key[0]
            if(key[1] > maximum_map_col): maximum_map_col = key[1]
        print('printing bounds')
        print(max(abs(minimum_map_row) , maximum_map_row,abs(minimum_map_col), maximum_map_col) + 3)
        print("printing map values")
        new_map = {} ; map_added = []
        visited = {}
        for interior_r_bounds in range(0, max(abs(minimum_map_row) , maximum_map_row,abs(minimum_map_col), maximum_map_col) + 1):

            for key_r in range(interior_r_bounds,-1 * interior_r_bounds,-1 ):
                for key_c in range( interior_r_bounds,-1 * interior_r_bounds, -1 ):
                    if((key_r, key_c) not in visited):
                        try:
                            new_map[(key_r, key_c)] = [(None, None), -1]
                            check_if_real_sloppy = self.map[(key_r, key_c)]
                            for possible_index in self.map[(key_r, key_c)]:
                                if(self.map[(key_r, key_c)][possible_index] > new_map[(key_r, key_c)][1]):

                                    new_map[(key_r, key_c)] = [possible_index, self.map[(key_r, key_c)][possible_index]]
                            

                        except:

                            print((key_r, key_c), 'not in map!')
                        visited[(key_r, key_c)] = True
        for m in new_map:
            new_map[m] = new_map[m][0]
            print(m, new_map[m])
        return new_map

        
            

        



class Compound_Lattice():
    def __init__(self, data):
        self.map_list = {} 
        self.picture  = Correlate.picture_pixel(data)
        self.picture.apply_association()
        self.uncertain = False
        height = data[0].shape[0] ; width = data[0].shape[1]
        for row in range(0,height):
            for col in range(0, width):
                if(self.picture.index_pixels_hash[(row, col)].vh_association_group[3][0] != 0):
                    new_lattice = Map.lattice(self.picture, (row, col))
                    new_lattice.expand_anchor_better()
                    new_lattice.lifecycle()
                    if(new_lattice.uncertain):
                        self.uncertain = True
                    
                    self.map_list[(row,col)] = new_lattice.map_hash
                
    
    def display_map(self, choice_index):
        max_row = 0;min_row = 0;  max_col = 0; min_col = 0
        print("DISPLAYING LATTICE", choice_index)
        for x in self.map_list[choice_index]:
            
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
                    row.append(str(self.map_list[choice_index][(x,y)].index))
                except:
                    row.append(str(None))
            grid.append(row)
        s = [[str(e) for e in row] for row in grid]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in s]
        print('\n'.join(table))
        return (row_space + 1, col_space + 1)
    
    def find_power_anchor(self):
        number_samples = len(self.picture.index_pixels[0].data)
        pixels = []
        for pixel in self.picture.index_pixels:
            pixels.append([pixel.index, sum(pixel.data)/ number_samples])
            #print(pixel.index, sum(pixel.data)/ number_samples)
        sorted_pixels = sorted(pixels, key = lambda x:x[1][0], reverse = True)
        print(sorted_pixels[0])
        print(sorted_pixels[1])
        print(sorted_pixels[2])
        self.power_anchor_list = sorted_pixels

    def Orient_around_anchor(self):


        start_anchor = self.power_anchor_list[0][0]
        start_map = self.map_list[start_anchor]
        start_index_list = pull_indice_list(start_map)
        print("ANCHOR", start_anchor)
        self.display_map(start_anchor)
        for x in start_map:
            print('x:',x,'starting_map[x]',start_map[x].index)
        included_maps = {} ; included_n = 0
        for map in start_index_list:
            included_n = 0
            for map_index in self.map_list[map]:
                if(self.map_list[map][map_index].index in start_index_list and map != self.power_anchor_list[0][0]):
                    print('found one!', included_n)
                    included_n += 1
                if(included_n == 2 and map not in [x[0] for x in included_maps]):
                    # EVERYTHING AFTER THIS IS JUST INTRODUCING CHALLENGES FOR TESTING. just need the included_maps[map] = self.map_list[map]
                    if(len(included_maps) == 1):
                        included_maps[map] = vertically_invert_map(rotate_map(self.map_list[map], 2))

                    else: included_maps[map] = rotate_map(self.map_list[map], 1)
        
        #for map in included_maps:
        #    self.display_map(map)
        #new_map = rotate_map(self.map_list[(14,15)], 1)
        #show_map(new_map)
        print("\n\nORIENTING MAP\n")
        oriented_maps = rotate_align(start_map, included_maps, start_index_list)
        oriented_maps[start_anchor] = start_map
        return oriented_maps





    def merge_restricted(self, restricted_oriented_maps):
        # zeroeth contains all the nodes
        

        centralized = central_align(restricted_oriented_maps[list(restricted_oriented_maps.keys())[0]], restricted_oriented_maps, pull_indice_list(restricted_oriented_maps[list(restricted_oriented_maps.keys())[0]]))
        for c in centralized:
            show_map(centralized[c])
        new_overlaid = Overlaid_Lattice()
        new_overlaid.initiate_map(centralized)
        show_map(new_overlaid.generate_current_map(), True)

        

    def bounded_align_anchor(self, anchor_map_index, bounds):
        map_in_bounds = {} ; restricted_map = {}
        for row_indices in range(bounds[0], bounds[2] + 1):
            for col_indices in range(bounds[1], bounds[3] + 1):
                map_in_bounds[self.map_list[anchor_map_index][(row_indices, col_indices)].index] = self.map_list[self.map_list[anchor_map_index][(row_indices, col_indices)].index]
                restricted_map[(row_indices, col_indices)] = self.map_list[anchor_map_index][(row_indices, col_indices)]
        restricted_indices = pull_indice_list(restricted_map)
        show_map(restricted_map)
        oriented_maps = rotate_align(restricted_map, map_in_bounds, restricted_indices)
        for x in oriented_maps:
            print('oriented',x)
        restricted_oriented_maps = {}

        for oriented_map in oriented_maps:
            restrict = {}
            for index in oriented_maps[oriented_map]:
                if(oriented_maps[oriented_map][index].index in restricted_indices):

                    restrict[index] = oriented_maps[oriented_map][index]
            restricted_oriented_maps[oriented_map] = restrict
        print('number of restricted maps', len(restricted_oriented_maps))
   
        self.merge_restricted(restricted_oriented_maps)
        
        


        





def working_test():
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='mnist', size = 4000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    test = Compound_Lattice(test_data)
    test.display_map((13,13))
    test.find_power_anchor()
    test.bounded_align_anchor(test.power_anchor_list[1][0], (0,0,1,1))
    #orientation_test = orientation_node((test.power_anchor_list[1][0]))
    #orientation_test.collect_orientations(test.map_list)


    #oriented_maps = test.Orient_around_anchor(oriented_maps)
    #print("ORIENTED LENGTH: ",len(oriented_maps))
working_test()