import math
from multiprocessing.sharedctypes import Value
import Gather
import Encrypt
import Correlate
import Map
from time import time
import pickle

# I know the code is long as fuck, fuck it.
'''
Remove after DEBUG:
stop arg in update_map and call to it in bounded_align .. merge_restricted
generate_currentmap shit
'''

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
                
                else: 
                    if(map_example[(x,y)] != (None, None)):
                        row.append(str(map_example[(x,y)].index))
                    else:
                        row.append(str(None))
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
        #print('for index, ')
        #print("Orientation Similarity: base:",base,'\n90:',turn_90,'\n180:', turn_180, '\n270:', turn_270,"base:",base_invert,'\ninv 90:',inverted_90,'\ninv 180:', inverted_180, '\ninv 270:', inverted_270)
        turns = [base, turn_90, turn_180, turn_270, base_invert, inverted_90, inverted_180, inverted_270 ]
        
        index = turns.index(max(turns))
        if(index > 3):
            # true for vertically invert
            return [True, index - 4, max(turns)]
        return [False, index, max(turns)]

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
            #print('relation')
            for unique in old_set:
                #print('unique')
                unique_test = []
                for start_shift in range(0,8):
                    #print(start_shift)
                    same = True
                    for element in range(0,8):
                        #print((start_shift + element)%8)
                        #print(new_member[(start_shift + element)%8], unique[(start_shift + element)%8] )
                        if(new_member[(start_shift + element)%8]!= unique[(start_shift + element)%8] and new_member[(start_shift + element)%8] != None and unique[(start_shift + element)%8] != None):
                            same = False
                    unique_test.append(same)
                #print(unique_test)
                different_test.append(max(unique_test))
            return max(different_test)
            
        node_in = []
        relations = []
        #print("COLLECTING ORIENTATIONS")
        for map in map_list:
            for index in map_list[map]:
                if(map_list[map][index].index == self.index):
                    node_in.append([map, index])
                    relations.append(self.map_orient(map_list[map]))
        #for x in range(len(relations)):
            #print(node_in[x], relations[x])

        unique_relations = [relations[0]] ; new_added = []
        #print(unique_relations[0])
        new_added = []
        for relation in range(1, len(relations)):
            same = new_addition_test(unique_relations, relations[relation])
            #print('function difference test',same)
            if(not same):
                new_same = False
                if(len(new_added) > 0):
                    new_same = new_addition_test(new_added, relations[relation])
                if(new_same == False):
                    new_added.append(relations[relation])
        #for new in new_added:
            #print("NEW ADDITION: ",new)
        self.relations.append(relations[0])
        for new in new_added:
            self.relations.append(new)

        #for r in self.relations:
            #print(r)
        
    def find_orientation(self):
        pass
              
def rotate_align(anchor_map, map_set, indice_list):
    # I want them all to be the same orientation
    oriented_maps = {}
    orientation_node_set = []
    for map_example in map_set:
        node_in_anchor = []
        for index in map_set[map_example]:
            if(map_set[map_example][index].index in indice_list ):
                node_in_anchor.append([index, map_set[map_example][index].index])
        orientation_node_set.append([map_example, node_in_anchor])
    
    relations = []
    #print("ORIENTATION")
    for x in orientation_node_set:
        #print(x)
        max_orientation_value = -1000000
        nodes_to_be_oriented = [y[1] for y in x[1]]
        for node in nodes_to_be_oriented:
            #print(node)
            new_node = orientation_node(node)
            new_node.map_orient(anchor_map)
            
            #show_map(map_set[x[0]])
            #print("\n\nOPERATING ON :", x[0], 'specifically at index ', node)
            invert_turns_value = new_node.orientation_analyze(map_set[x[0]])
            #print("VERTICALLY INVERT:", invert_turns_value[0],' ROTATE:', invert_turns_value[1])
            if(max_orientation_value < invert_turns_value[2]):
                max_orientation_value = invert_turns_value[2]
                if(invert_turns_value[0]):
                    #print('VERTICALLY INVERTED')
                    oriented_maps[x[0]] = rotate_map(vertically_invert_map( map_set[x[0]]), invert_turns_value[1] )
                else:
                    oriented_maps[x[0]] = rotate_map(map_set[x[0]], invert_turns_value[1])
            #print("ANCHOR")
            #show_map(anchor_map)
            #print("ORIGINAL")
            #show_map(map_set[x[0]])
            #print("TRANSFORMED")
            #show_map(oriented_maps[x[0]])
    #print("ANCHOR")
    #show_map(anchor_map)
    

    
    return oriented_maps

