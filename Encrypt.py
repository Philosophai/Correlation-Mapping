from cgi import test
from random import random, sample
from telnetlib import GA
import numpy as np
import Gather
from Gather import cifar10_name_hash
np.random.seed = 1
def build_random_arrangement_grid(picture):
    height = picture.shape[0]
    width = picture.shape[1]

    randomized_indices = []
    rows_shuffled = np.arange(0,height) ; np.random.shuffle(rows_shuffled)
    for row_index in rows_shuffled:
        cols_shuffled = np.arange(0,width) ; np.random.shuffle(cols_shuffled)
        random_row = [ (row_index, x) for x in cols_shuffled]
        for random_row_index in random_row: randomized_indices.append(random_row_index)
        
    randomized_indices = np.array(randomized_indices) ; np.random.shuffle(randomized_indices)

    random_arrangement_grid = []
    for x in range(height):
        random_arrangement_grid_row = []
        for y in range(width):
            random_index = randomized_indices[x*height + y]
            random_arrangement_grid_row.append((random_index[0], random_index[1]))

        random_arrangement_grid.append(random_arrangement_grid_row)

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

def test_enc_dec():
    (cifar10_test_data, cifar10_test_labels), (cifar10_validation_data, cifar10_validation_labels) = Gather.download_and_normalize('cifar10', 10)
    (mnist_test_data, mnist_test_labels), (mnist_validation_data ,mnist_validation_labels) = Gather.download_and_normalize('mnist', 10)
    random_sample_choice = np.random.randint(0, len(cifar10_test_data))
    sample_cifar10 = Gather.pull_sample(cifar10_test_data, cifar10_test_labels, random_sample_choice)
    sample_mnist = Gather.pull_sample(mnist_test_data, mnist_test_labels)

    rag_m = build_random_arrangement_grid(sample_mnist[0])
    rag_c = build_random_arrangement_grid(sample_cifar10[0])
    
    encrypted_mnist = encrypt(sample_mnist[0], rag_m)
    decrypted_mnist = decrypt(encrypted_mnist, rag_m)
    difference = 0

    for x in range(len(decrypted_mnist)):
        for y in range(len(decrypted_mnist[0])):
            difference += decrypted_mnist[x][y] - sample_mnist[0][x][y]
    print('TOTAL DIFFERENCE: ', difference)
    enc_total = 0 ; dec_total = 0 ; norm_total = 0
    for x in range(len(decrypted_mnist)):
        for y in range(len(decrypted_mnist[0])): 
            enc_total += encrypted_mnist[x][y]
            dec_total += decrypted_mnist[x][y]
            norm_total += sample_mnist[0][x][y]

    print('total encrypted : ', enc_total,'\ntotal decrypted:',dec_total,'\ntotal normal:',norm_total)    
    
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






