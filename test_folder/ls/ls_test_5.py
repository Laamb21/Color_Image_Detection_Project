'''
Implementing approach defined in approach.txt
'''

#Import libraries
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


#Step 1: Load image
img = Image.open("C:/Users/liams/ArchScan_Capture_Project/color_image_detection/test_folder/ls/11000005.jpg")          #Define path for image 
img_rgb = np.array(img)     #Convert to NumPy array for easy processing


#Step 2:  Convert to Grayscale or Black and White 
img_gray = img.convert('L')      #Convert to grayscale
img_bw = img.convert('1')        #Convert to black-and-white (binary)


#Step 3: Color Quantization (using K-means)
#Reshape the image to (N, 3) where N is the number of pixels and 3 are the RGB values 
pixels = img_rgb.reshape(-1, 3)
 
#Perform K-means clustering to group colors into K clusters
kmeans = KMeans(n_clusters=10)      #Let's assume we want 10 dominant shades 
kmeans.fit(pixels)
labels = kmeans.labels_
centroids = kmeans.cluster_centers_


#Step 4: Count Shades in Grayscale 
img_gray_array = np.array(img_gray)
hist, bins = np.histogram(img_gray_array, bins=256, range=(0, 255))     
#'hist' contains the count of pixels for each grayscale intensity (shade)


#Step 5: Count shades of Black and White:
img_bw_array = np.array(img_bw)
black_count = np.sum(img_bw_array == 0)
white_count = np.sum(img_bw_array == 255)


#Step 6: Visualization (Example for Grayscale)
plt.hist(img_gray_array.flatten(), bins=256, range=(0, 255))
plt.title("Grayscale Image Shade Distribution")
plt.xlabel("Shade (0 - 255)")
plt.ylabel("Pixel Count")
plt.show()



