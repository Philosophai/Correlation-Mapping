import Gather
import Encrypt
from time import time
import pickle
import Merge2
import numpy as np
import matplotlib.pyplot as plt
import Overlay

class Emerge():
    def __init__(self, Compound_lattice_instance):
        '''
        One more layer. 
        1. take in the same input as Overlay
        2. Create a power order list
        3. go through the power order list and create clusters
        4. grow and combine clusters evenly until they present a picture
        '''
        self.raw_frames = Compound_lattice_instance.expand_all()
        self.power_order = [x[0] for x in Compound_lattice_instance.power_anchor_list]
        
        
