# main.py

import tkinter as tk
from gui import App
from logging_setup import setup_logging

def main():
    # Setup logging
    setup_logging()
    
    # Initialize and run the GUI
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
