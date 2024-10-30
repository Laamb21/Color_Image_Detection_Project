'''
Test to connect welcome screen to upload screen
'''

#Import libraries
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("JPG TIF Processor")
        self.root.geometry("600x600")

        #Initialize variables
        self.parent_folder = tk.StringVar()
        
        #Function call to create header
        self.create_header()

        #Function call to create welcome state
        self.create_welcome_state()

    def create_header(self):
        #Create header frame
        header_frame = tk.Frame(self.root, bg='#4a90e3', height=160)
        header_frame.pack(fill='x')

        #Define logo path
        logo_path = "C:/Users/liams/ArchScan_Capture_Project/color_image_detection/archSCAN_logo.png"

        #Check if file for logo exists 
        if not os.path.isfile(logo_path):
            print(f"Error: Logo image file not found at specified file path: {logo_path}")
            return
        
        #Load logo image using Pillow library
        try:
            logo_image = Image.open(logo_path).convert("RGBA")
            print(f"Successfully loaded image: {logo_path}")
        except Exception as e:
            print(f"Error loading image: {e}")
            return
        
        #Resize image
        width = 200
        width_percentage = (width / float(logo_image.size[0]))
        height_size = int((float(logo_image.size[1]) * float(width_percentage)))
        print(f"Resized image to: {width} x { height_size}")

        #Convert Image object into TkPhoto object 
        try:
            logo_photo = ImageTk.PhotoImage(logo_image)
            print("Image converted to PhotoImage successfully.")
        except Exception as e:
            print(f"Error converting Image to PhotoImage: {e}")
            return
        
        #Create label to hold logo image
        try:
            logo_label = tk.Label(header_frame, image=logo_photo)
            logo_label.image = logo_photo
            logo_label.pack(pady=50)
            print("Logo label created and packed successfully")
        except Exception as e:
            print(f"Error creating or packing the logo label: {e}")
            return
        
    def create_welcome_state(self):
        #Create "Welcome!" label
        welcome_label = tk.Label(self.root, text="Welcome to the \nJPG and TIF Processor!", font=("Merriweather", 36, "bold"))
        welcome_label.pack(pady=50)

        #Create "Get Started" button
        get_started_button = tk.Button(self.root, text="Get Started", bg="#4a90e3", fg='white', padx=50, pady=20, font=("Merriweather", 20, "bold"), command=self.create_upload_state)
        get_started_button.pack(pady=20)

    def create_upload_state(self):
        #Create "Upload Set" label
        upload_set_label = tk.Label(self.root, text="Upload Set (set must contain \n'JPG' and 'TIF' folders)", font=("Merriweather", 36, "bold"))
        upload_set_label.pack(pady=50)

        #Create upload entry
        upload_set_entry = tk.Entry(self.root, textvariable=self.parent_folder)
        upload_set_entry.pack(pady=20)

        #Create upload button
        upload_set_button = tk.Button(self.root, text="Upload", bg="#4a90e3", fg='white', padx=50, pady=20, font=("Merriweather", 20, "bold"))        

def main():    
    # Initialize and run the GUI
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()