def central_align2(anchor_map, map_set, indice_list):
    '''
    old but dont want to throw out yet
    '''
    #print("CENTRAL ALIGNMENT")
    #print(anchor_map) 
    shift_set = {}
    for map_example in map_set:
        new_map = {}
        #print('\n\n\nMAP SET INDEX:',map_example) ; shift = []
        for other_index in map_set[map_example]:
            if(map_set[map_example][other_index].index in indice_list):
                #print("FOUND ",map_set[map_example][other_index].index,' in anchor! from ', map_example)
                #print("Map index: ", other_index)
                for anchor_index in anchor_map:
                    if(anchor_map[anchor_index].index == map_set[map_example][other_index].index):
                        #print("FOUND MATCHING NODE IN ANCHOR ", anchor_map[anchor_index].index)
                        #print("other index: ", other_index, 'anchor_index: ', anchor_index)
                        difference = (anchor_index[0] - other_index[0], anchor_index[1] - other_index[1])
                        #print(difference,'applied to other_node = ', (other_index[0] + difference[0],other_index[1] + difference[1]) )     
        for other_index in map_set[map_example]:
            new_map[(other_index[0] + difference[0],other_index[1] + difference[1])] = map_set[map_example][other_index]
        shift_set[map_example] = new_map
        #print('\n\n\n')
    return shift_set

def central_align(anchor_map, map_set, indice_list, score = False):
    #print("CENTRAL ALIGNMENT")
    #print(anchor_map) 
    shift_set = {}
    for map_example in map_set:
        new_map = {} ; best_similarity_value = 0
        #print('\n\n\nMAP SET INDEX:',map_example) ; shift = []
        for other_index in map_set[map_example]:
            if(map_set[map_example][other_index].index in indice_list):
                #print("FOUND ",map_set[map_example][other_index].index,' in anchor! from ', map_example)
                #print("Map index: ", other_index)
                for anchor_index in anchor_map:
                    if(anchor_map[anchor_index].index == map_set[map_example][other_index].index):
                        #print("FOUND MATCHING NODE IN ANCHOR ", anchor_map[anchor_index].index)
                        #print("other index: ", other_index, 'anchor_index: ', anchor_index)
                        difference = (anchor_index[0] - other_index[0], anchor_index[1] - other_index[1])
                        #print(difference,'applied to other_node = ', (other_index[0] + difference[0],other_index[1] + difference[1]) )   
                        temp_new_map = {} ; similarity_value = 0
                        for other_index in map_set[map_example]:
                            temp_new_map[(other_index[0] + difference[0],other_index[1] + difference[1])] = map_set[map_example][other_index]
                        for temp_index in temp_new_map:
                            try:
                                if(temp_new_map[temp_index].index == anchor_map[temp_index].index):
                                    similarity_value += 1
                            except:
                                pass
                        if(similarity_value > best_similarity_value):
                            new_map = temp_new_map ; best_similarity_value = similarity_value
        shift_set[map_example] = new_map
        #print('\n\n\n')
    if(score): return [shift_set, best_similarity_value]
    return shift_set             


