
import tensorflow as tf
import time 
import copy
from tqdm import tqdm
import numpy as np
import math
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import pickle

def download_and_normalize_mnist(size = 5000):
    mnist = tf.keras.datasets.mnist
    (X, Y) , (VX, VY) = mnist.load_data()[:size]
    X = X / 255.0 ; VX =  VX / 255.0
    return ((X, Y) , (VX, VY))

def random_arrangement_grid(X_sample, seed = 0):
    np.random.seed = seed
    width_X = X_sample.__len__() ; height_X= X_sample[0].__len__()
    print("length X", width_X, 'height X', height_X)
    def one_dimensional_arrangement_generator(width_X= width_X, height_X = height_X):
        arrangement = np.zeros((width_X, height_X))
        for row in range(height_X):
            pass

def module_test():
    (X, Y) , (VX, VY) = download_and_normalize_mnist(100)

    #plt.imshow(X[0])
    #plt.title(Y[0])
    #plt.show()
    random_arrangement_grid(X[0])

def work_test():
    pass

    


