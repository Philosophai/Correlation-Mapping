import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
from time import sleep
cifar10_name_hash = {0:'airplane', 1:'automobile',2:'bird', 3:'cat', 4:'deer',
                    5:'dog', 6:'frog', 7:'horse', 8:'ship', 9:'truck'}
def pull_sample(data, label, specific = False):
    random_choice = specific
    if(specific == False): random_choice = np.random.randint(0, data.shape[0] - 1)
    
    return [data[random_choice], int(label[random_choice])]
def plot_sample(sample, hash = False):
    plt.imshow(sample[0])
    if(hash): sample[1] = hash[sample[1]]
    plt.title(sample[1])
    plt.show()
    plt.figure()

def normalize_data(test_data, validation_data):
    test_data = test_data / float(np.max(test_data))
    validation_data = validation_data / float(np.max(validation_data))
    return (test_data, validation_data)

def download_cifar10(size = 5000):
    (test_data, test_labels) , (validation_data, validation_labels) = tf.keras.datasets.cifar10.load_data()
    return ((test_data[:size], test_labels[:size]) , (validation_data[:size], validation_labels[:size]))

def download_mnist(size = 5000):
    (test_data, test_labels) , (validation_data, validation_labels) = tf.keras.datasets.mnist.load_data()
    return ((test_data[:size], test_labels[:size]) , (validation_data[:size], validation_labels[:size]))

def download_and_normalize(dataset = 'cifar10', size = 5000):
    if (dataset == 'cifar10'): 
        (test_data, test_labels) , (validation_data, validation_labels) = download_cifar10(size)
    if (dataset == 'mnist'): 
        (test_data, test_labels) , (validation_data, validation_labels) = download_mnist(size)
        # Make equal to coloured
        test_data = np.expand_dims(test_data, 3) ; validation_data = np.expand_dims(validation_data, 3)
    try:
        (test_data, validation_data) = normalize_data(test_data, validation_data)
    except:
        raise ValueError('dataset not valid (cifar10, mnist) or size parameter too large.')
    return ((test_data, test_labels) , (validation_data, validation_labels))

def gather_unit_test():
    print('Running MNIST download_and_normalize test:')
    (mnist_test_data, mnist_test_labels), (mnist_validation_data ,mnist_validation_labels) = download_and_normalize('mnist', 10)
    print('Size 10:', len(mnist_test_data), '\nShape ( 10, 28, 28,1)', mnist_test_data.shape)
    print('Running pull_sample on MNIST')
    mnist_sample = pull_sample(mnist_test_data, mnist_test_labels)
    print('Running plot_sample on MNIST')
    plot_sample(mnist_sample)

    print("Running Cifar10 download_and_normalize:")
    (cifar10_test_data, cifar10_test_labels), (cifar10_validation_data, cifar10_validation_labels) = download_and_normalize('cifar10', 10)
    print('Size 10:', len(cifar10_test_data),'\nShape (10, 32, 32,3)', cifar10_test_data.shape)
    print('Running pull_sample on Cifar10')
    cifar10_sample = pull_sample(cifar10_test_data, cifar10_test_labels)
    print('Running plot_sample on Cifar10')
    plot_sample(cifar10_sample, cifar10_name_hash)
    



