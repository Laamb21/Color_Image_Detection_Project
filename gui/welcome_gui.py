'''
Gui file for welcome screen
'''

#Import libraries 
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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
    

def create_welcome_window(self):

    #Call function to create header 
    create_header(self)

    #Create "Welcome!" label
    welcome_label = tk.Label(self.root, text="Welcome to the \nJPG and TIF Processor!", font=("Merriweather", 36, "bold"))
    welcome_label.pack(pady=50)

    #Create "Get Started" button
    get_started_button = tk.Button(self.root, text="Get Started!",bg="#4a90e2", fg="white", padx=50, pady=20)
    get_started_button.pack(pady=20)