def restrict(map_set, bounds):
    new_set = {}
    for map in map_set:
        new_map = {}
        for indice in map_set[map]:
            if(indice[0] >= bounds[0] and indice[0] <= bounds[2] and indice[1] >= bounds[1] and indice[1] <= bounds[3]):
                new_map[indice] = map_set[map][indice]
        new_set[map] = new_map               

    return new_set

def pull_indice_list(map):
    indice_list = []
    for x in map:
       
        indice_list.append(map[x].index)
    return indice_list

def coordinate_distance(alpha, beta):
    return (( alpha[0] - beta[0])**2 + (alpha[1] - beta[1])**2)**(1/2)

class position_node():
    def __init__(self, index):
        self.index = index
        self.positions = {(1,0): {},(1,1): {},(0,1): {},(-1,1): {},(-1,0): {},(-1,-1): {},(0,-1): {},(1,-1): {} }
        
    def position_compile(self, map_list):
        for map in map_list:
            for index in map_list[map]:
                if(map_list[map][index].index == self.index):
                     #print("found", self.index,' in map', map)
                     for r in range(-1, 2):
                        for c in range(-1, 2):
                            try:
                                comparative_index = (index[0] + r, index[1] + c)
                                if(map_list[map][comparative_index].index in self.positions[(r,c)]):
                                    self.positions[(r,c)][map_list[map][comparative_index].index] += 1
                                else:
                                    self.positions[(r,c)][map_list[map][comparative_index].index] = 1
                            except:
                                pass
 
    def display_positions(self):
        print("INDICE::: ",self.index)
        for index in self.positions:
            print('relative index:',index,'\n\n')
            for key in self.positions[index]:
                print('\tkey:',key,': ', self.positions[index][key])
    
    def evaluate_map(self, map):
        for index in map:
            if(map[index].index == self.index):
                score = 0
                for r in range(-1, 2):
                    for c in range(-1, 2):
                        try:
                            score += self.positions[(r,c)][map[(index[0] + r, index[1] + c)].index]
                        except:
                            pass
                return score

