'''
Code to detect how many shades of gray are in grayscale JPGs
'''

#Import libraries 
import os
from PIL import Image
import numpy as np
import collections

#Define external hard drive path
external_drive_path = "D:/test_data/JPG"

# Load the images
image_paths = [os.path.join(external_drive_path, file) for file in os.listdir(external_drive_path) if file.endswith('.jpg')]

# Print the file names of the images found in the external drive
print("Image Files Found:")
for path in image_paths:
    print(os.path.basename(path))

print("\n" + "-"*50 + "\n")

gray_shades_count = []

# Process each image to count unique shades of gray
for path in image_paths:
    # Open image
    image = Image.open(path).convert("L")  # Convert to grayscale
    # Convert to numpy array
    image_array = np.array(image)
    # Get the unique gray levels and their counts
    unique_shades, counts = np.unique(image_array, return_counts=True)
    gray_shades_count.append(collections.OrderedDict(zip(unique_shades, counts)))

# Print the results
for idx, shades in enumerate(gray_shades_count):
    print(f"Image {idx + 1} - Unique Gray Shades and Counts:")
    for shade, count in shades.items():
        print(f"Gray Level {shade}: {count} occurrences")
    print("\n" + "-"*50 + "\n")
