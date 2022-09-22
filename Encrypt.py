from random import random, sample
from telnetlib import GA
import numpy as np
import Gather
from Gather import cifar10_name_hash

def build_random_arrangement_grid(picture):
    height = picture.shape[0]
    width = picture.shape[1]

    indices = []
    rows_shuffled = np.arange(0,height) ; np.random.shuffle(rows_shuffled)
    for row_index in rows_shuffled:
        cols_shuffled = np.arange(0,width) ; np.random.shuffle(cols_shuffled)
        random_row = [ (row_index, x) for x in cols_shuffled]
        for random_row_index in random_row: indices.append(random_row_index)
        
    indices = np.array(indices) ; np.random.shuffle(indices)

    random_arrangement_grid = []
    for x in range(height):
        row = []
        for y in range(width):
            row.append((indices[x*height + y][0], indices[x*height +y][1]))

        random_arrangement_grid.append(row)

    return random_arrangement_grid

def encrypt(picture, random_arrangement_grid):
    new_picture = np.zeros(picture.shape)
    height = picture.shape[0] ; width = picture.shape[1]
    for row in range(height):
        for col in range(width):
            rag_index = random_arrangement_grid[row][col]
            new_picture[rag_index[0]][rag_index[1]] = picture[row][col]
    return np.array(new_picture)

def decrypt(encrypted_picture, random_arrangement_grid):
    new_picture = np.zeros(encrypted_picture.shape)
    height = encrypted_picture.shape[0] ; width = encrypted_picture.shape[1]
    for row in range(height):
        for col in range(width):
            rag_index = random_arrangement_grid[row][col]
            new_picture[row][col] = encrypted_picture[rag_index[0]][rag_index[1]]
    return new_picture

def encrypt_batch(data, random_arrangement_grid):
    encrypted_data = []
    for picture in data:
        encrypted_data.append(encrypt(picture, random_arrangement_grid))
    return np.array(encrypted_data)

def decrypt_batch(data, random_arrangement_grid):
    decrypted_data = []
    for picture in data:
        decrypted_data.append(decrypt(picture, random_arrangement_grid))
    return np.array( decrypted_data )

def initialize_working_test():
    (cifar10_test_data, cifar10_test_labels), (cifar10_validation_data, cifar10_validation_labels) = Gather.download_and_normalize('cifar10', 10)
    (mnist_test_data, mnist_test_labels), (mnist_validation_data ,mnist_validation_labels) = Gather.download_and_normalize('mnist', 10)
    return mnist_test_data,mnist_test_labels, cifar10_test_data, cifar10_test_labels
def unit_test(mnist_test_data,mnist_test_labels, cifar10_test_data, cifar10_test_labels):
    random_sample_choice = np.random.randint(0, len(cifar10_test_data))
    sample_cifar10 = Gather.pull_sample(cifar10_test_data, cifar10_test_labels, random_sample_choice)
    sample_mnist = Gather.pull_sample(mnist_test_data, mnist_test_labels)

    rag_m = build_random_arrangement_grid(sample_mnist[0])
    rag_c = build_random_arrangement_grid(sample_cifar10[0])
    
    encrypted_mnist = encrypt(sample_cifar10[0], rag_c)
    decrypted_mnist = decrypt(encrypted_mnist, rag_c)

    batch_encrypted_cifar10 = encrypt_batch(cifar10_test_data, rag_c)
    batch_encrypt_cifar10_sample = Gather.pull_sample(batch_encrypted_cifar10, cifar10_test_labels, random_sample_choice)
    Gather.plot_sample(batch_encrypt_cifar10_sample)
    batch_decrypted_cifar10 = decrypt_batch(batch_encrypted_cifar10, rag_c)
    batch_decrypted_cifar10_sample = Gather.pull_sample(batch_decrypted_cifar10, cifar10_test_labels, random_sample_choice)
    Gather.plot_sample(batch_decrypted_cifar10_sample)
    Gather.plot_sample(sample_cifar10)
def run_unit_test():
    nist_test_data,mnist_test_labels, cifar10_test_data, cifar10_test_labels = initialize_working_test()
    unit_test(nist_test_data,mnist_test_labels, cifar10_test_data, cifar10_test_labels)