class Position_Lattice():
    def __init__(self, map_list):
        self.indices = {} ; self.map = None
        for map in map_list:
            for index in map_list[map]:
                if(map_list[map][index].index not in self.indices):
                    self.indices[map_list[map][index].index] = position_node(map_list[map][index].index)
        for p_node in self.indices:
            #print(self.indices[p_node].index)
            self.indices[p_node].position_compile(map_list)
            #show_map(map_list[self.indices[p_node].index])
            #self.indices[p_node].display_positions()
        #print('score:',self.indices[(14,14)].evaluate_map(map_list[(14,14)]))
    def evaluate_map(self, map):
        score = 0
        for index in self.indices:
            try:
                score += self.indices[index].evaluate_map(map)
            except:
                pass
        return score
    def optimize_map(self):
        def in_map(current_map, added_index):

            for p in current_map:
                if(current_map[p].index == added_index):
                    return p
            return False

        def valid_new_position(current_map, added_index, new_position):
            if(new_position in current_map):
                return False
            #print('valid_new_position check for ', added_index.index, 'at: ', new_position)
            #print('current map:', current_map)
            
            for index in self.indices:
                index_position = in_map(current_map, index)
                if(index_position):
                    #print('print index position', index)
                    
                    for p in self.indices[index].positions:
                        if(added_index.index in self.indices[index].positions[p] and new_position == ( index_position[0] + p[0] , index_position[1] + p[1]) ):
                            #print("FOUND THE RIGHT SPOT SO ITS GOOD")
                            return True
            return False
            
        def compile_possibilites(current_map, added_index, new_position, max_depth, current_depth):
            # check if the new_position is unoccupied
            maps = [] ; current_depth += 1
            
            if(not in_map(current_map, added_index.index)):
                if(valid_new_position(current_map, added_index, new_position)):
                # check if the added_index is already in the map
                
                    # make a new map
                    temp = current_map.copy()
                    temp[new_position] = added_index
                    if(current_depth == max_depth):
                        return temp
                    for p in added_index.positions:
                        for element in added_index.positions[p]:
                            maps.append(compile_possibilites( temp, self.indices[element], (new_position[0] + p[0], new_position[1] + p[1]), max_depth, current_depth))
            
            return maps

        def unwrap_compile(maps, current_depth, desired_depth, unwrapped_maps):
            current_depth += 1 ; loop_count = 0
            if(desired_depth == current_depth):
                loop_count = len(unwrapped_maps)
            for map in maps:
                if(desired_depth == current_depth):
                    if(len(map) > 1):
                        unwrapped_maps[loop_count] = map
                        loop_count += 1
                    
                else:
                    unwrap_compile(map, current_depth, desired_depth, unwrapped_maps)
                 
        
        #print("OPTIMIZE MAP")
        maps = []
        map_start = {}
        map_start[(0,0)] =  self.indices[list(self.indices.keys())[0]]
        depth = len(self.indices) - 1
        #print('MAP Start:',map_start[(0,0)].index)
        for p in map_start[(0,0)].positions:
            for element in map_start[(0,0)].positions[p]:
                #print('Position:',p,' element :', element)
                maps.append(compile_possibilites(map_start, self.indices[element], p, depth, 0))
        
        #for index in self.indices:
            #print('Index:',index)
        #    for p in self.indices[index].positions:
        #        print(p,':',self.indices[index].positions[p])
        #print("PRINTING MAPS:", len(maps))
        
        unwrapped = {} ; unwrap_compile(maps, 0,depth, unwrapped)
        max_score = 0 ; optimal_map = {}
        for m in unwrapped:
            #print(m)
            #show_map(unwrapped[m])
            score = self.evaluate_map(unwrapped[m])
            if(max_score < score):
                max_score = score; optimal_map = unwrapped[m]
            #print("SCORE OF ABOVE MAP IS: ", self.evaluate_map(unwrapped[m]))
        
        #print("SHOWING THE OPTIMAL MAP:")
        #show_map(optimal_map)
        #print("SCORE OF ABOVE MAP IS: ", max_score)
        return optimal_map





    


        
