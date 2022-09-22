import numpy as np
import Gather

def build_random_arrangement_grid(sample):
    height = sample.shape[0]
    width = sample.shape[1]
    depth = sample.shape[2]
    print(height, width, depth)

def initialize_working_test():
    cifar10 = Gather.download_and_normalize('cifar10', 10)
    mnist = Gather.download_and_normalize('mnist', 10)
    return mnist, cifar10
def working_test(mnist, cifar10):

    build_random_arrangement_grid

mnist, cifar10 = initialize_working_test()
working_test(mnist, cifar10)




