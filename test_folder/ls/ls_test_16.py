'''
Test to get archSCAN logo in Tkinter window 
'''

import tkinter as tk
from PIL import Image, ImageTk
import os

def main():
    # Initialize main window
    root = tk.Tk()
    root.title("Logo Test")
    root.geometry("400x300")
    root.configure(bg='white')

    # Define the logo path
    logo_path = "C:/Users/liams/ArchScan_Capture_Project/color_image_detection/test_folder/ls/archSCAN_logo.png"

    # Check if the file exists
    if not os.path.isfile(logo_path):
        print(f"Error: Logo image file not found at the specified path: {logo_path}")
        root.destroy()
        return

    # Load logo image using Pillow
    try:
        logo_image = Image.open(logo_path)
        print(f"Successfully loaded image: {logo_path}")
    except Exception as e:
        print(f"Error loading image: {e}")
        root.destroy()
        return

    # Optionally, resize the image
    desired_width = 200
    w_percent = (desired_width / float(logo_image.size[0]))
    h_size = int((float(logo_image.size[1]) * float(w_percent)))
    #logo_image = logo_image.resize((desired_width, h_size), Image.ANTIALIAS)
    print(f"Resized image to: {desired_width}x{h_size}")

    # Convert the Image object into a TkPhoto object
    try:
        logo_photo = ImageTk.PhotoImage(logo_image)
        print("Image converted to PhotoImage successfully.")
    except Exception as e:
        print(f"Error converting image to PhotoImage: {e}")
        root.destroy()
        return

    # Create a label to hold the logo image
    try:
        logo_label = tk.Label(root, image=logo_photo, bg='white')
        logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
        logo_label.pack(pady=50)
        print("Logo label created and packed successfully.")
    except Exception as e:
        print(f"Error creating or packing the logo label: {e}")
        root.destroy()
        return

    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
