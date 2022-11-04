from audioop import avg
import Gather
import Encrypt
import Map
from time import time
import pickle
import Merge2
import numpy as np
import matplotlib.pyplot as plt


class Overlay():
    def __init__(self, Compound_Lattice_instance):
        self.frames = {}
        self.power_order = []
        self.power_hash = {}
        self.completed = {}
        self.reduced = False
        try:
            self.frames = Compound_Lattice_instance.double_expanded
            self.power_order = Compound_Lattice_instance.power_anchor_list
        except:
            
            Compound_Lattice_instance.find_power_anchor()
            Compound_Lattice_instance.double_expand_all()
            Compound_Lattice_instance.expand_all()
            self.frames = Compound_Lattice_instance.double_expanded
            self.power_order = Compound_Lattice_instance.power_anchor_list
        for node in self.power_order:
            self.power_hash[node[0]] = node[1]

        self.Master = {}
    def transform(self, picture):
        fitted_grid = [] ; min_row = 0 ; max_row = 0; min_col = 0 ; max_col = 0
        for index in self.Master:
            if(index[0] < min_row): min_row = index[0]
            if(index[1] < min_col): min_col = index[1]
            if(index[0] > max_row): max_row = index[0]
            if(index[1] > max_col): max_col = index[1]
        print('PICTURE SHAPE:',picture.shape,' min row:',min_row,' min_col:',min_col)
        print(picture.shape[2])
        print("size row:", max_row + abs(min_row), ' size col:', abs(min_col) + max_col)
        for row in range(max_row + abs(min_row)):
            for col in range(abs(min_col) + max_col):
                pass

    def representative_power(self, map_index, element_specified):
        '''
        for a map index in Master find the contributing percentage of a specific element to the index.
        '''
        total = 0; specified = 0
        for element in self.Master[map_index]:
            if(element_specified == element[0]):
                specified += element[1]
            total += element[1]
        if(total == 0): return 0
        return specified / total

    def update_master_indices(self):
        self.Master_indices = {}
        for index in self.Master:
            for element in self.Master[index]:
                self.Master_indices[element[0]] = True
        

    def place_frame(self, frame, center, power):
        if(center == self.completed):
            raise ValueError("FUCK YOU IM ALREADY HERE", center)

        for index in frame:
            #print(index, frame[index].index, center, power, Merge2.coordinate_distance(frame[index].index, center))
            if(index not in self.Master):
                self.Master[index] = []
            distance = max(Merge2.coordinate_distance(index, (0,0)), 0.1)
            
            self.Master[index].append((frame[index].index, power.sum()/distance))
            #print("POWER DISTANCE", power)
        self.completed[center] = True

    def align_to_frame(self, new_frame):
        '''
        Process:
        DONE 1. find every frame in completed that has an index in the new_frame : corresponding_frames
        2. run rotate align for every alignment against every frame in corresponding_frames and keep the maximally aligned option globally
        3. run central align for every suggested alignment against every frame corresponding_frames and keep the maximally aligned option globally
        4. insert the frame? 
        '''
        def rotate_align(new_frame):
            def rotation_score(self, map, center):
                
                score = 0
                for index in map:
                    #print(index, map[index].index)
                    for master_index in self.Master:
                        for master_element in self.Master[master_index]:
                            if(master_element[0] == map[index].index):
                                #print("FOUND MATCHING ELEMENT: ", master_element[0])
                                for row_shift in range(-1, 2):
                                    for col_shift in range(-1, 2):
                                        try:
                                            # if the specific adjacent index in the map is in the specified adjacent index of master
                                            if(map[(row_shift + index[0] , col_shift + index[1])].index in [x[0] for x in self.Master[(master_index[0] + row_shift, master_index[1] + col_shift)]]):

                                                score += self.representative_power((master_index[0] + row_shift, master_index[1] + col_shift), map[(row_shift + index[0] , col_shift + index[1])].index) * (1 / Merge2.coordinate_distance((0,0), (row_shift + index[0] , col_shift + index[1])))
                                                #print("UPDATED SCORE", self.representative_power((master_index[0] + row_shift, master_index[1] + col_shift), map[(row_shift + index[0] , col_shift + index[1])].index) * (1 / Merge2.coordinate_distance(center, (row_shift + index[0] , col_shift + index[1]))))
                                        except:
                                            
                                            #print("FUCKED SOMETHING UP")
                                            pass
                #print("FINAL SCORE?", score)
                return score

            frame_id = new_frame[0] 
            new_map = self.frames[frame_id]
            
            turn_90 = Merge2.rotate_map(new_map, 1)
            turn_180 = Merge2.rotate_map(new_map, 2)
            turn_270 = Merge2.rotate_map(new_map, 3)
            inverted_map = Merge2.vertically_invert_map(new_map)
            inverted_90 = Merge2.rotate_map(inverted_map, 1)
            inverted_180 = Merge2.rotate_map(inverted_map, 2)
            inverted_270 = Merge2.rotate_map(inverted_map, 3)
            #print("SHOWING MAP ORIGINAL")
            maps = [new_map, turn_90, turn_180, turn_270, inverted_map, inverted_90, inverted_180, inverted_270]
            max_score = 0 ; max_index = -1
            for map_list_index in range(len(maps)):
                #print("scoring", map_list_index)
                present_score = rotation_score(self, maps[map_list_index], frame_id)
                if(present_score > max_score):
                    max_score = present_score 
                    max_index = map_list_index
            #print("Best Map index: ", max_index)
            #Merge2.show_map(maps[max_index])
            return maps[max_index]
            
        def central_align(new_frame, new_map):
            def center_score(self, map, center, difference):
                
                score = 0
                for index in map:
                    try:
                        if(map[index].index in [ x[0] for x in self.Master[(index[0] + difference[0], index[1] + difference[1])]]):
                            
                            score += self.representative_power((index[0] + difference[0], index[1] + difference[1]), map[index].index) * Merge2.coordinate_distance((0,0) , index)
                    except:
                        
                        pass
                #print("FINAL SCORE:", score, difference)
                return score    

            frame_id = new_frame[0] ;
            possible_differences = []
            for frame_index in new_map:
                #print('index', frame_index,':', new_map[frame_index].index)
                for master_index in self.Master:
                    for master_element in self.Master[master_index]:
                        if(master_element[0] == new_map[frame_index].index):
                            difference =  (master_index[0] - frame_index[0], master_index[1] - frame_index[1])
                            if(difference not in possible_differences):
                                possible_differences.append(difference)
                                #print('difference:',difference)
                                #print('Master index:', master_index,' frames index:',frame_index)
            
            #print("POSSIBLE DIFFERENCES")
            max_score = -1 ; max_index = -1
            for diff in possible_differences:
                
                
                score = center_score(self, new_map, frame_id, diff)
                #print('SCORE', score, ':',diff)
                if(score > max_score):
                    max_score = score 
                    max_difference = diff
            #print("BEST ALIGNMENT OPTION: ", max_difference,' with score:', max_score)
            central_aligned_map = {}
            for index in new_map:
                central_aligned_map[(index[0] + max_difference[0], index[1] + max_difference[1])] = new_map[index]

            #keys_old = list(new_map.keys())
            #keys_new = list(central_aligned_map.keys())
            #for index in range(len(new_map)):
            #    print('old:', keys_old[index], 'aligned:', keys_new[index])
            return [central_aligned_map, max_score]

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
        '''
        start = time()
        rotate_aligned_map = rotate_align(new_frame)
        [central_aligned_map, score] = central_align(new_frame, rotate_aligned_map)
        #print('Total time to complete insertion', time() - start, 'with score', score)    
        return [central_aligned_map, score, new_frame[0], new_frame[1]]
     
    def Generate_Anchor(self, chosen_anchor = False):
        
        find_first_power_anchor = 0
        while(self.power_order[find_first_power_anchor][0] not in self.frames):
            find_first_power_anchor += 1

        
        #print('Found Anchor in frames: ', self.power_order[find_first_power_anchor][0])
        if(chosen_anchor):
            anchor = self.frames[chosen_anchor]
            self.place_frame(anchor, chosen_anchor, self.power_hash[chosen_anchor])
            self.center = chosen_anchor
        else:
            anchor = self.frames[self.power_order[find_first_power_anchor][0]]
            self.place_frame(anchor, self.power_order[find_first_power_anchor][0], self.power_order[find_first_power_anchor][1])
            self.center = self.power_order[find_first_power_anchor][0]
        self.update_master_indices()
    
    def judge_frame(self,frame_id):
        if(frame_id not in self.frames): return None
        frame_map = self.frames[frame_id]

        '''
        check how well a particular frame lines up with its neighbours to check its validity
        1. Grab every frame that has 2 or more indices in test_frame
        2. rotate_align and central_align then compare the score of the average against its score against itself
        '''
        frame_indices = Merge2.pull_indice_list(frame_map)
        included_frames = {}
        for frame in self.frames:
            if(frame != frame_id):
                index_match = 0
                #print('FRAME:',frame)
                for indice in self.frames[frame]:
                    #print(indice, self.frames[frame][indice].index)
                    if(self.frames[frame][indice].index in frame_indices):
                        #print(frame, "MATCH",self.frames[frame][indice].index)
                        index_match += 1
                        if(index_match == 3):
                            included_frames[frame] = self.frames[frame]
        #for x in included_frames:
            #print("included:",x)
        
        rotated = Merge2.rotate_align(frame_map, included_frames, frame_indices)
        centralized = Merge2.central_align(frame_map, rotated, frame_indices, True)
        self_score = list(Merge2.central_align(frame_map, {frame_id: frame_map}, frame_indices, True).values())[0][1]
        #print("Self Score:", self_score)
        #print('Other Scores')
        percentages = [] ; top = []
        for s in centralized:
            #print(s, centralized[s][1], centralized[s][1]/ self_score)
            percentages.append((s,centralized[s][1]/ self_score))
            if(centralized[s][1] == self_score):
                top.append(s)

            #percentages.append(centralized[s][1]/ self_score)
        # format = [ frame, average_percentage, 100% correlate list]
        return percentages, top
    def judge_all(self):
        percentages = []
        for frame in self.frames:
            temp_percentages, temp_top = self.judge_frame(frame)
            if(len(temp_percentages) > 0):
                #print(frame, temp_percentages)
                percentages.append((frame, sum([x[1] for x in temp_percentages])/len(temp_percentages), len(temp_percentages), temp_top))
            
        percentages = sorted(percentages, key = lambda x:x[1])
        return percentages

    def Priority_expansion(self, percentages):
        priority_expansion = [] ; in_list = {}
        for p in percentages:
            expansion_list = []
            for top_index in p[3]:
                if(top_index not in in_list):
                    expansion_list.append(top_index)
                    in_list[top_index] = True
            if(len(expansion_list) > 0):
                in_list[p[0]] = True
                priority_expansion.append(((p[0], expansion_list)))
        return priority_expansion
        

    def Expand_Master(self):
        '''
        DONE 1. find every indice in master that is not in completed and add it to the queue. 
        DONE 2. find every indice with a certain number of indices in master and add it to the queue.
        DONE 3. order them for insertion on distance from the center node. with closer being inserted first, then the number of indices in the graph in master. and the first group before the second.
        DONE 4. pass entire queue to align to frame to receive score, then insert on maximum score. adding inserted to completed
        DONE 5. repeat 4 until there is nothing left to expand

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
            
            for element in queue:
                #print("ELEMEsNT", element)
                if(element[0] in self.frames):
                    new_queue.append((element[0], elements_in_master(element[0])))
            #for x in new_queue:
                #print('NEW QUEUE', x)
            new_queue = sorted(new_queue, key = lambda x:x[1], reverse = True)
            for x in range(len(new_queue)):
                new_queue[x] = (new_queue[x][0], self.power_hash[new_queue[x][0]])
            '''
                #print('ELEMENT TO BE INSERTED',element)
                distance = Merge2.coordinate_distance(element[0], self.center)
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
                    print('appending ', element,' to queue')
                    new_queue.append((element, self.power_hash[element[0]]))
            
            '''
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
                if(element[0] not in [x[0] for x in queue]):queue.append(element)
                
            for element in second_round_insertion_queue:
                #print('second_round', element)
                if(element[0] not in [x[0] for x in queue]):queue.append(element)
            return queue

        queue = collect_insertion_queues()
        #print("Starting batch alignment")
        alignment_values = []
        start = time()
        for map in queue:
            alignment_values.append(self.align_to_frame(map))
        #print("GATHERED RESULTS")
        alignment_values = sorted(alignment_values, key = lambda x:x[1], reverse = True)
        #for x in range(len(alignment_values)):
            #print(queue[x][0], alignment_values[x][1])
            #Merge2.show_map(alignment_values[x][0])
        
        #print("INSERTING AND RE-ALIGNING MAPS")

        inserted = 0
        while(inserted < len(self.frames) and len(alignment_values) > 0):
            
            '''
            1. pop alignment values stack and insert
            2. realign every node into a new alignment_values 
            '''
            #for x in alignment_values:
                #print('alignment_values', inserted, x[2])
            # map center power
            self.place_frame(alignment_values[0][0], alignment_values[0][2], alignment_values[0][3])
            inserted += 1

            print("INSERTED",alignment_values[0][2],'\n\n')
            alignment_values = []
            #queue = collect_insertion_queues()
            for map in queue:
               
                if( map[0] not in self.completed):
                    alignment_values.append(self.align_to_frame(map))
            alignment_values = sorted(alignment_values, key = lambda x:x[1], reverse = True)
        #print('TIME TO COMPLETE', time() - start)

        #for index in self.Master:
            #print(index, self.Master[index])
        self.update_master_indices()
        return
        #self.align_to_frame(queue[0])
        
    def Build_Overlay(self):
        '''
        1. run the Generate_Anchor Function
        2. Run Expand_Master until the it returns 0 or completed is the size of frames
        '''
        pass

    def Reduce_Overlay(self):
        '''
        DDONE 1. For every indice in a master, check if there are copies of the same index.
        DONE 2. for every copy found add its contributing power together into a new master
        DONE 3. return the reduced copy of master, ready for projection
        '''
        reduced = {}
        for index in self.Master:
            reduced[index] = []
            #print("INDEX: ",index)
            index_set = {} ; index_sum = 0
            for element in self.Master[index]:
                if(element[0] not in index_set):
                    
                    index_set[element[0]] = element[1]
                else:
                    index_set[element[0]] += element[1]
                index_sum += element[1]

            for element in index_set:
                reduced[index].append((element, index_set[element]/ index_sum))
        # for r in reduced:
            #print(r, reduced[r])
        self.reduced = reduced
    
    def Project_Overlay(self, picture):
        '''
        DONE 1. build a zero - replica of the picture
        2. center the master to the frame
        3. update the values of the frame index by index
        
        '''
        if(self.reduced == False):
            self.Reduce_Overlay()
        blank = np.zeros((len(picture) + 15, len(picture[0])+15, len(picture[0][1])))
        copy = np.zeros((len(picture) + 3, len(picture[0]) + 3, len(picture[0][1])))
        mid_row = int((len(picture) + 3)/2) ; mid_col = int((len(picture[0]) + 3)/2)
        min_row = 0; min_col = 0; max_row = 0; max_col = 0
        for index in self.reduced:
            if(index[0] < min_row): min_row = index[0]
            if(index[1] < min_col): min_col = index[1]
            if(index[0] > max_row): max_row = index[0]
            if(index[1] > max_col): max_col = index[1]
        #print(min_row, min_col, max_row, max_col)
        #print("COM", ((min_row + max_row)/2, (min_col + max_col)/2))
        mid_row += int((min_row + max_row)/2) ; mid_col += int((min_col + max_col)/2)
        #print('mid_row', mid_row, 'mid_col',mid_col)
        for index in self.reduced:
            for element in self.reduced[index]:
                blank[mid_row + index[0]][mid_col + index[1]] += picture[element[0][0]][element[0][1]] * element[1]

        plt.imshow(blank)
        plt.show()
        plt.figure()
        plt.imshow(picture)
        plt.show()
        plt.figure()

    def Optimize_Overlay(self):
        '''
        Dont need to do this, but if it seems like a good idea after completing the others:
        See if scaling the powers geometrically results in a better image. 
        '''
        pass


