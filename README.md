# Correlation-Mapping
Correlation Mapping is the attempt to reorder a scrambled picture back into its ordered form with the sole use of Correlation Data.
This description is high level and ignores some algorithm details that help speed it up.

the encryption process:

given a picture, construct a transformation key that will assign each pixel to a random location on a np array of the same size.
given a dataset and a transformation key, encrypt the dataset.

The process:

First gather association data on the variance between each pixel to each other pixel. 
This is data that is not lost when undergoing the transformation, this is the key piece of data.

Then using this and observations of the relationships between pixels on a grid, I use a distributed tesselation algorithms to expand the 
number of pixels placed until the entire picture has been placed.

currently working on: 
Merging distributed tesselations together to solve conflicts intelligently.

Animations that show previous work can be found in the animations tab.
