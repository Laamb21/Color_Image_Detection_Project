'''
Gui file for welcome screen
'''

#Import libraries 
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

#Import additional GUI files
from upload_gui import create_upload_window
    

def create_welcome_window(self):
    #Create "Welcome!" label
    welcome_label = tk.Label(self.root, text="Welcome to the \nJPG and TIF Processor!", font=("Merriweather", 36, "bold"))
    welcome_label.pack(pady=50)

    #Create "Get Started" button
    get_started_button = tk.Button(self.root, 
                                   text="Get Started!",
                                   bg="#4a90e2", 
                                   fg="white", 
                                   padx=50, 
                                   pady=20, 
                                   font=("Merriweather", 20, "bold"),
                                   command= lambda: create_upload_window)
    get_started_button.pack(pady=20)

