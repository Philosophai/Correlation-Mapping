
import Gather
import Encrypt
from time import time
import Correlate
import pickle
import Merge2
import numpy as np
import matplotlib.pyplot as plt
import Overlay


'''
TODO:
1. BUILD MERGE PROTOCOL-
    play around with idea where conflicting nodes aren't attempted to be solved and are instead just assigned to be the average 


'''
class node:
    def __init__(self, index, index_pixel, map_index, up = None, down = None, right = None, left = None):
        self.index = index ; self.map_index = map_index
        self.up = up ; self.down = down ; self.right = right ; self.left = left
        self.vh = index_pixel.vh_association_group
        self.diag = index_pixel.diag_association_group
        self.power = index_pixel.power


    def has_connections_available(self):

        if(self.up != None and self.down != None and self.left != None and self.right != None):
            #print("NO CONNECTIONS AVAILABLE")
            return False
        #print("CONNECTIONS AVAILABLE")
        return True
    def return_available_positions(self):
        locations = []
        if(self.up == None): 
            locations.append((1 + self.map_index[0], self.map_index[1]))
            #print('up')
        if(self.down == None): 
            locations.append((self.map_index[0] - 1, self.map_index[1]))
            #print('down')
        if(self.left == None): 
            locations.append((self.map_index[0], self.map_index[1] - 1))
            #print('left')
        if(self.right == None): 
            locations.append((self.map_index[0], self.map_index[1] + 1))
            #print("right")
        
        return locations

    def find_available_connections(self):
        # this makes no fucking sense but it works...
        open = []
        if(type(self.up) ==  type(None)): open.append('up')
        if(type(self.down) ==  type(None)): open.append('down')
        if(type(self.right) ==  type(None)): open.append('right')
        if(type(self.left) ==  type(None)): open.append('left')
        return open

