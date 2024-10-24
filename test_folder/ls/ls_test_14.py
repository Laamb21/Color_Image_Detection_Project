'''
Test to implement screen transition
States to add:
    Welcome (initial)
    Upload (user uploads file path)
    Threshold (user adjusts threshold)
    Verify Input(user is able to verify file path and thresholds before running script)
    Run (progress bar to indicate script is running)
    Results (shows how many files were flagged, logs available for download)
    Verify Output(user selected which flagged files to select, can download folder when done)
'''

#Import libraries
import queue
import tkinter as tk
from tkinter import ttk

class App():
    def __init__(self, root):
        self.root = root
        self.root.title("JPG and TIFF Processor ")
        self.root.geometry("600x600")

        #Initialize variables
        self.parent_folder = tk.StringVar()                 
        self.low_threshold = tk.DoubleVar(value = 10.0)     #Default low threshold
        self.high_threshold = tk.DoubleVar(value = 15.0)    #Default high threshold
        self.processing_thread = None
        self.process_queue = queue.Queue()

        #Initialize lists
        self.flagged_files = []     #List to keep track of flagged files
        self.selected_files = []    #List to keep track of selected files
        self.log_entries = []       #List to store log data

        #Define all possible states
        self.STATE_WELCOME = "welcome"
        self.STATE_UPLOAD = "upload"
        self.STATE_THRESHOLD = "threshold"
        self.STATE_VERIFY_INPUT = "verify_input"
        self.STATE_RUN = "run"
        self.STATE_RESULTS = "results"
        self.STATE_VERIFY_OUTPUT = "verify_output"

        #Store states in an array
        self.states = [self.STATE_WELCOME, 
                       self.STATE_UPLOAD, 
                       self.STATE_THRESHOLD, 
                       self.STATE_VERIFY_INPUT,
                       self.STATE_RUN,
                       self.STATE_RESULTS,
                       self.STATE_VERIFY_OUTPUT]

        #Initialize current state
        self.current_state = 0

        #Container for state frames 
        self.container = ttk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        

