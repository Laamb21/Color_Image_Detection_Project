'''
Used chat to make a GUI for code from main.py
'''

import os
from tkinter import Tk, Button, Label, filedialog
from PIL import Image
import pytesseract

# Function to allow directory selection
def select_directory(label):
    directory = filedialog.askdirectory()
    label.config(text=directory)
    return directory

# Main function to process TIFF images
def process_images(tiff_dir, jpeg_dir, output_dir):
    # Iterate over TIFF files
    for tiff_filename in os.listdir(tiff_dir):
        if tiff_filename.startswith("10") or tiff_filename.startswith("20"):
            tiff_path = os.path.join(tiff_dir, tiff_filename)
            # Derive the color JPEG path
            color_filename = tiff_filename.replace("10", "11").replace("20", "21")
            jpeg_path = os.path.join(jpeg_dir, color_filename)

            try:
                # Open the TIFF image
                tiff_image = Image.open(tiff_path)

                # Perform OCR to check for text
                ocr_text = pytesseract.image_to_string(tiff_image)

                # Check if image contains significant non-text content (images, graphs)
                # Replace if the page is detected as containing images or if OCR content is minimal
                if 'image' in ocr_text.lower() or len(ocr_text.strip()) < 50:
                    if os.path.exists(jpeg_path):
                        # Replace with color image if condition is met and color image exists
                        color_image = Image.open(jpeg_path)
                        color_image.save(os.path.join(output_dir, tiff_filename))
                        print(f'Replaced: {tiff_filename} with its color version.')
                    else:
                        # Log if the corresponding color JPEG is missing
                        print(f'Color JPEG not found for: {tiff_filename}, using original TIFF.')
                        tiff_image.save(os.path.join(output_dir, tiff_filename))
                else:
                    # Save the original black-and-white image if it's text-only
                    tiff_image.save(os.path.join(output_dir, tiff_filename))
                    print(f'Kept original TIFF for: {tiff_filename}')

            except Exception as e:
                print(f'Error processing {tiff_filename}: {e}')

# GUI setup
def create_gui():
    # Create the main window
    root = Tk()
    root.title("TIFF Image Processor")

    # Labels and Buttons for directory selection
    tiff_label = Label(root, text="Select TIFF Directory")
    tiff_label.pack(pady=5)

    tiff_button = Button(root, text="Browse", command=lambda: select_directory(tiff_label))
    tiff_button.pack(pady=5)

    jpeg_label = Label(root, text="Select JPEG Directory")
    jpeg_label.pack(pady=5)

    jpeg_button = Button(root, text="Browse", command=lambda: select_directory(jpeg_label))
    jpeg_button.pack(pady=5)

    output_label = Label(root, text="Select Output Directory")
    output_label.pack(pady=5)

    output_button = Button(root, text="Browse", command=lambda: select_directory(output_label))
    output_button.pack(pady=5)

    # Button to run the processing
    run_button = Button(root, text="Run", command=lambda: process_images(tiff_label.cget("text"), jpeg_label.cget("text"), output_label.cget("text")))
    run_button.pack(pady=20)

    # Run the main loop
    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    create_gui()