class lattice:
    
    def __init__(self, picture_pixel, anchor_index, pre_build = False):
        self.anchor_index = node(anchor_index, picture_pixel.index_pixels_hash[anchor_index], (0,0))
        if(not pre_build):
            self.anchor_index.right = node(self.anchor_index.vh[0][1],picture_pixel.index_pixels_hash[self.anchor_index.vh[0][1]],(0,1), left = self.anchor_index)
            self.placement_list = [self.anchor_index, self.anchor_index.right]
            self.placement_hash = {self.anchor_index.index:self.anchor_index , self.anchor_index.right.index : self.anchor_index.right}
            self.map_hash = {self.anchor_index.map_index: self.anchor_index , self.anchor_index.right.map_index : self.anchor_index.right}
        else:
            self.placement_list = [self.anchor_index]
            self.placement_hash = {self.anchor_index.index:self.anchor_index }
            self.map_hash = {self.anchor_index.map_index: self.anchor_index }   
        self.merge_count = {}        
        self.picture = picture_pixel
        self.hash = picture_pixel.index_pixels_hash
        self.uncertain = False
        for node_index in self.hash:
            if(self.hash[node_index].vh_association_group[2][0] == 0.0):
                self.uncertain = True
                break
    def prebuild_lattice(self, map_set):
        for mapping in map_set:
            self.place_by_map_index(mapping[0], mapping[1])
    def integrity_test(self):
        score = 0
        for pixel in self.placement_hash:
            up_right_down_left = [self.placement_hash[pixel].up,self.placement_hash[pixel].right,self.placement_hash[pixel].down,self.placement_hash[pixel].left]
            
            for adjacent in up_right_down_left:
                present = True
                if(type(adjacent) != type(None)):
                    present = False
                    for vh_node in self.placement_hash[pixel].vh:
                        if(adjacent.index == vh_node[1]):
                            score += vh_node[0]
                            present = True
                if(not present ):
                    score -= 1
        return score


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

    def place_by_map_index(self, to_be_placed_index, map_index_target):
        if(map_index_target in self.map_hash):
            raise ValueError ('MAP INDEX ALREADY IN USE')
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
        #print("DISPLAYING LATTICE\n")
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

    def find_best_expansion(self):
        '''
        Goal:   return the node that best fits into the lattice, based on all current nodes
                and nodes that could be expanded into in the future.

        Process:
        1.  find all possible locations that are VH associated with the lattice ie. no diagonal corners.
        2.  for each of these locations find all 
        '''
        def build_primary_and_secondary_support(map_index):
            def find_map_index_of_support(secondary, center_index):
                locations = secondary.return_available_positions()
                #print('LOCAtIONA MARK PASSed')
                for l in locations:
                    if(abs(l[0] - center_index[0]) + abs(l[1] - center_index[1]) == 1 ):
                        #print('Locations of ', secondary.index,' support is: ', l)
                        return l
            #print("BUILDING SUPPORT")
            primary_support_group = []
            secondary_support_group = []
            for r in range(-1,2):
                for c in range(-1, 2):
                    try:
                        if((r == 0 and c != 0 ) or (r != 0 and c == 0)):
                            primary_support_group.append(self.map_hash[(map_index[0] + r, map_index[1] + c)].index)
                        else:
                            #print("DIDDLY DO")
                            support_location = find_map_index_of_support(self.map_hash[(map_index[0] + r, map_index[1] + c)], map_index)
                            #print("STIIDLY DAY", support_location)
                            secondary_support_group.append([support_location, self.map_hash[(map_index[0] + r, map_index[1] + c)].index])
                            #print("YEAH DEE DEE BIDDLY BAY")
                        
                    except:
                        pass
            #print('Primary Group')
            #for r in primary_support_group:
            ##    print(r)
            #print("Secondary Group")
            #for r in secondary_support_group:
            #    print(r)
            return [primary_support_group, secondary_support_group]

        def find_possible_next_locations():
            locations = []
            for pixel in self.map_hash:
                #print(pixel, self.map_hash[pixel].index)
                temp = self.map_hash[pixel].return_available_positions()
                #print("temp", temp)
                for x in temp:
                    locations.append(x)
            #print("POSSIBLE LOCATIONS")
            return locations
        #locations = list(set(locations))
        def score_primary_suggestions(expansions_group):
            primary_sources = expansions_group[0]
            secondary_sources = expansions_group[1]
            primary_suggestions = {}
            secondary_suggestions = {}
            #print("Primary Suggestions = ")

            # format for primary suggestion = primary_suggestion[pixel index ie. (10, 10)] = [ number of primaries it is a member of ,  the multiplied rank among primaries, sum of score among primaries]
            for primary in primary_sources:
                #print('primary index:',primary)
                for node in range(len(self.hash[primary].vh_association_group)):
                    if(self.hash[primary].vh_association_group[node][1] not in self.placement_hash and self.hash[self.hash[primary].vh_association_group[node][1]].power > 0):
                        
                        #print("Not known node found ", self.hash[primary].vh_association_group[node][1],self.hash[primary].vh_association_group )
                        if(self.hash[primary].vh_association_group[node][1] not in primary_suggestions):
                            primary_suggestions[self.hash[primary].vh_association_group[node][1]] = [1, max(1,node), self.hash[primary].vh_association_group[node][0]]
                            #print("INSTANTIATING NODE:",primary_suggestions[self.hash[primary].vh_association_group[node][1]] )
                        else:
                            primary_suggestions[self.hash[primary].vh_association_group[node][1]][0] += 1
                            primary_suggestions[self.hash[primary].vh_association_group[node][1]][1] *=max(node, 1)
                            primary_suggestions[self.hash[primary].vh_association_group[node][1]][2] += self.hash[primary].vh_association_group[node][0]
            
            #print("PRINTING PRIMARY SUGGESTIONS")
            #for index in primary_suggestions:
            #    print('index:',index," :", primary_suggestions[index])

            # have the base nodes to be judged now need to gather the supporting nodes
            #print("PRINTING SECONDARY SOURCES", secondary_sources)
            for secondary in secondary_sources:
                #print("secondary_source", secondary)
                if(secondary[0] not in secondary_suggestions):
                    secondary_suggestions[secondary[0]] = {}
                vh = self.hash[secondary[1]].vh_association_group
                for index in range(len(vh)):
                    if(vh[index][1] in secondary_suggestions[secondary[0]]):
                        secondary_suggestions[secondary[0]][vh[index][1]][0] += 1
                        secondary_suggestions[secondary[0]][vh[index][1]][1] *= max(1, index)
                        secondary_suggestions[secondary[0]][vh[index][1]][1] += vh[index][0]
                    else:
                        secondary_suggestions[secondary[0]][vh[index][1]] = [1, max(1, index), vh[index][0]]
            
            
            #print("PRINTING SECONDARY SUGGESTIONS")
            
            #for map_index in secondary_suggestions:
            #    print('map_index of support', map_index)
            #    for index in secondary_suggestions[map_index]:
            #        print("index ", index,":" , secondary_suggestions[map_index][index])
            
            # Now I have the supporting indices, all thats left is to bring it all together into a coherent score
            #print("\n\nExpansion Group: ", expansions_group)
            #print("PLACED NODES", [ x.index for x in list(self.placement_hash.values())])
            #print("Combining into scores")
            for primary in primary_suggestions:
                #print('Primary: ',primary,": ", primary_suggestions[primary])
                new_best_score = primary_suggestions[primary]
                
                for secondary_map_index in secondary_suggestions:
            #        print('secondary index:', secondary_map_index)
                    secondary_source_position_counted = False
                    for index in secondary_suggestions[secondary_map_index]:
            #            print("index ", index,":" , secondary_suggestions[secondary_map_index][index])
                        if(index not in self.placement_hash and index != primary):
                            vh_group = self.hash[index].vh_association_group
                            for vh_node in range(len(vh_group)):
            #                    print("VH_NODE:",vh_group[vh_node], '#', vh_node)
                                if(vh_group[vh_node][1] == primary):
            #                        print("FOUND PRIMARY")
                                    if(not secondary_source_position_counted):
                                        new_best_score[0] += 1
                                        new_best_score[1] *= (max(vh_node, 1)*secondary_suggestions[secondary_map_index][index][1])
                                        new_best_score[2] += vh_group[vh_node][0] + secondary_suggestions[secondary_map_index][index][1]
            #                            print("FIRST UPDATE TO PRIMARY ",primary,": ", new_best_score)
                                        secondary_source_position_counted = True
                                    else:
            #                            print("CHECKING NEW SCORE")
                                        temp_score =  primary_suggestions[primary].copy()
                                        temp_score[0] += 1
                                        temp_score[1] *= ( max(vh_node, 1)*secondary_suggestions[secondary_map_index][index][1])
                                        temp_score[2] += vh_group[vh_node][0] + secondary_suggestions[secondary_map_index][index][1]
            #                            print("NEW BEST SCORE", new_best_score)
                                        if(temp_score[1] < new_best_score[1] or (temp_score[1] == new_best_score[1] and temp_score[2] < new_best_score[2])):
            #                                print("updating best score with help from ",vh_group[vh_node][1])
                                            new_best_score = temp_score
            #                            print("CHANGED NEW BEST SCORE", new_best_score)
                primary_suggestions[primary] = new_best_score
                #print("FINAL PRIMARY:",primary," score is -> ",primary_suggestions[primary] )
            
            max_1st_sort = 0
            for primary in primary_suggestions: 
                if(primary_suggestions[primary][0] > max_1st_sort): max_1st_sort = primary_suggestions[primary][0]

            min_2nd_sort = 10000000
            for primary in primary_suggestions: 
                if(primary_suggestions[primary][0] == max_1st_sort and min_2nd_sort > primary_suggestions[primary][1]): min_2nd_sort = primary_suggestions[primary][1]

            min_final_value = 100000 ; min_final_index = -1
            for primary in primary_suggestions: 
                if(primary_suggestions[primary][0] == max_1st_sort and min_2nd_sort == primary_suggestions[primary][1] and min_final_value > primary_suggestions[primary][2]): 
                    min_final_value = primary_suggestions[primary][2] ; min_final_index = primary
                    #print("updating value", min_final_index)
                #print("PRIMARY SUGGESTIONS",primary,':', primary_suggestions[primary], 'max 1st:', max_1st_sort, 'min 2nd:', min_2nd_sort)
            
            #print("FINAL SHIT BOIIII: ", primary_suggestions[min_final_index], min_final_index )
            #self.display_self()
            if(min_final_index == -1):
                return []
            return [primary_suggestions[min_final_index], min_final_index]
                                        
                                        

                

                    

        locations = find_possible_next_locations()
        print("\nFOUND LOCATIONS : ", locations)
        expansion_groups = {}
        for map_index in locations:
            #print('map location:',map_index)
            expansion_groups[map_index] = build_primary_and_secondary_support(map_index)

        score_indice_position = []
        for map_index in expansion_groups:
            
            #print('\n\nASSESSING ',map_index)
            #self.display_self()
            score_indice = score_primary_suggestions(expansion_groups[map_index])
            if(len(score_indice) == 0):
                score_indice = [[0, 1000, 1000], -1]
            score_indice_position.append([score_indice[0], score_indice[1], map_index])
        
        print("GOING THROUGH SCORE INDICE POSITION")
        #self.display_self()
        for sip in score_indice_position:
            print("SCORE:",sip[0], '// INDEX:',sip[1],'// POSITION:',sip[2])

        '''
        SHIT SEEMS PRETTY VALID. NEED TO DO MORE TESTING AND BUILD RETURN FUNCTION FOR THIS BUT GOOD
        '''
        max_1st_sort = 0
        for primary in range(len(score_indice_position)): 
            #print("1st: ", score_indice_position[primary][0][0])
            if(score_indice_position[primary][0][0] > max_1st_sort): max_1st_sort = score_indice_position[primary][0][0]

        min_2nd_sort = 10000000
        for primary in range(len(score_indice_position)): 
            if(score_indice_position[primary][0][0] == max_1st_sort and min_2nd_sort > score_indice_position[primary][0][1]): min_2nd_sort = score_indice_position[primary][0][1]

        min_final_value = 100000 ; final_index = -1
        for primary in range(len(score_indice_position)): 
            if(score_indice_position[primary][0][0] == max_1st_sort and min_2nd_sort == score_indice_position[primary][0][1] and min_final_value > score_indice_position[primary][0][2]): 
                min_final_value = score_indice_position[primary][0][2] ; final_index = score_indice_position[primary]
            
        
        print("END RESULT OF find_best_expansion ",  final_index)
        self.display_self()
        print("DISPLAYED OVER\n")

        return final_index
            
        

