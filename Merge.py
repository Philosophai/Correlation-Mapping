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

def central_align(anchor_map, map_set, indice_list, score = False, emerge = False):
    #print("CENTRAL ALIGNMENT")
    #print(anchor_map) 
    shift_set = {}
    removing_indices = []
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
                            if((other_index[0] + difference[0],other_index[1] + difference[1]) in temp_new_map):
                                removing_indices.append((other_index[0] + difference[0],other_index[1] + difference[1]))
                            temp_new_map[(other_index[0] + difference[0],other_index[1] + difference[1])] = map_set[map_example][other_index]
                        for temp_index in temp_new_map:
                            try:
                                if(temp_new_map[temp_index].index == anchor_map[temp_index].index):
                                    similarity_value += 1
                            except:
                                pass
                        if(similarity_value > best_similarity_value):
                            new_map = temp_new_map ; best_similarity_value = similarity_value
        if(score):
            shift_set[map_example] = [new_map, best_similarity_value]
        else:
            shift_set[map_example] = new_map
        #print('\n\n\n')
    if(emerge):
        return shift_set, removing_indices
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

