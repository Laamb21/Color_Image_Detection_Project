'''
Taking new approach on color analysis on multiple files
'''

#Import libraries
import os
from PIL import Image
import numpy as np
import matplotlib.colors as mcolors

#Define color categories with HSV ranges
COLOR_RANGES = {
    'red':      {'h_min': 0/360, 'h_max': 10/360},
    'orange':   {'h_min': 11/360, 'h_max': 25/360},
    'yellow':   {'h_min': 26/360, 'h_max': 35/360},
    'green':    {'h_min': 36/360, 'h_max': 85/360},
    'blue':     {'h_min': 86/360, 'h_max': 125/360},
    'purple':   {'h_min': 126/360,'h_max': 160/360},
}

def is_grayscale(img):
    if img.mode not in ("L", "RGB", "RGBA"):
        return False
    if img.mode == "L":
        return True
    
    #Check if all channels are equal
    np_img = np.array(img)
    if img.mode == "RGB":
        return np.all(np_img[:,:,0] == np_img[:,:,1]) and np.all(np_img[:,:,0] == np_img[:,:,2])
    elif img.mode == "RGBA":
        return np.all(np_img[:,:,0] == np_img[:,:,1]) and np.all(np_img[:,:,0] == np_img[:,:,2])
    return False

def categorize_colors(img):
    #Convert image to RGB
    img = img.convert('RGB')
    np_img = np.array(img)
    #Normalize RGB values
    rgb_norm = np_img / 255.0
    #Convert RGB to HSV 
    hsv = np.apply_along_axis(lambda rgb: mcolors.rgb_to_hsv(rgb), 2, rgb_norm)
    hues = hsv[:,:,0]      #Hue values
    counts = {color: set() for color in COLOR_RANGES}
    for color, range_vals in COLOR_RANGES.items():
        mask = (hues >= range_vals['h_min']) & (hues <= range_vals['h_max'])
        #Extract the RGB tuples where mask is true
        shades = tuple(map(tuple, np_img[mask]))
        counts[color].update(shades)
    #Convert sets to counts 
    counts = {color: len(shades) for color, shades, in counts.items()}
    return counts

def count_grayscale_shades(img):
    np_img = np.array(img)
    unique_shades = np.unique(np_img)
    return len(unique_shades)

def process_jpg(file_path):
    try:
        img = Image.open(file_path)
    except Exception as e:
        print(f"Error opening {file_path}: {e}")

    if is_grayscale(img):
        shades = count_grayscale_shades(img)
        print(f"[JPG] {os.path.basename(file_path)} is Grayscale with {shades} shades of gray.")

    else:
        color_counts = categorize_colors(img)
        print(f"[JPG] {os.path.basename(file_path)} is Color.")
        for color, counts, in color_counts.items():
            print(f"    {color.capitalize()} shades: {counts}")
    
    img.close()

def process_tiff(file_path):
    try:
        img = Image.open(file_path)
    except Exception as e:
        print(f"Error opening {file_path}: {e}")

    #Assuming TIFFs are balck and white; check number of unique shades 
    np_img = np.array(img)
    unique_shades = np.unique(img)
    print(f"[TIFF] {os.path.basename(file_path)} has {len(unique_shades)} shades of black and white.")
    img.close()

def main():
    base_folder = "D:/test_data"
    jpg_folder = os.path.join(base_folder, "JPG")
    tiff_folder = os.path.join(base_folder, "TIFF")

    #Define valid image extensions
    jpg_extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG')
    tiff_extensions = ('.tif', '.tiff', '.TIF', '.TIFF')

    #Function to filter valid image files and exclude hidden/system files
    def get_valid_files(folder, extensions):
        if not os.path.exists(folder):
            print(f"Folder not found: {folder}")
            return []
        files = []
        for filename in os.listdir(folder):
            #Exclude hidden/system files starting with '.' or '_'
            if filename.startswith('.') or filename.startswith('_'):
                continue
            if filename.lower().endswith(extensions):
                files.append(os.path.join(folder, filename))
        return files

    #Process JPG files
    print(f"Processing JPG files...")
    jpg_files = get_valid_files(jpg_folder, jpg_extensions)
    for file_path in jpg_files:
        process_jpg(file_path)
    '''
    if os.path.exists(jpg_folder):
        print("Processing JPG files")
        for filename in os.listdir(jpg_folder):
            if filename.lower().endswith(('.jpg', '.jpeg')):
                file_path = os.path.join(jpg_folder, filename)
                process_jpg(file_path)
    else:
        print(f"JPG folder not found at {jpg_folder}")
    '''

    #Process TIFF files
    print("\nProcessing TIFF files...")
    tiff_files = get_valid_files(tiff_folder, tiff_extensions)
    for file_path in tiff_files:
        process_tiff(file_path)
    '''
    if os.path.exists(tiff_folder):
        print("\nProcessing TIFF files...")
        for filename in os.listdir(tiff_folder):
            if filename.lower().endswith(('.tif', '.tiff')):
                file_path = os.path.join(tiff_folder, filename)
                process_tiff(file_path)
    else:
        print(f"TIFF folder not found at {tiff_folder}")
    '''
    

if __name__ == "__main__":
    main()
