import cv2
import os
import shutil
import numpy as np


def move_non_black_white_images(source_folder, target_folder, threshold=90):
    # Create the target folder if it doesn't exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Iterate through all files in the source folder
    for file_name in os.listdir(source_folder):
        if file_name.lower().endswith(".jpg") or file_name.lower().endswith(".jpeg"):
            # Full path to the image
            file_path = os.path.join(source_folder, file_name)

            # Load the image
            image = cv2.imread(file_path)

            # Convert to grayscale
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Define thresholds for black and white pixels
            black_threshold = 30  # Pixel values below this are considered black
            white_threshold = 225  # Pixel values above this are considered white

            # Count black and white pixels
            black_pixels = np.sum(gray_image < black_threshold)
            white_pixels = np.sum(gray_image > white_threshold)
            total_pixels = gray_image.size

            # Calculate the percentage of black and white pixels
            black_white_percentage = ((black_pixels + white_pixels) / total_pixels) * 100

            # Check if the image contains NO black and white pixels
            no_black_white_pixels = black_pixels == 0 and white_pixels == 0

            # Move the image if it has no black/white pixels OR black/white content is below threshold
            if no_black_white_pixels or black_white_percentage < threshold:
                target_path = os.path.join(target_folder, file_name)
                shutil.move(file_path, target_path)
                print(f"Moved: {file_name}")

    print(
        f"All non-black/white images or those with less than {threshold}% black/white content have been moved to '{target_folder}'.")


# Example usage
source_folder = "/Users/kevinshieldsjr/Desktop/test_color/sample"  # Replace with your source folder path
target_folder = "/Users/kevinshieldsjr/Desktop/test_color/output"  # Replace with your target folder path
threshold = 90  # Percentage threshold for black and white content
move_non_black_white_images(source_folder, target_folder, threshold)