'''
Test to determine threshold for choosing JPG or TIFF (grayscale vs. black and white)
Refactored to eliminate output directories and only use input directories and a log file.
Logs the selected file's full name without extension in selection_log.tsv based on the decision.
Accounts for front (1) and back (2) captures of documents.
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
INPUT_DIR_TIFF = "D:/test_data/TIF"    # Directory containing TIFF files
LOG_FILE = 'selection_log.tsv'          # TSV file to log decisions

# Thresholds for gray percentage
LOW_GRAY_THRESHOLD = 5      # Below this percentage, use TIFF
HIGH_GRAY_THRESHOLD = 20    # Above this percentage, use JPG

# Configure logging with rotating file handler to prevent log file from growing indefinitely
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = RotatingFileHandler('processing_debug.log', maxBytes=5*1024*1024, backupCount=2)  # 5MB per file, keep 2 backups
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

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

def extract_first_digit(filename):
    """
    Extract the first numerical digit of the filename before the extension.
    
    Parameters:
        filename (str): The filename to extract the first digit from.
    
    Returns:
        str or None: The first digit as a string, or None if extraction fails.
    """
    base, _ = os.path.splitext(filename)
    for char in base:
        if char.isdigit():
            return char
    return None

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
    Build a dictionary mapping (first_digit, last_four_digits) to corresponding TIFF filenames.
    Only include TIFF files where the second character in the base name is '0'.
    
    Parameters:
        input_dir_tiff (str): Directory containing TIFF files.
    
    Returns:
        dict: Mapping of (first_digit, last_four_digits) to list of TIFF filenames.
    """
    tiff_mapping = {}
    all_tiff_files = [
        f for f in os.listdir(input_dir_tiff)
        if f.lower().endswith(('.tif', '.tiff')) and is_valid_tiff(f)
    ]
    
    logging.info(f"Found {len(all_tiff_files)} valid TIFF files.")
    
    for tiff in all_tiff_files:
        first_digit = extract_first_digit(tiff)
        last_four = extract_last_four_digits(tiff)
        if not first_digit or not last_four:
            logging.warning(f"Could not extract necessary digits from TIFF '{tiff}'. Skipping.")
            continue
        
        key = (first_digit, last_four)
        if key in tiff_mapping:
            tiff_mapping[key].append(tiff)
            logging.info(f"Appending to existing key {key}: {tiff}")
        else:
            tiff_mapping[key] = [tiff]
            logging.info(f"Mapping {key} to {tiff}")
    
    return tiff_mapping

def process_documents(input_dir_jpg, input_dir_tiff, log_file):
    """
    Process all JPG and TIFF pairs in the input directories, decide which format to use,
    and log the selected file's base name without extension based on the decision.
    
    Parameters:
        input_dir_jpg (str): Directory containing JPG files.
        input_dir_tiff (str): Directory containing TIFF files.
        log_file (str): Path to the TSV log file.
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
        # Use single tab delimiter for TSV
        log_writer = csv.writer(log_csv, delimiter='\t')  # Tab delimiter
        log_writer.writerow(['Document', 'Gray_Percentage', 'Selected_Format'])  # Header

        for jpg_file in tqdm(all_jpg_files, desc="Processing Documents"):
            base_name, _ = os.path.splitext(jpg_file)  # Extract base name without extension
            first_digit = extract_first_digit(jpg_file)
            last_four = extract_last_four_digits(jpg_file)
            if not first_digit or not last_four:
                logging.warning(f"Could not extract necessary digits from JPG '{jpg_file}'. Skipping.")
                continue

            # Find corresponding TIFF(s)
            key = (first_digit, last_four)
            tiff_files = tiff_mapping.get(key)
            if not tiff_files:
                logging.warning(f"No corresponding TIFF found for JPG '{jpg_file}' with key {key}. Skipping.")
                continue

            jpg_path = os.path.join(input_dir_jpg, jpg_file)

            gray_pct = calculate_gray_percentage(jpg_path)
            if gray_pct is None:
                logging.error(f"Skipping {jpg_file} due to read error.")
                continue

            # Decision logic
            if gray_pct < LOW_GRAY_THRESHOLD:
                selected_format = "TIFF"
                # Log all corresponding TIFF base names, separated by commas
                selected_documents = ', '.join([os.path.splitext(tiff)[0] for tiff in tiff_files])
            elif gray_pct > HIGH_GRAY_THRESHOLD:
                selected_format = "JPG"
                # Log the JPG's base name
                selected_documents = base_name
            else:
                selected_format = "JPG (Intermediate)"
                # Log the JPG's base name
                selected_documents = base_name

            # Log the decision
            log_writer.writerow([selected_documents, f"{gray_pct:.2f}", selected_format])
            logging.info(f"Document: {selected_documents}, Gray_Percentage: {gray_pct:.2f}, Selected_Format: {selected_format}")

    print(f"\nProcessing complete. Log saved to {log_file}")
    logging.info(f"Processing complete. Log saved to {log_file}")

if __name__ == "__main__":
    process_documents(INPUT_DIR_JPG, INPUT_DIR_TIFF, LOG_FILE)
