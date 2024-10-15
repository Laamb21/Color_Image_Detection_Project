'''
Test to determine threshold for choosing JPG or TIFF (grayscale vs. black and white)
Refactored to eliminate output directories and only use input directories and a log file.
'''

# Import libraries 
import os
import cv2
import numpy as np
from tqdm import tqdm
import csv
import logging

# Configuration
INPUT_DIR_JPG = "D:/test_data/JPG"      # Directory containing JPG files
INPUT_DIR_TIFF = "D:/test_data/TIFF"    # Directory containing TIFF files
LOG_FILE = 'selection_log.csv'          # CSV file to log decisions

# Thresholds for gray percentage
LOW_GRAY_THRESHOLD = 5      # Below this percentage, use TIFF
HIGH_GRAY_THRESHOLD = 20    # Above this percentage, use JPG

# Optional: Configure logging for detailed logs
logging.basicConfig(
    filename='processing_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def calculate_gray_percentage(image_path):
    """
    Calculate the percentage of gray pixels in a grayscale image.
    Gray pixels are those with intensity values strictly between 0 and 255.
    
    Parameters:
        image_path (str): The file path to the image.
    
    Returns:
        float: The percentage of gray pixels, or None if the image couldn't be read.
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        logging.error(f"Error reading image: {image_path}")
        return None
    
    total_pixels = image.size
    # Count pixels that are not 0 and not 255
    gray_pixels = np.count_nonzero((image > 0) & (image < 255))
    gray_percentage = (gray_pixels / total_pixels) * 100
    return gray_percentage

def extract_last_four_digits(filename):
    """
    Extract the last four numerical digits before the file extension.
    
    Parameters:
        filename (str): The filename to extract digits from.
    
    Returns:
        str or None: The last four digits as a string, or None if extraction fails.
    """
    base, _ = os.path.splitext(filename)
    digits = ''.join(filter(str.isdigit, base))
    if len(digits) < 4:
        return None
    return digits[-4:]

def is_valid_jpg(filename):
    """
    Check if the filename is a valid JPG based on the second character being '1'.
    
    Parameters:
        filename (str): The JPG filename to validate.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    base, _ = os.path.splitext(filename)
    if len(base) < 2 or not base[1].isdigit():
        return False
    return base[1] == '1'

def is_valid_tiff(filename):
    """
    Check if the filename is a valid TIFF based on the second character being '0'.
    
    Parameters:
        filename (str): The TIFF filename to validate.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    base, _ = os.path.splitext(filename)
    if len(base) < 2 or not base[1].isdigit():
        return False
    return base[1] == '0'

def build_tiff_mapping(input_dir_tiff):
    """
    Build a dictionary mapping the last four digits to a list of corresponding TIFF filenames.
    Only include TIFF files where the second character in the base name is '0'.
    
    Parameters:
        input_dir_tiff (str): Directory containing TIFF files.
    
    Returns:
        dict: Mapping of last_four_digits (str) to list of TIFF filenames (list).
    """
    tiff_mapping = {}
    all_tiff_files = [
        f for f in os.listdir(input_dir_tiff)
        if f.lower().endswith(('.tif', '.tiff')) and is_valid_tiff(f)
    ]
    
    logging.info(f"Found {len(all_tiff_files)} valid TIFF files.")
    
    for tiff in all_tiff_files:
        last_four = extract_last_four_digits(tiff)
        if last_four:
            if last_four in tiff_mapping:
                tiff_mapping[last_four].append(tiff)
                logging.info(f"Appending to existing key: {last_four} -> {tiff}")
            else:
                tiff_mapping[last_four] = [tiff]
                logging.info(f"Mapping: {last_four} -> {tiff}")
        else:
            logging.warning(f"Could not extract last four digits from TIFF '{tiff}'. Skipping.")
    
    return tiff_mapping

def process_documents(input_dir_jpg, input_dir_tiff, log_file):
    """
    Process all JPG and TIFF pairs in the input directories, decide which format to use,
    and log the decisions without performing any file copying or moving.
    
    Parameters:
        input_dir_jpg (str): Directory containing JPG files.
        input_dir_tiff (str): Directory containing TIFF files.
        log_file (str): Path to the CSV log file.
    """
    # Build TIFF mapping
    tiff_mapping = build_tiff_mapping(input_dir_tiff)
    if not tiff_mapping:
        logging.error("No valid TIFF files found. Exiting.")
        print("No valid TIFF files found. Exiting.")
        return
    
    # Collect all JPG files
    all_jpg_files = [
        f for f in os.listdir(input_dir_jpg)
        if f.lower().endswith(('.jpg', '.jpeg')) and is_valid_jpg(f)
    ]

    if not all_jpg_files:
        logging.error("No valid JPG files found. Exiting.")
        print("No valid JPG files found. Exiting.")
        return

    # Prepare log file 
    with open(log_file, mode='w', newline='') as log_csv:
        log_writer = csv.writer(log_csv)
        log_writer.writerow(['Document', 'Gray_Percentage', 'Selected_Format'])

        for jpg_file in tqdm(all_jpg_files, desc="Processing Documents"):
            last_four = extract_last_four_digits(jpg_file)
            if not last_four:
                logging.warning(f"Could not extract last four digits from JPG '{jpg_file}'. Skipping.")
                continue

            # Find corresponding TIFF(s)
            tiff_files = tiff_mapping.get(last_four)
            if not tiff_files:
                logging.warning(f"No corresponding TIFF found for JPG '{jpg_file}' with last four digits '{last_four}'. Skipping.")
                continue

            jpg_path = os.path.join(input_dir_jpg, jpg_file)

            gray_pct = calculate_gray_percentage(jpg_path)
            if gray_pct is None:
                logging.error(f"Skipping {jpg_file} due to read error.")
                continue

            # Decision logic
            if gray_pct < LOW_GRAY_THRESHOLD:
                selected_format = "TIFF"
            elif gray_pct > HIGH_GRAY_THRESHOLD:
                selected_format = "JPG"
            else:
                selected_format = "JPG (Intermediate)"

            # Log the decision
            log_writer.writerow([last_four, f"{gray_pct:.2f}", selected_format])
            logging.info(f"Document: {last_four}, Gray_Percentage: {gray_pct:.2f}, Selected_Format: {selected_format}")

    print(f"\nProcessing complete. Log saved to {log_file}")
    logging.info(f"Processing complete. Log saved to {log_file}")

if __name__ == "__main__":
    process_documents(INPUT_DIR_JPG, INPUT_DIR_TIFF, LOG_FILE)
