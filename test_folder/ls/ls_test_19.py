#Test file to determine if an image is color, grayscale, or black and white

import cv2
import numpy as np

def determine_image_type_opencv(image_path):
    """
    Determines if the image is color, grayscale, or black and white using OpenCV.

    Parameters:
    - image_path: str, path to the image file.

    Returns:
    - str: 'color', 'grayscale', or 'black and white'
    """
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Image not found or unable to read.")

    # Check number of channels
    if len(img.shape) == 3:
        # Check if all channels are the same
        b, g, r = cv2.split(img[:,:,:3])
        if np.array_equal(b, g) and np.array_equal(b, r):
            # It's grayscale, now check for black and white
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            unique_values = np.unique(gray)
            if set(unique_values).issubset({0, 255}):
                return "black and white"
            else:
                return "grayscale"
        else:
            return "color"
    elif len(img.shape) == 2:
        unique_values = np.unique(img)
        if set(unique_values).issubset({0, 255}):
            return "black and white"
        else:
            return "grayscale"
    else:
        return "unknown"

# Example usage:
image_path = "D:/image_test/PGCPS-LF-05966_Page_02.tif"
image_type = determine_image_type_opencv(image_path)
print(f"The image is {image_type}.")
