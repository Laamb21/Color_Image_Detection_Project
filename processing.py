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

def get_sort_key(first_digit, last_four_digits):
    """
    Generate a sort key based on first digit and last four digits.
    
    Parameters:
        first_digit (str): The first digit indicating front (1) or back (2).
        last_four_digits (str): The last four digits of the document number.
    
    Returns:
        tuple: (int_first_digit, int_last_four_digits)
    """
    if first_digit and first_digit.isdigit():
        first_digit_int = int(first_digit)
    else:
        first_digit_int = float('inf')  # Push to the end if invalid
    
    if last_four_digits and last_four_digits.isdigit():
        last_four_digits_int = int(last_four_digits)
    else:
        last_four_digits_int = float('inf')  # Push to the end if invalid
    
    return (first_digit_int, last_four_digits_int)

def process_documents(input_dir_jpg, input_dir_tiff, log_file_tsv, log_file_xlsx, progress_queue, low_threshold, high_threshold):
    """
    Process all JPG and TIFF pairs in the input directories, decide which format to use,
    and log the selected file's base name without extension based on the decision.
    Sorts the log entries first by first digit (1 then 2), and within each group by last four digits from least to greatest.
    Adds a count of "JPG (Intermediate)" selections.
    
    Parameters:
        input_dir_jpg (str): Directory containing JPG files.
        input_dir_tiff (str): Directory containing TIFF files.
        log_file_tsv (str): Path to the TSV log file.
        log_file_xlsx (str): Path to the Excel log file.
        progress_queue (queue.Queue): Queue to communicate progress to the GUI.
        low_threshold (float): Low gray threshold percentage.
        high_threshold (float): High gray threshold percentage.
    """
    try:
        # Build TIFF mapping
        tiff_mapping = build_tiff_mapping(input_dir_tiff)
        if not tiff_mapping:
            logging.error("No valid TIFF files found. Exiting.")
            progress_queue.put(("error", "No valid TIFF files found in the selected directory."))
            return

        # Collect all JPG files
        all_jpg_files = [
            f for f in os.listdir(input_dir_jpg)
            if f.lower().endswith(('.jpg', '.jpeg')) and is_valid_jpg(f)
        ]
    
        if not all_jpg_files:
            logging.error("No valid JPG files found. Exiting.")
            progress_queue.put(("error", "No valid JPG files found in the selected directory."))
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
                logging.warning(f"Could not extract necessary digits from JPG '{jpg_file}'. Skipping.")
                processed_files += 1
                progress_queue.put(("progress", processed_files, total_files))
                continue
    
            # Find corresponding TIFF(s)
            key = (first_digit, last_four)
            tiff_files = tiff_mapping.get(key)
            if not tiff_files:
                logging.warning(f"No corresponding TIFF found for JPG '{jpg_file}' with key {key}. Skipping.")
                processed_files += 1
                progress_queue.put(("progress", processed_files, total_files))
                continue
    
            jpg_path = os.path.join(input_dir_jpg, jpg_file)
    
            gray_pct = calculate_gray_percentage(jpg_path)
            if gray_pct is None:
                logging.error(f"Skipping {jpg_file} due to read error.")
                processed_files += 1
                progress_queue.put(("progress", processed_files, total_files))
                continue
    
            # Decision logic
            if gray_pct < low_threshold:
                selected_format = "TIFF"
                # Log all corresponding TIFF base names, separated by commas
                selected_documents = ', '.join([os.path.splitext(tiff)[0] for tiff in tiff_files])
            elif gray_pct > high_threshold:
                selected_format = "JPG"
                # Log the JPG's base name
                selected_documents = base_name
            else:
                selected_format = "JPG (Intermediate)"
                # Log the JPG's base name
                selected_documents = base_name
                flagged_count += 1  # Increment counter for flagged files
    
            # Append the entry with sort key based on first and last four digits
            sort_key = get_sort_key(first_digit, last_four)
            log_entries.append((sort_key, selected_documents, f"{gray_pct:.2f}", selected_format))
    
            # Log the decision in debug log
            logging.info(f"Document: {selected_documents}, Gray_Percentage: {gray_pct:.2f}, Selected_Format: {selected_format}")
    
            # Update progress
            processed_files += 1
            progress_queue.put(("progress", processed_files, total_files))
    
        # Sort the log entries based on the sort key (first digit, then last four digits)
        log_entries_sorted = sorted(log_entries, key=lambda x: x[0])
    
        # ---------------------------- Write to TSV File ---------------------------- #
        try:
            with open(log_file_tsv, mode='w', newline='') as log_csv:
                log_writer = csv.writer(log_csv, delimiter='\t')  # Tab delimiter
                # Write header with the fourth column
                log_writer.writerow(['Document', 'Gray_Percentage', 'Selected_Format', 'Flagged_Files'])  # Header
    
                # Write data rows with the fourth column empty
                for entry in log_entries_sorted:
                    _, selected_documents, gray_pct_str, selected_format = entry
                    log_writer.writerow([selected_documents, gray_pct_str, selected_format, ''])
            logging.info(f"TSV log saved to {log_file_tsv}")
        except Exception as e:
            logging.error(f"Failed to write TSV log: {str(e)}")
            progress_queue.put(("error", f"Failed to write TSV log: {str(e)}"))
            return
    
        # ---------------------------- Write to Excel File ---------------------------- #
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Selection Log"
    
            # Define headers
            headers = ['Document', 'Gray Percentage (%)', 'Selected Format', 'Flagged Files']
            header_font = Font(bold=True)
    
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num, value=header)
                cell.font = header_font
    
            # Write data rows
            for row_num, entry in enumerate(log_entries_sorted, start=2):
                _, selected_documents, gray_pct_str, selected_format = entry
                ws.cell(row=row_num, column=1, value=selected_documents)
                ws.cell(row=row_num, column=2, value=float(gray_pct_str))
                ws.cell(row=row_num, column=3, value=selected_format)
                ws.cell(row=row_num, column=4, value='')  # Empty for Flagged Files
    
            # Adjust column widths for better readability
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if cell.value:
                            cell_length = len(str(cell.value))
                            if cell_length > max_length:
                                max_length = cell_length
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column_letter].width = adjusted_width
    
            # Save the workbook
            wb.save(log_file_xlsx)
            logging.info(f"Excel log saved to {log_file_xlsx}")
        except Exception as e:
            logging.error(f"Failed to write Excel log: {str(e)}")
            progress_queue.put(("error", f"Failed to write Excel log: {str(e)}"))
            return
    
        # ---------------------------- Notify Completion ---------------------------- #
        progress_queue.put(("complete", "Processing complete. Logs saved to selection_log.tsv and selection_log.xlsx", flagged_count))
    
    except Exception as e:
        logging.error(f"An unexpected error occurred during processing: {str(e)}")
        progress_queue.put(("error", f"An unexpected error occurred: {str(e)}"))
        return