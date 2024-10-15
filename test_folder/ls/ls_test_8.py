'''
Test to determine threshold for choosing JPG or TIFF (grayscale vs. black and white)
'''

#Import libraries 
import os
import cv2
import numpy as np
import shutil
from tqdm import tqdm
import csv

#Configuration
INPUT_DIR_JPG = "D:/test_data/JPG"                              #Directory containing JPG files
INPUT_DIR_TIFF = "D:/test_data/TIFF"                            #Directory containing TIFF files
OUTPUT_DIR_JPG = "D:/test_data/tests/test_2/output_jpg"         #Directory to store selected JPG files
OUTPUT_DIR_TIFF = "D:/test_data/tests/test_2/output_tiff"       #Directory to store selected TIFF files
LOG_FILE = 'selection_log.csv'                                  #CSV file to log decisions

#Thresholds for gray percentage
LOW_GRAY_THRESHOLD = 5      #Below this percentage, use TIFF
HIGH_GRAY_THRESHOLD = 20    #Above this percentage, use TIFF

#Ensure output directories exist
os.makedirs(OUTPUT_DIR_JPG, exist_ok=True)
os.makedirs(OUTPUT_DIR_TIFF, exist_ok=True)

def calculate_gray_percentage(image_path):
    #Calculate the percentag of gray pixels in a grayscale image.
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Error reading image: {image_path}")
        return None
    
    total_pixels = image.size
    #Count pixels tat are not 0 and not 255
    gray_pixels = np.count_nonzero((image > 0) & (image < 255))
    gray_percentage = (gray_pixels / total_pixels) * 100
    return gray_percentage


'''
def derive_tiff_filename(jpg_filename):
    #Derive corresponding TIFF filename from JPG filename 

    base, ext = os.path.splitext(jpg_filename)
    if len(base) < 2 or not base[1].isdigit():
        print(f"Filename '{jpg_filename}' does not conform to expected format.")
        return None
    
    #Replace second character with '0' 
    tiff_base = base[:1] + '0' + base[2:]
    tiff_filename = tiff_base + '.tiff'
    return tiff_filename
'''

def extract_last_four_digits(filename):
    #Extract last four digits before file extension
    #Returns last four digits as a string, or None if extraction fails

    base, ext = os.path.splitext(filename)
    digits = ''.join(filter(str.isdigit, base))
    if len(digits) < 4:
        return None
    return digits[-4:]


def is_valid_jpg(filename):
    #Check if the filename is a valid JPG based on the second digit being 1

    base, ext = os.path.splitext(filename)
    if len(base) < 2 or not base[1].isdigit():
        return False
    return base[1] == '1'

def is_valid_tiff(filename):
    #Check if the filename is a valiud TIFF based on the seconf digit being 0

    base, ext = os.path.splitext(filename)
    if len(base) < 2 or not base[1].isdigit():
        return False
    return base[1] == '0'

def build_tiff_mapping(input_dir_tiff):
    #Build dictionary mapping last four digits to TIFF file names. Only include TIFFs with second digit as '0'

    tiff_mapping = {}
    all_tiff_files = [f for f in os.listdir(input_dir_tiff)
                      if f.lower().endswith(('.tif', '.tiff')) and is_valid_tiff(f)]
    
    print(f"Foung {len(all_tiff_files)} valid TIFF files")
    
    for tiff in all_tiff_files:
        last_four = extract_last_four_digits(tiff)
        if last_four:
            if last_four in tiff_mapping:
                tiff_mapping[last_four].append(tiff)
                print(f"Appending to existing key: {last_four} -> {tiff}")
            else:
                tiff_mapping[last_four] = [tiff]
                print(f"Mapping: {last_four} -> {tiff}")
        else:
            print(f"Warning: Could not extract last four digits from TIFF '{tiff}'. Skipping. ")

    return tiff_mapping

def process_documents(input_dir_jpg, input_dir_tiff, output_dir_jpg, output_dir_tiff, log_file):
    #Process all JPG and TIFF pairs in the input directories, and decide which format to use

    #Build TIFF mapping
    tiff_mapping = build_tiff_mapping(input_dir_tiff)
    if not tiff_mapping:
        print(f"No valid TIFF files found. Exiting")
        return
    
    #Collect all JPG files
    all_jpg_files = [f for f in os.listdir(input_dir_jpg) if f.lower().endswith(('.jpg', '.jpeg')) and is_valid_jpg(f)]

    if not all_jpg_files:
        print(f"No valid JPG files. Exiting.")
        return
    
    
    '''
    #Collect all TIFF files
    all_tiff_files = [f for f in os.listdir(input_dir_tiff) if f.lower().endswith(('.tif', '.tiff')) and is_valid_tiff(f)]

    #Create a quick lookup for the TIFF file names 
    tiff_set = set(os.path.splitext(f)[0].lower() for f in all_tiff_files)

    '''
    
    #Prepare log file 
    with open(log_file, mode='w', newline='') as log_csv:
        log_writer = csv.writer(log_csv)
        log_writer.writerow(['Document', 'Gray_Percentage', 'Selected_Format'])

        for jpg_file in tqdm(all_jpg_files, desc="Processing Documents"):
            last_four = extract_last_four_digits(jpg_file)
            if not last_four:
                print(f"Warning: Could not extract last four digits from JPG '{jpg_file}'. Skipping.")
                continue

            #Find corresponding TIFF
            tiff_files = tiff_mapping.get(last_four)
            if not tiff_files:
                print(f"Warning: No corresponding TIFF found for JPG '{jpg_file}' with last four digits '{last_four}'. Skipping.")

            jpg_path = os.path.join(input_dir_jpg, jpg_file)

            gray_pct = calculate_gray_percentage(jpg_path)
            if gray_pct is None:
                print(f"Skipping {jpg_file} due to read error")
                continue

            #Decision logic
            if gray_pct < LOW_GRAY_THRESHOLD:
                selected_format = "TIFF"
                for tiff_file in tiff_files:
                    tiff_path = os.path.join(input_dir_tiff, tiff_file)
                    destination = os.path.join(output_dir_tiff, tiff_file)
                    try:
                        shutil.copy2(tiff_path, destination)
                    except Exception as e:
                        print(f"Error copying TIFF '{tiff_file}': {e}")
                        selected_format = "TIFF (Copy failed)"
                #Log once per JPG
                log_writer.writerow([tiff_file, f"{gray_pct:.2f}", selected_format])
            elif gray_pct > HIGH_GRAY_THRESHOLD:
                selected_format = "JPG"
                destination = os.path.join(output_dir_jpg, jpg_file)
                try:
                    shutil.copy2(jpg_path, destination)
                except Exception as e:
                    print(f"Error copying JPG '{jpg_file}': {e}")
                    selected_format = "JPG (Copy failed)"
                #Log once per JPG
                log_writer.writerow([jpg_file, f"{gray_pct:.2f}", selected_format])
            else:
                selected_format = "JPG (Intermediate)"
                destination = os.path.join(output_dir_jpg, jpg_file)
                try:
                    shutil.copy2(jpg_path, destination)
                except Exception as e:
                    print(f"Error copying JPG '{jpg_file}': {e}")
                    selected_format = "JPG (Intermediate Copy failed)"
                log_writer.writerow([jpg_file, f"{gray_pct:.2f}", selected_format])
    
    print(f"\nProcessing complete. Log saved to {log_file}")

if __name__ == "__main__":
    process_documents(INPUT_DIR_JPG, INPUT_DIR_TIFF, OUTPUT_DIR_JPG, OUTPUT_DIR_TIFF, LOG_FILE)