def check_expanded(Overlay_test, center_index):
    if(Overlay_test.reduced == False):
        Overlay_test.Reduce_Overlay()
    reduced = Overlay_test.reduced
    most_right = 0 ; tot = 0
    for rot in range(0,8):
        if(rot >3):
            temp_reduced = Merge2.vertically_invert_map(Merge2.rotate_map(Overlay_test.reduced, rot - 4))
        else:
            temp_reduced = Merge2.rotate_map(Overlay_test.reduced, rot)
        
        right = 0 ; total = 0
        for x in temp_reduced:
            #print('\n\nmaster index:',x[0] + center_index[0], x[1] + center_index[1], temp_reduced[x])
            if((x[0] + center_index[0], x[1] + center_index[1]) == temp_reduced[x][0][0]): right += 1
            total += 1
        if(most_right < right): most_right = right ; tot = total

    print('\n\nright:', most_right, 'total', tot,' %:', most_right/tot)         

def working_test_4():
    # test saving of data needed to generate Overlay
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='cifar10', size = 2000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    full_data = []
    for x in test_data:
        full_data.append(x)
    for x in validation_data:
        full_data.append(x)
    full_data = np.array(full_data)
    start = time()
    test = Merge2.Compound_Lattice(full_data)
    print('Built test at', time() - start)
    test.find_power_anchor()
    print("Built Power Anchor", time() - start)
    test.double_expand_all()
    print("Double Expand All", time() - start)
    Overlay_test = Overlay(test)
    print("Built Overlay", time() - start)
    #outfile = open('Overlay_lattice_feed.obj','wb')
    #pickle.dump(test,outfile)
    inc_A, top_A = Overlay_test.judge_frame((15,14))
    inc_B = Overlay_test.judge_frame((7,14))
    inc_C = Overlay_test.judge_frame((12,14))
    Merge2.show_map(Overlay_test.frames[(12,14)])
    #print('Av A:', sum(inc_A)/len(inc_A),'Length B:',sum(inc_B)/len(inc_B), 'Length C:', sum(inc_C)/len(inc_C))
    for x in inc_A:
        print(x)
    for y in top_A:
        print('top',y)
    percentages = Overlay_test.judge_all()
    for p in percentages:
        print('\nINDEX + VALIDITY:',p)
        Merge2.show_map(Overlay_test.frames[p[0]])  
    priority = Overlay_test.Priority_expansion(percentages)
    blank = np.zeros((34,34,1)) ; animation = []
    for p in priority:
        print('center index', p[0])
        print(p)
        blank[p[0][0]][p[0][1]][0] = 1
        for t in p[1]:
            blank[t[0]][t[1]][0] = 0.3
        animation.append(blank.copy())
    Map.animate_image_matrix(animation, 'Distributed Anchor Generation CIFAR10', 10)

    #print("Loading the Overlay:")
    #infile = open('Overlay_lattice_feed.obj','rb')
    #Overlay_food = pickle.load(infile)
    #Overlay_test = Overlay(Overlay_food)
    #Overlay_test.Generate_Anchor()
    '''
    print("Generated Anchor", time() - start)
    Overlay_test.Expand_Master()
    print("EXPANDED 1", time() - start)
    Overlay_test.Expand_Master()
    print("EXPANDED 2", time() - start)
    Overlay_test.Expand_Master()
    print("EXPANDED 3", time() - start)
    Overlay_test.Expand_Master()
    print("EXPANDED 4", time() - start)
    Overlay_test.Expand_Master()
    print("EXPANDED 5", time() - start)
    Overlay_test.Expand_Master()
    print("EXPANDED 6", time() - start)
    Overlay_test.Expand_Master()
    print("EXPANDED 7", time() - start)
    Overlay_test.Expand_Master()
    print("EXPANDED 8", time() - start)
    Overlay_test.Expand_Master()
    print("EXPANDED 9", time() - start)
    Overlay_test.Expand_Master()
    print("EXPANDED 10", time() - start)

    Merge2.show_map(Overlay_test.frames[Overlay_test.power_order[0][0]])
    Overlay_test.Project_Overlay(test_data[0])
    '''
    print('LENGTH OF DATA:', len(full_data))
   

