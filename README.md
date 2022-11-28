# Correlation-Mapping
Correlation Mapping is an algorithm that takes in a set of encrypted pictures, and decrypts them based on the variance between pixels. 
It works for pictures that have a degree of detail and are have a normal appearance. ie. each pixel is associated with its neighbour before encryption.

If you want to see it yourself quickly- here is the colab file: https://colab.research.google.com/drive/1XSZ3qCSyv2i4gWrAI_QqbrysoTD1qEVB?usp=sharing

I completed this November 2022.

Files necessary for demo: Gather.py, Encrypt.py, Correlate.py, Map.py, Merge.py, Emerge.py : run Emerge.py for the demo.

the encryption process:

I build an arrangment grid that takes each pixel and assigns it a new randomly chosen location, each pixels location is independent from others in its row and column. 
Then to encrypt I pass a picture into this mapping.

The Association Process:

I find the variance of difference between every pixel.

This could be massively sped up by pruning which pixels are computed further. by picture 100 each pixel has a good idea of which pixels it is randomly associated with, it could reduce the size of its computation to a group of 100 quickly. This would massively save time and I will hopefully implement this soon, if you would like to go for it!

Tesselation:
Using this correlation and a given starting pixel, finds the pixel most associated and joins it. Continues this process in rings, using the overlapping associative properties of each pixel already placed and found in the ring to stabilize noisy association groups.
This process could be worked on to require less data, but is already pretty fast. Although I didn't spend much time speed optimizing.
Animations that show previous work can be found in the animations tab.

Note: there is a cropping effect and most decrypted pictures have a crop of around 2 pixels, this is because edge data has weaker correlation. 

Areas to improve:

1.) sparse data -> currently this does not work on mnist
2.) time optimizing correlation -> could massively speed this up from N_pixels * N_pixels (* data length ) to some form of N_pixels * log_N_pixels * data_length
3.) edge recovery
4.) extending libraries to accept larger input images
5.) Changing the correlation function to detect when it is done to use the minimal number of images / modifying the tesselation function to work with less.

This project is a preliminary step in a larger field of research. This takes in obfuscated data and feature engineers it to ordered form, I chose to start this work on images because it was the easiest to determine correctness on. But images are simply data, with the property that most pixels are strongly associated with eight other features, some are associated with five other features, and four are associated with three other features. 
If one could extend this idea to a dynamic space where each feature could be associated to any number of features, it could be a powerful feature engineering step to apply to a new type of convolutional neural network. 
One where each feature has its own convolutional kernel, I recognize this would negate some of the weight sharing benefits of traditional convolution but it would extend it past the space of gridworld. 

If you would like to chat about this project or any field of research related to this contact me at thompsonbrown@live.ca. I am also looking for work! If you are looking for a machine learning engineer / researcher I would love to hear from you. 