class Compound_Lattice():
    def __init__(self, data):
        self.map_list = {} 
        self.optimal_map_list = {}
        self.picture  = Correlate.picture_pixel(data)
        self.picture.apply_association()
        self.uncertain = False
        self.buffer = 0
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
                else:
                    self.buffer += 1
                
    def find_power_anchor(self):
        number_samples = len(self.picture.index_pixels[0].data)
        pixels = []
        for pixel in self.picture.index_pixels:
            pixels.append([pixel.index, sum(pixel.data)/ number_samples])
            #print(pixel.index, sum(pixel.data)/ number_samples)
        sorted_pixels = sorted(pixels, key = lambda x:x[1][0], reverse = True)
        #print(sorted_pixels[0])
        #print(sorted_pixels[1])
        #print(sorted_pixels[2])
        self.power_anchor_list = sorted_pixels


    def bounded_align_anchor(self, anchor_map_index):
        bounds = [0,0,1,1]
        map_in_bounds = {} ; restricted_map = {}
        for row_indices in range(bounds[0], bounds[2] + 1):
            for col_indices in range(bounds[1], bounds[3] + 1):
                map_in_bounds[self.map_list[anchor_map_index][(row_indices, col_indices)].index] = self.map_list[self.map_list[anchor_map_index][(row_indices, col_indices)].index]
                restricted_map[(row_indices, col_indices)] = self.map_list[anchor_map_index][(row_indices, col_indices)]
        restricted_indices = pull_indice_list(restricted_map)
        #show_map(restricted_map)
        oriented_maps = rotate_align(restricted_map, map_in_bounds, restricted_indices)
        #for x in oriented_maps:
        #    print('oriented',x)
        restricted_oriented_maps = {}

        for oriented_map in oriented_maps:
            restrict = {}
            for index in oriented_maps[oriented_map]:
                if(oriented_maps[oriented_map][index].index in restricted_indices):

                    restrict[index] = oriented_maps[oriented_map][index]
            restricted_oriented_maps[oriented_map] = restrict
        #print('number of restricted maps', len(restricted_oriented_maps))
        #for map in restricted_oriented_maps:
        #    print('\nMAP:',map)
        #    show_map(restricted_oriented_maps[map])
        centralized = central_align(self.map_list[anchor_map_index], restricted_oriented_maps, restricted_indices)
        position_lattice = Position_Lattice(centralized)
        optimal_map = position_lattice.optimize_map()
        return optimal_map

    def expand_anchor(self, anchor):
        # just trying to grow an anchor
        optimal_maps = {}
        for index in anchor:
            #print(index, anchor[index].index)
            optimal_maps[anchor[index].index] = self.bounded_align_anchor(anchor[index].index)

        #print("SHOWING OPTIMAL MAPS")
        indice_set = []
        for map in optimal_maps:
            #print('\nMAP:',map)
            for x in pull_indice_list(optimal_maps[map]):
                indice_set.append(x)
            #show_map(optimal_maps[map])
        indice_set = list(set(indice_set))
        oriented_maps = rotate_align(list(optimal_maps.values())[0], optimal_maps, indice_set)
        #print("SHOWING ORIENTED MAPS")
        #for m in oriented_maps:
        #    show_map(oriented_maps[m])

        centralized = central_align(list(oriented_maps.values())[0], oriented_maps, indice_set)

        #print("SHOWING CENTRALIZED")
        #for m in centralized:
        #    show_map(centralized[m])

        position_lattice = Position_Lattice(centralized)
        optimal_map = position_lattice.optimize_map()
        return optimal_map

    def double_anchor(self, index):
        start = time()
        double_expanded_anchor = self.expand_anchor(self.bounded_align_anchor(index))
        #print("FINISHED AN INDEX IN ", time() - start)
        return double_expanded_anchor

    def double_expand_all(self):
        self.double_expanded = {}
        print("STARTING:") ; start = time() ; finished = 0
        for map in self.map_list:
            
            try:
                
                self.double_expanded[map] = self.double_anchor(map)
                #print(map)
                finished += 1
            except:
                pass
        print('total maps = ', len(self.map_list), '/ competed : ', finished)
        print("estimated completion: ", 0.02*len(self.map_list))
        print("actual completion:", time() - start)
    
    def expand_all(self):
        self.expanded = {}
        print("STARTING:") ; start = time() ; finished = 0
        for map in self.map_list:
            
            try:
                
                self.expanded[map] = self.bounded_align_anchor(map)
                #print(map)
                finished += 1
            except:
                pass
        print('total maps = ', len(self.map_list), '/ competed : ', finished)
        print("estimated completion: ", 0.02*len(self.map_list))
        print("actual completion:", time() - start)
        
