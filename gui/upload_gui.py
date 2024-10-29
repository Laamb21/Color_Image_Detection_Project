'''
Gui for upload screen
'''

#Import libraries 
import tkinter as tk
from tkinter import ttk

def create_upload_window(self):
    #Create "Upload Set" label
    upload_set_label = tk.Label(self.root, text='Uplaod Set (set must contain \n"JPG" and "TIF" folders)', font=('Merriweather', 36, "bold"))
    upload_set_label.pack(pady=50)

    #Create upload entry
    upload_set_entry = tk.Entry(self.root, textvariable=self.parent_folder)
    upload_set_entry.pack(pady=20)

    #Create upload button
    upload_set_button = tk.Button(self.root, text="Upload ", bg="#4a90e2", fg="white", padx=50, pady=20, font=("Merriweather", 20, "bold"))
    upload_set_button.pack(pady=20)