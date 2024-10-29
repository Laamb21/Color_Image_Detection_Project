'''
Main GUI file to hold all window instances
'''

#Import libraries
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

#Import additional GUI windows 
from welcome_gui import create_welcome_window
from upload_gui import create_upload_window

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("JPG TIF Processor")
        self.root.geometry("600x600")

        #Initialize varibales 
        self.parent_folder = tk.StringVar()

        #Function call to create header
        self.create_header()

        #Function call to create welcome window
        create_welcome_window(self)

    def create_header(self):
        #Create haeder frame
        header_frame = tk.Frame(self.root, bg='#4a90e2', height = 160)
        header_frame.pack(fill='x')

        #Define logo path
        logo_path = "C:/Users/liams/ArchScan_Capture_Project/color_image_detection/test_folder/ls/archSCAN_logo.png"

        # Check if the file exists
        if not os.path.isfile(logo_path):
            print(f"Error: Logo image file not found at the specified path: {logo_path}")
            return

        # Load logo image using Pillow
        try:
            logo_image = Image.open(logo_path).convert("RGBA")
            print(f"Successfully loaded image: {logo_path}")
        except Exception as e:
            print(f"Error loading image: {e}")
            return

        # Resize the image
        desired_width = 200
        w_percent = (desired_width / float(logo_image.size[0]))
        h_size = int((float(logo_image.size[1]) * float(w_percent)))
        print(f"Resized image to: {desired_width}x{h_size}")

        # Convert the Image object into a TkPhoto object
        try:
            logo_photo = ImageTk.PhotoImage(logo_image)
            print("Image converted to PhotoImage successfully.")
        except Exception as e:
            print(f"Error converting image to PhotoImage: {e}")
            return

        # Create a label to hold the logo image
        try:
            logo_label = tk.Label(header_frame, image=logo_photo)
            logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
            logo_label.pack(pady=50)
            print("Logo label created and packed successfully.")
        except Exception as e:
            print(f"Error creating or packing the logo label: {e}")
            return



def main():    
    # Initialize and run the GUI
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