class Overlay():
    def __init__(self, Compound_Lattice_instance):
        self.frames = {}
        self.power_order = []
        self.power_hash = {}
        self.completed = {}
        try:
            self.frames = Compound_Lattice_instance.double_expanded
            self.power_order = Compound_Lattice_instance.power_anchor_list
        except:
            
            Compound_Lattice_instance.find_power_anchor()
            Compound_Lattice_instance.double_expand_all()
            self.frames = Compound_Lattice_instance.double_expanded
            self.power_order = Compound_Lattice_instance.power_anchor_list
        for node in self.power_order:
            self.power_hash[node[0]] = node[1]

        self.Master = {}
        
    
    def update_master_indices(self):
        self.Master_indices = {}
        for index in self.Master:
            for element in self.Master[index]:
                self.Master_indices[element[0]] = True
        

    def place_frame(self, frame, center, power):
        if(center == self.completed):
            raise ValueError("FUCK YOU IM ALREADY HERE", center)

        for index in frame:
            print(index, frame[index].index, center, power, coordinate_distance(frame[index].index, center))
            if(index not in self.Master):
                self.Master[index] = []
            distance = max(coordinate_distance(frame[index].index, center), 0.25)
            self.Master[index].append((frame[index].index, power/distance))
        self.completed[center] = True

    def align_to_frame(self, new_frame):
        '''
        Process:
        DONE 1. find every frame in completed that has an index in the new_frame : corresponding_frames
        2. run rotate align for every alignment against every frame in corresponding_frames and keep the maximally aligned option globally
        3. run central align for every suggested alignment against every frame corresponding_frames and keep the maximally aligned option globally
        4. insert the frame? 
        '''
        corresponding_frames = []
        print("ALIGNING TO FRAME", new_frame)
        frame_id = new_frame[0] ; frame_power = new_frame[1]
        print("BUILDING CORRESPONDING FRAMES")
        for frame in self.frames[frame_id]:
            print('frame:', self.frames[frame_id][frame].index)
            if(self.frames[frame_id][frame].index in self.Master_indices):
                print("ADDING", self.frames[frame_id][frame].index, 'to corresponding frames')
                corresponding_frames.append(self.frames[frame_id][frame].index)
        


        pass
    def Generate_Anchor(self):
        find_first_power_anchor = 0
        while(self.power_order[find_first_power_anchor][0] not in self.frames):
            find_first_power_anchor += 1

        
        print('Found Anchor in frames: ', self.power_order[find_first_power_anchor][0])
        anchor = self.frames[self.power_order[find_first_power_anchor][0]]
        self.place_frame(anchor, self.power_order[find_first_power_anchor][0], self.power_order[find_first_power_anchor][1])
        self.update_master_indices()
        self.center = self.power_order[find_first_power_anchor][0]

    def Expand_Master(self):
        '''
        DONE 1. find every indice in master that is not in completed and add it to the queue. 
        DONE 2. find every indice with a certain number of indices in master and add it to the queue.
        DONE 3. order them for insertion on distance from the center node. with closer being inserted first, then the number of indices in the graph in master. and the first group before the second.
        4. pass them to align_to_frame and then pass that output to place_frame to be inserted into master
        4. return the number of nodes completed, based on the difference in the length of self.completed at the start and after
        '''
        def sort_insertion_queue(queue):
            '''

            1. separate by distance first
            2. sort by number of indices in master
            3. recombine and return
            '''
            
            def elements_in_master(map_index):
                number_of_elements = 0
                for frame_element in self.frames[map_index]:
                    #print('frame element', frame_element, self.frames[map_index][frame_element].index)
                    if(self.frames[map_index][frame_element].index in self.Master_indices):
                        number_of_elements += 1
                #print('number of elements:', number_of_elements)
                return number_of_elements

            new_queue = []
            distance_classes = {}
            for element in queue:
                #print('ELEMENT TO BE INSERTED',element)
                distance = coordinate_distance(element[0], self.center)
                if(distance in distance_classes):
                    distance_classes[distance].append((element[0], elements_in_master(element[0])))
                else:
                    distance_classes[distance] = [(element[0], elements_in_master(element[0]))]
            sorted_distance_classes = []
            for distance_class in distance_classes:
                sorted_distance_classes.append((distance_class, distance_classes[distance_class]))
            sorted_distance_classes = sorted(sorted_distance_classes, key = lambda x:x[0])
            for distance_class in sorted_distance_classes:
                #print('distance class', distance_class[0])
                presence_sorted_distance_class = sorted(distance_class[1], key = lambda x: x[1] , reverse=True)
                for element in presence_sorted_distance_class:
                    #print('appending ', element,' to queue')
                    new_queue.append((element[0], self.power_hash[element[0]]))
            

            return new_queue

        def collect_insertion_queues():

            first_round_insertion_queue = []
            for map_index in self.Master:
                #print('\n\nMap Index:',map_index)
                for map_power in self.Master[map_index]:
                    if(map_power[0] not in self.completed):
                        #print('\tMap value:',map_power)
                        first_round_insertion_queue.append(map_power)
            
            #print("INDICEs IN MASter")
            #for x in self.Master_indices:
            #   print(x)
            second_round_insertion_queue = []
            for map_index in self.frames:
                map_contained = 0
                if(map_index not in self.completed and map_index not in self.Master_indices):

                    for index in self.frames[map_index]:
                        # if an index in the frame is 
                        if(self.frames[map_index][index].index in self.Master_indices):
                            map_contained += 1
                            if(map_contained == 3):
                                second_round_insertion_queue.append((map_index, self.power_hash[map_index]))
                                #print('Inserted',map_index,'into second round insertion queue')
                        
            #print("Sorting Queues")
            first_round_insertion_queue = sort_insertion_queue(first_round_insertion_queue)
            second_round_insertion_queue = sort_insertion_queue(second_round_insertion_queue)
            queue = []
            for element in first_round_insertion_queue:
                #print('first_round', element)
                queue.append(element)
            for element in second_round_insertion_queue:
                #print('second_round', element)
                queue.append(element)
            return queue

        queue = collect_insertion_queues()
        print("CHECKING FUNCITON RESULT")
    
        self.align_to_frame(queue[0])
        

        
    
    def Build_Overlay(self):
        '''
        1. run the Generate_Anchor Function
        2. Run Expand_Master until the it returns 0 or completed is the size of frames
        '''
        pass

    def Reduce_Overlay(self):
        '''
        1. For every indice in a master, check if there are copies of the same index.
        2. for every copy found add its contributing power together into a new master
        3. return the reduced copy of master
        '''
        pass
    def Optimize_Overlay(self):
        '''
        Dont need to do this, but if it seems like a good idea after completing the others:
        See if scaling the powers geometrically results in a better image. 
        '''
        pass

        
   
