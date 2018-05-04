# Import the libraries
import cv2
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np


# User defined functions
from scripts.cmask import *
from scripts.color16mask import *
from scripts.internal_calibration import *
from scripts.make_cluster_mask import *
from scripts.undistortImg import *
from scripts.showasImage import *


# Sample image
image_loc = './input/2016-03-10-12-16-04-wahrsis3.jpg'

im = cv2.imread(image_loc)
plt.figure(1)
plt.imshow(im[:,:,[2,1,0]])
plt.show()


# Undistorting the image
unImage = undistortCC(im)
plt.figure(2)
plt.imshow(unImage[:,:,[2,1,0]])
plt.savefig('./results/undistortedImage.pdf', format='pdf')
plt.show()


# Calculation of the coverage
im = unImage
(rows,cols,_)=im.shape
im_mask = np.ones((rows,cols))
(inp_mat) = colorc15mask(im,im_mask)
(th_image,coverage) = make_cluster_mask_default(inp_mat,im_mask)
print ('Coverage is ',coverage)


plt.figure(3)
plt.imshow(th_image, cmap = cm.bone)
plt.savefig('./results/binaryImage.pdf', format='pdf')
plt.show()