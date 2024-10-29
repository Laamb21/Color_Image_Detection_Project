'''
Test file to create Welcome screen for GUI
'''

#Import libraries
import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import os 


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        #Configure main window 
        self.title = ("JPG TIF Processor")
        self.geometry = ("600x600")
        self.configure(bg='white')

        #Create header
        self.create_header()

    def create_header(self):
        #Create frame for the header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x')

        #Set header frame background color to light blue 
        header_frame.configure(style="Header.TFrame") 

        #Define logo path
        logo_path = r"C:/Users/liams/ArchScan_Capture_Project/color_image_detection/test_folder/ls/archSCAN_logo.png"

        #Load logo image using Pillow
        try:
            logo_image = Image.open(logo_path)
        except FileNotFoundError as e:
            print(f"Error: Logo image file not found at the specified path: {logo_path}")
            print(e)
            return
        except Exception as e:
            print(f"An unexpected error has occured while loading the image: {e}")
            return 

        #Convert Image object into TkPhoto object
        logo_photo = ImageTk.PhotoImage(Image.open(logo_path))

        #Create label to hold logo image
        logo_label = tk.Label(header_frame, image=logo_photo, background='white')
        logo_label.pack(pady=10)  


def main():
    # Define styles
    style = ttk.Style()
    style.configure('Header.TFrame', background='white')  # Set header frame background to white

    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()