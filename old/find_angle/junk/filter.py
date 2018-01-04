import numpy as np

from skimage.transform import (hough_line, hough_line_peaks,
                               probabilistic_hough_line)
from skimage.feature import canny
from skimage import data
from skimage.color import rgb2gray

from pylab import imread, imshow, gray, mean

import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd


img = plt.imread('maps/map.png')

print(img.shape)
print(img[10,20])

mask = img < 87

#img[mask] = 0

plt.imshow(img)
plt.show()