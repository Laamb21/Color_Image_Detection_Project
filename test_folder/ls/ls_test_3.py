'''
Modified GUI from ls_test_2.py
'''

import os
from tkinter import Tk, Button, Label, filedialog, Text, Scrollbar, END
from PIL import Image
import pytesseract
import sys
import threading

# Function to allow directory selection
def select_directory(label):
    directory = filedialog.askdirectory()
    label.config(text=directory)
    return directory

# Function to redirect print statements to the Text widget in the GUI
class RedirectOutputToGUI:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.insert(END, text)
        self.text_widget.see(END)  # Auto-scroll to the bottom

    def flush(self):
        pass  # Required to handle flush calls from Python's output system

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

# Wrapper to run the process in a separate thread to avoid blocking the GUI
def run_in_thread(tiff_dir, jpeg_dir, output_dir):
    thread = threading.Thread(target=process_images, args=(tiff_dir, jpeg_dir, output_dir))
    thread.start()

# GUI setup
def create_gui():
    # Create the main window
    root = Tk()
    root.title("TIFF Image Processor")
    
    # Set the window size (increase size for a bigger window)
    root.geometry("600x600")

    # Buttons and Labels for directory selection
    tiff_button = Button(root, text="Select TIFF Directory", command=lambda: select_directory(tiff_label))
    tiff_button.pack(pady=5)

    tiff_label = Label(root, text="")
    tiff_label.pack(pady=5)

    jpeg_button = Button(root, text="Select JPEG Directory", command=lambda: select_directory(jpeg_label))
    jpeg_button.pack(pady=5)

    jpeg_label = Label(root, text="")
    jpeg_label.pack(pady=5)

    output_button = Button(root, text="Select Output Directory", command=lambda: select_directory(output_label))
    output_button.pack(pady=5)

    output_label = Label(root, text="")
    output_label.pack(pady=5)

    # Button to run the processing
    run_button = Button(root, text="Run", command=lambda: run_in_thread(tiff_label.cget("text"), jpeg_label.cget("text"), output_label.cget("text")))
    run_button.pack(pady=20)

    # Text widget for displaying output (moved below the Run button, and made larger)
    output_text = Text(root, height=300, wrap='word')  # Increased height to 20
    output_text.pack(pady=10, fill='both', expand=True)

    # Scrollbar for the output Text widget
    scrollbar = Scrollbar(output_text)
    scrollbar.pack(side="right", fill="y")
    output_text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=output_text.yview)

    # Redirect output to the Text widget in the GUI
    sys.stdout = RedirectOutputToGUI(output_text)  # Redirect print output to the GUI

    # Run the main loop
    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    create_gui()
