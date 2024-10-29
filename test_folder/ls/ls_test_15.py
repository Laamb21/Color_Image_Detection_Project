'''
Test file to create Welcome screen for GUI
'''

#Import libraries
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os 


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        #Configure main window 
        self.title("JPG TIF Processor")
        self.geometry("600x600")
        self.configure(bg='white')

        #Create header
        self.create_header()

    def create_header(self):
        #Create frame for the header
        header_frame = ttk.Frame(self, style='Header.TFrame')
        header_frame.pack(fill='x')

        #Define logo path
        logo_path = "C:/Users/liams/ArchScan_Capture_Project/color_image_detection/test_folder/ls/archSCAN_logo.png"

        #Load logo image using Pillow
        try:
            logo_image = Image.open(logo_path)
            print(f"Successfully loaded image: {logo_path}")
        except Exception as e:
            print(f"Error loading image: {e}")
            return 

        #Convert Image object into TkPhoto object
        try:
            logo_photo = ImageTk.PhotoImage(logo_image)
            print("Image converted to PhotoImage successfully")
        except Exception as e:
            print(f"Error converting image to PhotoImage: {e}")
            return

        #Create label to hold logo image
        try:
            logo_label = tk.Label(header_frame, image=logo_photo, bg='white')
            logo_label.image = logo_photo
            logo_label.pack(pady=50)
            print("Logo label created and packed successfully")
        except Exception as e:
            print(f"Error creating and/or packing logo label: {e}")
            return

def main():
    # Define styles
    style = ttk.Style()
    style.configure('Header.TFrame', background='white')  # Set header frame background to white

    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()