class Emerge:
    def __init__(self, picture_pixel):
        def undiscovered_mutual_favorites(picture_pixel, proposed_partern , pixel):
            if(picture_pixel.index_pixels_hash[proposed_partern[1]].vh_association_group[0][1] == pixel and picture_pixel.index_pixels_hash[proposed_partern[1]].vh_association_group[0][1] not in self.completed and picture_pixel.index_pixels_hash[pixel].power > 0.05 ):
                return True
            return False
        self.lattices = {}
        self.completed = {}
        self.uncertain_nodes = {}
        self.expansion_set = {}
        for pixel in picture_pixel.index_pixels_hash:
            print(pixel, picture_pixel.index_pixels_hash[pixel].vh_association_group[2])
            if(picture_pixel.index_pixels_hash[pixel].vh_association_group[2][0] == 0):
                self.uncertain_nodes[pixel] = True
        blank = np.zeros((32,32))
        power_graph = []
        for pixel in picture_pixel.index_pixels_hash:
            #print('index',pixel)
            vh_pixel = picture_pixel.index_pixels_hash[pixel].vh_association_group[0]
            
            if(undiscovered_mutual_favorites(picture_pixel, vh_pixel, pixel)):
                
                self.lattices[pixel] = lattice(picture_pixel , pixel)
                #print("DISPLAYING ",pixel,vh_pixel[1],' #', len(self.lattices) , 'power:',picture_pixel.index_pixels_hash[pixel].power)
                #self.lattices[pixel].display_self()
                self.completed[pixel] = True
                self.completed[vh_pixel[1]] = True
                #blank[pixel[0]][pixel[1]] = 1
        for lattice_index in self.lattices:
            self.expansion_set[lattice_index] = [False, []]
                #power_graph.append(picture_pixel.index_pixels_hash[pixel].power)
        #print(power_graph[0])
        #power_graph = sorted(power_graph)
        #plt.imshow(blank)
        #plt.show()
        #plt.figure()
        #plt.plot(power_graph)
        #plt.show()

    def build_expansion_set(self):
        '''
        Find the best possible expansion of all anchors that have not already been expanded.

        for every lattice in self.lattices
        if(lattice already in self.expansion_set)
            skip
        else: ie. if a new expansion needs to be generated
            run find_best_expansion and set self.expansion_set[index] = best_expansion
        At this point I want to review the results
        '''
        sorted_expansion_set = []
        for lattice_index in self.lattices:
            if(self.expansion_set[lattice_index][0] == False):
                self.expansion_set[lattice_index][1] = self.lattices[lattice_index].find_best_expansion()
                self.expansion_set[lattice_index][0] = True
                sorted_expansion_set.append(self.expansion_set[lattice_index][1])
            else:
                sorted_expansion_set.append(self.expansion_set[lattice_index][1])
        
        for x in range(len(sorted_expansion_set)):
            print('expansion_set: ', x, sorted_expansion_set[x])
    
    def merge_two(self, index_alpha, index_beta):
        if(index_beta not in self.lattices[index_alpha].merge_count):
            self.lattices[index_alpha].merge_count[index_beta] = 1
        else: self.lattices[index_alpha].merge_count[index_beta] += 1
        
        if(index_alpha not in self.lattices[index_beta].merge_count):
            self.lattices[index_beta].merge_count[index_alpha] = 1
        else: self.lattices[index_beta].merge_count[index_alpha] += 1
        
        if(self.lattices[index_alpha].merge_count[index_beta] > 2 or self.lattices[index_beta].merge_count[index_alpha] > 2):
            anchor_map_hash = self.lattices[index_beta].map_hash
            incomer_map_hash = self.lattices[index_alpha].map_hash
            anchor_indice_list = Merge2.pull_indice_list(anchor_map_hash)
            print("ANCHOR MAP:")
            self.lattices[index_beta].display_self()
            print("\nINCOMING MAP:")
            self.lattices[index_alpha].display_self()
            oriented = Merge2.rotate_align(anchor_map_hash, {'first': incomer_map_hash}, anchor_indice_list)

            raise ValueError('REACHED THE POINT WHERE WE ACTUALLY NEED A MERGE')
        print('merge count: ',self.lattices[index_beta].merge_count[index_alpha])

    def grow_outliers_of_expansion_set(self):
        '''
        IDEA:
        FOR THIS SET GROW EVERY EXPANSION RESULT THAT HAVE THE MAXIMUM 1st AND 2nd VALUES.
        ei. [2, 2, 2.01], [2,2,1.04] but not [2,3,1.7]
        IN every 
        '''
        max_1st = 0
        min_2nd = 1000
        proposals_to_expand = []
        for expansion_proposal in self.expansion_set:
            if(self.expansion_set[expansion_proposal][1][0][0] > max_1st):
                max_1st = self.expansion_set[expansion_proposal][1][0][0]
                min_2nd = 1000
                proposals_to_expand = []
                
            if(self.expansion_set[expansion_proposal][1][0][1] < min_2nd and self.expansion_set[expansion_proposal][1][0][0] == max_1st):
                min_2nd = self.expansion_set[expansion_proposal][1][0][1]
                proposals_to_expand = []
                
            if(self.expansion_set[expansion_proposal][1][0][0] == max_1st and self.expansion_set[expansion_proposal][1][0][1] == min_2nd):
                proposals_to_expand.append((expansion_proposal, self.expansion_set[expansion_proposal]))
        print('printing proposals', max_1st, min_2nd, 'len:', len(proposals_to_expand))

        max_1st -= 1 ; min_3rd = 10 ; min_index = -1
        while(max_1st > 1):
            for expansion_proposal in self.expansion_set:
                if(self.expansion_set[expansion_proposal][1][0][0] == max_1st and self.expansion_set[expansion_proposal][1][0][2] < min_2nd):
                    min_3rd = self.expansion_set[expansion_proposal][1][0][2]
                    min_index = expansion_proposal
            max_1st -= 1
            proposals_to_expand.append((min_index, self.expansion_set[min_index]))
        for x in proposals_to_expand : 
            print('X',x)
            if(x[1][1][1] in self.completed):
                print("MERGE NECESSARY FOR ", x[0], 'trying to merge into ', x[1][1][1])
                self.lattices[x[0]].display_self()
                lattice_to_be_merged = -1
                for lattice in self.lattices:
                    for index in self.lattices[lattice].placement_hash:
                        if(index == x[1][1][1]):
                            print('LATTICE TO BE MERGED WITH: ', lattice)
                            self.lattices[lattice].display_self()
                            lattice_to_be_merged = lattice
                self.lattices[x[0]].place_by_map_index(x[1][1][1], x[1][1][2])
                self.merge_two(x[0], lattice)
                self.expansion_set[x[0]][0] = False
                self.completed[x[1][1][1]] = True

                #raise ValueError('havent done this yet.')
            else:
                print("\nADDING", x[1][1][1],'to', x[0])
                self.lattices[x[0]].display_self()
                self.lattices[x[0]].place_by_map_index(x[1][1][1], x[1][1][2])
                print("ADDED:")
                self.lattices[x[0]].display_self()
                self.expansion_set[x[0]][0] = False
                self.completed[x[1][1][1]] = True

        pass

        

