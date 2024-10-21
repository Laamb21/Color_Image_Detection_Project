# processing.py

import os
import cv2
import numpy as np
import csv
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font
import logging

from utils import extract_first_digit, extract_last_four_digits, is_valid_jpg, is_valid_tiff

# Configure logging
logger = logging.getLogger()
# Remove existing handlers to prevent duplicate logs if setup_logging is called multiple times
if not logger.handlers:
    logging.basicConfig(
        filename='processing_debug.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

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
    try:
        all_tiff_files = [
            f for f in os.listdir(input_dir_tiff)
            if f.lower().endswith(('.tif', '.tiff')) and is_valid_tiff(f)
        ]

        logger.info(f"Found {len(all_tiff_files)} valid TIFF files in '{input_dir_tiff}'.")

        for tiff in all_tiff_files:
            first_digit = extract_first_digit(tiff)
            last_four = extract_last_four_digits(tiff)
            if not first_digit or not last_four:
                logger.warning(f"Could not extract necessary digits from TIFF '{tiff}'. Skipping.")
                continue

            key = (first_digit, last_four)
            if key in tiff_mapping:
                tiff_mapping[key].append(tiff)
                logger.info(f"Appending to existing key {key}: {tiff}")
            else:
                tiff_mapping[key] = [tiff]
                logger.info(f"Mapping {key} to {tiff}")

    except Exception as e:
        logger.error(f"Error building TIFF mapping: {str(e)}")
        raise  # Re-raise exception to be handled by the caller

    return tiff_mapping

def calculate_gray_percentage(image_path):
    """
    Calculate the percentage of gray pixels in a grayscale image.
    Gray pixels are those with intensity values strictly between 0 and 255.

    Parameters:
        image_path (str): The file path to the image.

    Returns:
        float: The percentage of gray pixels, or None if the image couldn't be read.
    """
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            logger.error(f"Error reading image: {image_path}")
            return None

        total_pixels = image.size
        # Count pixels that are not 0 and not 255
        gray_pixels = np.count_nonzero((image > 0) & (image < 255))
        gray_percentage = (gray_pixels / total_pixels) * 100
        logger.debug(f"Image '{image_path}' has {gray_percentage:.2f}% gray pixels.")
        return gray_percentage
    except Exception as e:
        logger.error(f"Exception while calculating gray percentage for '{image_path}': {str(e)}")
        return None

def get_sort_key(first_digit, last_four_digits):
    """
    Generate a sort key based on first digit and last four digits.

    Parameters:
        first_digit (str): The first digit indicating front (1) or back (2).
        last_four_digits (str): The last four digits of the document number.

    Returns:
        tuple: (int_first_digit, int_last_four_digits)
    """
    try:
        if first_digit and first_digit.isdigit():
            first_digit_int = int(first_digit)
        else:
            first_digit_int = float('inf')  # Push to the end if invalid

        if last_four_digits and last_four_digits.isdigit():
            last_four_digits_int = int(last_four_digits)
        else:
            last_four_digits_int = float('inf')  # Push to the end if invalid

        return (first_digit_int, last_four_digits_int)
    except Exception as e:
        logger.error(f"Exception in get_sort_key with first_digit='{first_digit}', last_four_digits='{last_four_digits}': {str(e)}")
        return (float('inf'), float('inf'))

def process_documents(input_dir_jpg, input_dir_tiff, progress_queue, low_threshold, high_threshold):
    """
    Process all JPG and TIFF pairs in the input directories, decide which format to use,
    and prepare log entries based on the decision.
    Sorts the log entries first by first digit (1 then 2), and within each group by last four digits from least to greatest.
    Adds a count of "TIF (Intermediate)" selections.

    Parameters:
        input_dir_jpg (str): Directory containing JPG files.
        input_dir_tiff (str): Directory containing TIFF files.
        progress_queue (queue.Queue): Queue to communicate progress to the GUI.
        low_threshold (float): Low gray threshold percentage.
        high_threshold (float): High gray threshold percentage.
    """
    try:
        # Build TIFF mapping
        tiff_mapping = build_tiff_mapping(input_dir_tiff)
        if not tiff_mapping:
            error_message = "No valid TIFF files found in the selected directory."
            logger.error(error_message)
            progress_queue.put(("error", error_message))
            return

        # Collect all JPG files
        all_jpg_files = [
            f for f in os.listdir(input_dir_jpg)
            if f.lower().endswith(('.jpg', '.jpeg')) and is_valid_jpg(f)
        ]

        if not all_jpg_files:
            error_message = "No valid JPG files found in the selected directory."
            logger.error(error_message)
            progress_queue.put(("error", error_message))
            return

        # List to hold all log entries
        log_entries = []
        flagged_count = 0  # Initialize counter for flagged files

        total_files = len(all_jpg_files)
        processed_files = 0

        # Process each JPG file
        for jpg_file in all_jpg_files:
            # Notify the GUI of the current file
            progress_queue.put(("current_file", jpg_file))

            base_name, _ = os.path.splitext(jpg_file)  # Extract base name without extension
            first_digit = extract_first_digit(jpg_file)
            last_four = extract_last_four_digits(jpg_file)
            if not first_digit or not last_four:
                logger.warning(f"Could not extract necessary digits from JPG '{jpg_file}'. Skipping.")
                processed_files += 1
                progress_queue.put(("progress", processed_files, total_files))
                continue

            # Find corresponding TIFF(s)
            key = (first_digit, last_four)
            tiff_files = tiff_mapping.get(key)
            if not tiff_files:
                logger.warning(f"No corresponding TIFF found for JPG '{jpg_file}' with key {key}. Skipping.")
                processed_files += 1
                progress_queue.put(("progress", processed_files, total_files))
                continue

            jpg_path = os.path.join(input_dir_jpg, jpg_file)

            gray_pct = calculate_gray_percentage(jpg_path)
            if gray_pct is None:
                logger.error(f"Skipping {jpg_file} due to read error.")
                processed_files += 1
                progress_queue.put(("progress", processed_files, total_files))
                continue

            # Decision logic
            if gray_pct < low_threshold:
                selected_format = "TIFF"
                # Log all corresponding TIFF base names, separated by commas
                selected_documents = ', '.join([os.path.splitext(tiff)[0] for tiff in tiff_files])
                flagged = "No"
            elif gray_pct > high_threshold:
                selected_format = "JPG"
                # Log the JPG's base name
                selected_documents = base_name
                flagged = "No"
            else:
                selected_format = "TIF (Intermediate)"
                # Log the TIFF's base names
                selected_documents = ', '.join([os.path.splitext(tiff)[0] for tiff in tiff_files])
                flagged_count += 1  # Increment counter for flagged files
                flagged = "Yes"

            # Append the entry with sort key based on first and last four digits
            sort_key = get_sort_key(first_digit, last_four)
            log_entries.append((sort_key, selected_documents, f"{gray_pct:.2f}", selected_format, flagged))

            # Log the decision in debug log
            logger.info(f"Document: {selected_documents}, Gray_Percentage: {gray_pct:.2f}, Selected_Format: {selected_format}, Flagged: {flagged}")

            # Update progress
            processed_files += 1
            progress_queue.put(("progress", processed_files, total_files))

        # Sort the log entries based on the sort key (first digit, then last four digits)
        log_entries_sorted = sorted(log_entries, key=lambda x: x[0])

    except Exception as e:
        logger.error(f"An unexpected error occurred during processing: {str(e)}")
        progress_queue.put(("error", f"An unexpected error occurred: {str(e)}"))
        return

    # ---------------------------- Notify Completion with Log Data ---------------------------- #
    completion_message = "Processing complete."
    logger.info(completion_message)
    progress_queue.put(("complete", completion_message, flagged_count, log_entries_sorted))