def working_test_1():
    # test the bounded align anchor and the optimize map
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='mnist', size = 4000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    test = Compound_Lattice(test_data)
    for map in test.map_list:
        print(map)
    print("BUFFER", test.buffer)
    test.bounded_align_anchor((14,15) )

def working_test_2():
    # test the anchor expansion
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='mnist', size = 4000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    test = Compound_Lattice(test_data)
    start = time()
    t1 = test.bounded_align_anchor((15,13))
    print("DONE T1 at :", time() - start)
    show_map(t1)
    t2 = test.expand_anchor(t1)
    print("DONE T2 at :", time() - start)
    show_map(t2)
    print("\n\nDOING 16,13")
    t1 = test.bounded_align_anchor((16,13))
    print("DONE T1 at :", time() - start)
    show_map(t1)
    t2 = test.expand_anchor(t1)
    print("DONE T2 at :", time() - start)
    show_map(t2)

def working_test_3():
    # test double expand all
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='mnist', size = 4000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    test = Compound_Lattice(test_data)
    test.find_power_anchor()
    test.double_expand_all()
    Overlay_test = Overlay(test)

def working_test_4():
    # test saving of data needed to generate Overlay
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='mnist', size = 4000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    test = Compound_Lattice(test_data)
    test.find_power_anchor()
    test.double_expand_all()
    Overlay_test = Overlay(test)
    outfile = open('Overlay_lattice_feed.obj','wb')
    pickle.dump(test,outfile)

def working_test_5():
    print("Loading the Overlay:")
    infile = open('Overlay_lattice_feed.obj','rb')
    Overlay_food = pickle.load(infile)
    Overlay_test = Overlay(Overlay_food)
    Overlay_test.Generate_Anchor()
    Overlay_test.Expand_Master()
    show_map(Overlay_test.frames[Overlay_test.power_order[0][0]])
#working_test_4()
#working_test_5()