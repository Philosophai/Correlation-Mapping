from symbol import and_test
from tracemalloc import start
import math
import Gather
import Encrypt
import Correlate
import Map

def rotate_map(map, turns):
    def rotate(origin, point, angle):

        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return round(qx), round(qy)
    new_map = {}
    for index in map:
        print(index, 'turned', turns,' :', rotate((0,0) , index,  math.radians(90*turns)))
        new_map[rotate((0,0) , index,  math.radians(90*turns))] = map[index]
    return new_map

def show_map( map_example):
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
                row.append(str(map_example[(x,y)].index))
            except:
                row.append(str(None))
        grid.append(row)
    s = [[str(e) for e in row] for row in grid]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))
    return (row_space + 1, col_space + 1)

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

    def Merge(self):
        def pull_indice_list(map):
            indice_list = []
            for x in map:
                indice_list.append(map[x].index)
            return indice_list
        def central_align(anchor, ):
            pass
        import math


            
        start_anchor = self.power_anchor_list[0][0]
        start_map = self.map_list[start_anchor]
        start_index_list = pull_indice_list(start_map)
        print("ANCHOR", start_anchor)
        self.display_map(start_anchor)
        for x in start_map:
            print('x:',x,'starting_map[x]',start_map[x].index)
        included_maps = [] ; included_n = 0
        for map in start_index_list:
            included_n = 0
            for map_index in self.map_list[map]:
                if(self.map_list[map][map_index].index in start_index_list):
                    print('found one!', included_n)
                    included_n += 1
                if(included_n == 2 and map not in [x[0] for x in included_maps]):
                    included_maps.append([ map, self.map_list[map]])
        
        for map in included_maps:
            self.display_map(map[0])
        new_map = rotate_map(self.map_list[(14,15)], 1)
        show_map(new_map)

            
        





def working_test():
    ((test_data, test_labels) , (validation_data, validation_labels)) = Gather.download_and_normalize(dataset='mnist', size = 4000)
    random_arrangement_grid = Encrypt.build_random_arrangement_grid(Gather.pull_sample(test_data, test_labels, picture_only=True))
    encrypted_test_data = Encrypt.encrypt_batch(test_data, random_arrangement_grid)
    test = Compound_Lattice(test_data)
    test.display_map((13,13))
    test.find_power_anchor()
    test.Merge()
working_test()