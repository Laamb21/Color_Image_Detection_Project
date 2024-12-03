'''
Test file to determine if images in a folder are color, grayscale
or balck and white
'''

import os
import sys
import threading
import csv
import random
from tkinter import Entry, Tk, Label, Button, Radiobutton, StringVar, filedialog, messagebox
from tkinter.ttk import Progressbar
from PIL import Image
import cv2
import numpy as np

# --------------------- Image Classification Functions ---------------------

def determine_image_type_pillow(image_path):
    """
    Determines if the image is color, grayscale, or black and white using Pillow.

    Parameters:
    - image_path: str, path to the image file.

    Returns:
    - str: 'color', 'grayscale', or 'black and white'
    """
    try:
        with Image.open(image_path) as img:
            # Handle different image modes
            if img.mode not in ("RGB", "RGBA", "L"):
                img = img.convert("RGB")
            
            width, height = img.size
            total_pixels = width * height

            pixels = img.getdata()
            sampled_pixels = list(pixels)  # Process all pixels

            if img.mode in ("RGB", "RGBA"):
                # Check if all pixels have R=G=B
                is_grayscale = all(p[0] == p[1] == p[2] for p in sampled_pixels)
                if is_grayscale:
                    # Convert to grayscale
                    gray = img.convert("L")
                    gray_pixels = list(gray.getdata())
                    # Check if all grayscale pixels are 0 or 255
                    is_bw = all(p in (0, 255) for p in gray_pixels)
                    return "black and white" if is_bw else "grayscale"
                else:
                    return "color"
            
            elif img.mode == "L":
                # Grayscale image
                gray_pixels = sampled_pixels
                is_bw = all(p in (0, 255) for p in gray_pixels)
                return "black and white" if is_bw else "grayscale"
            
            else:
                return "unknown"
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return "error"

def determine_image_type_opencv(image_path):
    """
    Determines if the image is color, grayscale, or black and white using OpenCV.

    Parameters:
    - image_path: str, path to the image file.

    Returns:
    - str: 'color', 'grayscale', or 'black and white'
    """
    try:
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Unable to read image: {image_path}")
            return "error"

        # Check number of channels
        if len(img.shape) == 3:
            # Check if all channels are the same
            b, g, r = cv2.split(img[:, :, :3])
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
            # Grayscale image
            unique_values = np.unique(img)
            if set(unique_values).issubset({0, 255}):
                return "black and white"
            else:
                return "grayscale"
        else:
            return "unknown"
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return "error"

# --------------------- GUI Application ---------------------

class ImageClassifierApp:
    def __init__(self, master):
        self.master = master
        master.title("Batch Image Classifier")

        # Initialize variables
        self.folder_path = ""
        self.method = StringVar(value="Pillow")
        self.results = []
        self.csv_data = []
        self.processing_thread = None

        # Folder Selection
        self.label = Label(master, text="Select Image Folder:")
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky='e')

        self.folder_entry = Entry(master, width=50)
        self.folder_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_button = Button(master, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        # Processing Method
        self.method_label = Label(master, text="Select Processing Method:")
        self.method_label.grid(row=1, column=0, padx=10, pady=10, sticky='e')

        self.pillow_radio = Radiobutton(master, text="Pillow", variable=self.method, value="Pillow")
        self.pillow_radio.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        self.opencv_radio = Radiobutton(master, text="OpenCV", variable=self.method, value="OpenCV")
        self.opencv_radio.grid(row=1, column=1, padx=80, pady=5, sticky='w')

        # Start Button
        self.start_button = Button(master, text="Start Processing", command=self.start_processing)
        self.start_button.grid(row=2, column=1, padx=10, pady=20)

        # Progress Bar
        self.progress = Progressbar(master, orient='horizontal', length=400, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Save CSV Button
        self.save_button = Button(master, text="Save CSV", command=self.save_csv, state='disabled')
        self.save_button.grid(row=4, column=1, padx=10, pady=10)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path = folder_selected
            self.folder_entry.delete(0, 'end')
            self.folder_entry.insert(0, folder_selected)

    def start_processing(self):
        if not self.folder_entry.get():
            messagebox.showwarning("Input Required", "Please select an image folder.")
            return

        # Disable buttons to prevent multiple clicks
        self.start_button.config(state='disabled')
        self.save_button.config(state='disabled')

        # Reset progress bar and results
        self.progress['value'] = 0
        self.results = []

        # Start processing in a separate thread
        self.processing_thread = threading.Thread(target=self.process_images)
        self.processing_thread.start()

    def process_images(self):
        folder = self.folder_entry.get()
        method = self.method.get()

        # Supported image extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif'}

        # Gather all image files
        all_files = [f for f in os.listdir(folder) if os.path.splitext(f.lower())[1] in image_extensions]

        total_files = len(all_files)
        if total_files == 0:
            messagebox.showinfo("No Images", "No supported image files found in the selected folder.")
            self.start_button.config(state='normal')
            return

        self.progress['maximum'] = total_files

        for idx, filename in enumerate(all_files, start=1):
            image_path = os.path.join(folder, filename)
            if method == "Pillow":
                image_type = determine_image_type_pillow(image_path)
            else:
                image_type = determine_image_type_opencv(image_path)
            
            self.results.append((filename, image_type))
            self.progress['value'] = idx

            # Update the GUI
            self.master.update_idletasks()

        # Enable Save button after processing
        self.save_button.config(state='normal')
        self.start_button.config(state='normal')
        messagebox.showinfo("Processing Complete", "Image classification completed successfully.")

    def save_csv(self):
        if not self.results:
            messagebox.showwarning("No Data", "No classification results to save.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension='.csv',
                                                 filetypes=[('CSV files', '*.csv')],
                                                 title="Save CSV")
        if save_path:
            try:
                with open(save_path, mode='w', newline='', encoding='utf-8') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(['Filename', 'Image Type'])
                    writer.writerows(self.results)
                messagebox.showinfo("Success", f"CSV file saved successfully at:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save CSV file:\n{e}")

# --------------------- Main Execution ---------------------

def main():
    root = Tk()
    app = ImageClassifierApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
