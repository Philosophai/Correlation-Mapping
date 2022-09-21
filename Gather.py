import tensorflow as tf
import numpy as np
def set_seed(seed):
    np.seed = seed

def pull_sample(test_data):
    #r = np.random.randint()
    a = np.array.arange(0,20)
    

def normalize_data(test_data, validation_data):
    pass
def download_and_normalize_mnist(size = 5000):
    mnist = tf.keras.datasets.mnist
    (X, Y) , (VX, VY) = mnist.load_data()[:size]
    X = X / 255.0 ; VX =  VX / 255.0
    normalized_data = ((X, Y) , (VX, VY))
    return normalized_data