'''
JPG TIFF Selection Script with Tkinter Front End
Refactored to eliminate output directories and only use input directories and a log file.
Logs the selected file's full name without extension in selection_log.tsv based on the decision.
Accounts for front (1) and back (2) captures of documents.
Sorts the log entries first by first digit (1 then 2), and within each group by last four digits from least to greatest.
Adds a count of "JPG (Intermediate)" selections.
Includes a Tkinter GUI with folder selection, run button, progress bar, and log display.
'''

# ---------------------------- Import Libraries ---------------------------- #
import os
import cv2
import numpy as np
import csv
import logging
from logging.handlers import RotatingFileHandler
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import queue

# ---------------------------- Configuration ---------------------------- #

# Thresholds for gray percentage
LOW_GRAY_THRESHOLD = 10      # Below this percentage, use TIFF
HIGH_GRAY_THRESHOLD = 15    # Above this percentage, use JPG

# ---------------------------- Logging Setup ---------------------------- #

# Configure logging with rotating file handler to prevent log file from growing indefinitely
logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = RotatingFileHandler('processing_debug.log', maxBytes=5*1024*1024, backupCount=2)  # 5MB per file, keep 2 backups
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

# ---------------------------- Image Processing Functions ---------------------------- #

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

def process_documents(input_dir_jpg, input_dir_tiff, log_file, progress_queue):
    """
    Process all JPG and TIFF pairs in the input directories, decide which format to use,
    and log the selected file's base name without extension based on the decision.
    Sorts the log entries first by first digit (1 then 2), and within each group by last four digits from least to greatest.
    Adds a count of "JPG (Intermediate)" selections.
    
    Parameters:
        input_dir_jpg (str): Directory containing JPG files.
        input_dir_tiff (str): Directory containing TIFF files.
        log_file (str): Path to the TSV log file.
        progress_queue (queue.Queue): Queue to communicate progress to the GUI.
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
    
        # Write the sorted entries to the TSV file
        with open(log_file, mode='w', newline='') as log_csv:
            log_writer = csv.writer(log_csv, delimiter='\t')  # Tab delimiter
            # Write header with the fourth column
            log_writer.writerow(['Document', 'Gray_Percentage', 'Selected_Format', 'Flagged_Files'])  # Header
    
            # Write data rows with the fourth column empty
            for entry in log_entries_sorted:
                _, selected_documents, gray_pct_str, selected_format = entry
                log_writer.writerow([selected_documents, gray_pct_str, selected_format, ''])
    
            # After all data rows, add a summary in the GUI instead of the TSV
    
        # Notify completion with flagged_count
        progress_queue.put(("complete", "Processing complete. Log saved to selection_log.tsv", flagged_count))
    
    except Exception as e:
        logging.exception("An unexpected error occurred during processing.")
        progress_queue.put(("error", f"An unexpected error occurred: {str(e)}"))
    
    # ---------------------------- GUI Class ---------------------------- #

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("JPG TIFF Selection Script")
        self.root.geometry("800x600")
        
        # Queue for thread communication
        self.progress_queue = queue.Queue()
        
        # Header
        header = ttk.Label(root, text="JPG TIFF Selection Script", font=("Helvetica", 16))
        header.pack(pady=10)
        
        # Folder Selection Frame
        folder_frame = ttk.Frame(root)
        folder_frame.pack(pady=10, padx=10, fill='x')
        
        # Store reference to the Select Folder button
        self.select_button = ttk.Button(folder_frame, text="Select Folder", command=self.select_folder)
        self.select_button.pack(side='left')
        
        self.selected_folder = tk.StringVar()
        folder_label = ttk.Label(folder_frame, textvariable=self.selected_folder, foreground="blue")
        folder_label.pack(side='left', padx=10)
        
        # Run Button
        # Store reference to the Run Script button
        self.run_button = ttk.Button(root, text="Run Script", command=self.run_script)
        self.run_button.pack(pady=10)
        
        # Progress Bar
        progress_frame = ttk.Frame(root)
        progress_frame.pack(pady=10, padx=10, fill='x')
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x')
        
        # Progress Percentage Label
        self.progress_percentage_var = tk.StringVar(value="0%")
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_percentage_var)
        progress_label.pack(side='right', padx=10)
        
        # Current File Label
        self.current_file_var = tk.StringVar(value="No file being processed.")
        current_file_label = ttk.Label(root, textvariable=self.current_file_var, foreground="green")
        current_file_label.pack(pady=5)
        
        # Text Window for selection_log.tsv
        log_label = ttk.Label(root, text="Selection Log:")
        log_label.pack(pady=(20, 0))
        
        self.log_text = scrolledtext.ScrolledText(root, width=100, height=20, state='disabled')
        self.log_text.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Status Label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(root, textvariable=self.status_var, foreground="green")
        self.status_label.pack(pady=5)
        
        # Initialize variables
        self.parent_folder = ""
        
        # Periodically check the queue
        self.root.after(100, self.process_queue)
    
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.parent_folder = folder_selected
            self.selected_folder.set(folder_selected)
    
    def run_script(self):
        if not self.parent_folder:
            messagebox.showwarning("No Folder Selected", "Please select a folder before running the script.")
            return
        
        # Define input directories based on the parent folder
        input_dir_jpg = os.path.join(self.parent_folder, "JPG")
        input_dir_tiff = os.path.join(self.parent_folder, "TIF")  # Updated from "TIFF" to "TIF"
        log_file = os.path.join(self.parent_folder, "selection_log.tsv")
        
        # Check if input directories exist
        if not os.path.isdir(input_dir_jpg):
            messagebox.showerror("Invalid Directory", f"JPG directory not found: {input_dir_jpg}")
            return
        if not os.path.isdir(input_dir_tiff):
            messagebox.showerror("Invalid Directory", f"TIF directory not found: {input_dir_tiff}")
            return
        
        # Disable only the select and run buttons to prevent multiple runs
        self.select_button.configure(state='disabled')
        self.run_button.configure(state='disabled')
        
        # Reset progress bar and current file label
        self.progress_var.set(0)
        self.progress_percentage_var.set("0%")
        self.current_file_var.set("Starting processing...")
        
        # Update status
        self.status_var.set("Processing...")
        
        # Start the processing in a separate thread
        processing_thread = threading.Thread(target=process_documents, args=(input_dir_jpg, input_dir_tiff, log_file, self.progress_queue))
        processing_thread.start()
    
    def process_queue(self):
        try:
            while True:
                message = self.progress_queue.get_nowait()
                if message[0] == "progress":
                    processed, total = message[1], message[2]
                    percentage = (processed / total) * 100
                    self.progress_var.set(percentage)
                    self.progress_percentage_var.set(f"{percentage:.2f}%")
                elif message[0] == "complete":
                    self.status_var.set(message[1])
                    flagged_count = message[2]
                    self.load_log()
                    # Re-enable only the select and run buttons
                    self.select_button.configure(state='normal')
                    self.run_button.configure(state='normal')
                    # Display the flagged count in the GUI
                    messagebox.showinfo("Processing Complete", f"{message[1]}\nFlagged Files Count: {flagged_count}")
                    # Reset current file label
                    self.current_file_var.set("Processing complete.")
                elif message[0] == "error":
                    self.status_var.set(message[1])
                    messagebox.showerror("Error", message[1])
                    # Re-enable only the select and run buttons
                    self.select_button.configure(state='normal')
                    self.run_button.configure(state='normal')
                    # Reset current file label
                    self.current_file_var.set("Error encountered.")
                elif message[0] == "current_file":
                    current_file = message[1]
                    self.current_file_var.set(f"Processing: {current_file}")
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)
    
    def load_log(self):
        log_file = os.path.join(self.parent_folder, "selection_log.tsv")
        if os.path.exists(log_file):
            with open(log_file, 'r') as file:
                content = file.read()
            self.log_text.configure(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, content)
            self.log_text.configure(state='disabled')
        else:
            self.log_text.configure(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, "Log file not found.")
            self.log_text.configure(state='disabled')

# ---------------------------- Main Execution ---------------------------- #

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