def working_test_5():
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='mnist', size = 10)
    print("Loading the Overlay:")
    infile = open('Overlay_lattice_feed.obj','rb')
    Overlay_food = pickle.load(infile)
    Overlay_test = Overlay(Overlay_food)
    start = time()
    
    Overlay_test.Generate_Anchor((18,15))

    Overlay_test.Expand_Master()
    #print("EXPANDED 1", time() - start)
    #Overlay_test.Expand_Master()
    #print("EXPANDED 2", time() - start)
    #Overlay_test.Expand_Master()
    #print("EXPANDED 3", time() - start)
    #Overlay_test.Expand_Master()
    #print("EXPANDED 4", time() - start)
    #print("Generated Anchor", time() - start)
    



    Merge2.show_map(Overlay_test.frames[Overlay_test.power_order[0][0]])
    
    reduced = Overlay_test.Reduce_Overlay() 
    reduced = Merge2.vertically_invert_map(Merge2.rotate_map(Overlay_test.reduced, 1))
    Merge2.show_map(Overlay_test.frames[(18,15)])
    right = 0 ; total = 0
    for x in reduced:
        print('\n\nmaster index:',x[0] + 18, x[1] + 15, reduced[x])
        if((x[0] + 18, x[1] + 15) == reduced[x][0][0]): right += 1
        total += 1
    print('\n\nright:', right, 'total', total,' %:', right/total)

    '''
    Correctness Test: 
     (14,15)
     Anchor = 1 ( 8/8 )
     Expand 1 = 0.923 ( 12/13)
     Expand 2 = 0.913 ( 21/23)
     Expand 3 = 0.805 (29/36)
     Expand 4 = 0.679 (38/56)
     (15,15)
     Anchor  = 0.888 ( 8/9)
     Expand 1 = 0.789 ( 30/38)
     Expand 2 = 0.63 (53/84)
     

    '''
    #for x in range(10):
    #    Overlay_test.Project_Overlay(test_data[x])
    
    
