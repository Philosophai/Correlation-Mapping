import numpy as np

def random_arrangement_grid(X_sample, seed = 0):
    np.random.seed = seed
    width_X = X_sample.__len__() ; height_X= X_sample[0].__len__()
    print("length X", width_X, 'height X', height_X)
    def one_dimensional_arrangement_generator(width_X= width_X, height_X = height_X):
        arrangement = np.zeros((width_X, height_X))
        for row in range(height_X):
            pass

def work_test():
    pass

    


