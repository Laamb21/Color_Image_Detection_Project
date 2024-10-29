'''
Main GUI file to hold all window instances
'''

#Import libraries
import tkinter as tk
from tkinter import ttk
from PIL import Image

#Import additional GUI windows 
from welcome_gui import create_welcome_window

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("JPG TIF Processor")
        self.root.geometry("600x600")

        #Function call to create header
        create_welcome_window(self)



def main():    
    # Initialize and run the GUI
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