def working_test_6():
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='mnist', size = 10)
    print("Loading the Overlay:")
    infile = open('Overlay_lattice_feed.obj','rb')
    Overlay_food = pickle.load(infile)
    Overlay_test = Overlay(Overlay_food)
    for frame in Overlay_test.frames:
        print(frame)
        Merge2.show_map(Overlay_test.frames[frame])
    inc_A, top_A = Overlay_test.judge_frame((15,14))
    inc_B = Overlay_test.judge_frame((7,14))
    inc_C = Overlay_test.judge_frame((12,14))
    Merge2.show_map(Overlay_test.frames[(12,14)])
    #print('Av A:', sum(inc_A)/len(inc_A),'Length B:',sum(inc_B)/len(inc_B), 'Length C:', sum(inc_C)/len(inc_C))
    for x in inc_A:
        print(x)
    for y in top_A:
        print('top',y)
    percentages = Overlay_test.judge_all()
    for p in percentages:
        print('\nINDEX + VALIDITY:',p)
        Merge2.show_map(Overlay_test.frames[p[0]])  
    priority = Overlay_test.Priority_expansion(percentages)
    animation = []
    blank = np.zeros((28,28,1))
    for p in priority:
        print('center index', p[0])
        print(p)
        blank[p[0][0]][p[0][1]][0] = 1
        for t in p[1]:
            blank[t[0]][t[1]][0] = 0.3
        #plt.imshow(blank)
        #plt.title(label=str(p[0]))
        #plt.show()
        #plt.figure()
        animation.append(blank.copy())
    Map.animate_image_matrix(animation, 'Distributed Anchor Generation MNIST', 5)
    

    #Overlay_test.Generate_Anchor((12,15))
    #Overlay_test.Expand_Master()
    #reduced = Overlay_test.Reduce_Overlay() 
    #check_expanded(Overlay_test, (12,15))


#working_test_4()