def working_test():
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='mnist', size = 3000)
    picture_test = Correlate.picture_pixel(test_data)
    picture_test.apply_association()
    test = Emerge(picture_test)
    print("INTEGRITY TEST",test.lattices[(10,6)].integrity_test())
    start = time()
    test.build_expansion_set()
    first = time() - start
    test.grow_outliers_of_expansion_set()
    second = time() - first - start
    test.build_expansion_set()
    third = time() - second - first - start
    print("first expansion", first, 'build and set:', second,' second expansion', third)
    test.grow_outliers_of_expansion_set()
    test.build_expansion_set()
    test.grow_outliers_of_expansion_set()
    test.build_expansion_set()
    test.grow_outliers_of_expansion_set()
    test.build_expansion_set()
    test.grow_outliers_of_expansion_set()
    test.build_expansion_set()
    test.grow_outliers_of_expansion_set()
    test.build_expansion_set()
    test.grow_outliers_of_expansion_set()
    test.build_expansion_set()
    test.grow_outliers_of_expansion_set()
    test.build_expansion_set()
    test.grow_outliers_of_expansion_set()
    test.build_expansion_set()
    test.grow_outliers_of_expansion_set()
    test.build_expansion_set()
    test.grow_outliers_of_expansion_set()
    test.build_expansion_set()
    test.grow_outliers_of_expansion_set()
    test.build_expansion_set()
    test.grow_outliers_of_expansion_set()

working_test()