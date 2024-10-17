# gui.py

import os
import sys
import subprocess
import threading
import queue
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, scrolledtext, messagebox

from processing import process_documents

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("JPG and TIFF Processor")
        self.root.geometry("800x700")
        
        # Initialize variables
        self.parent_folder = tk.StringVar()
        self.low_threshold = tk.DoubleVar(value=10.0)   # Default low threshold
        self.high_threshold = tk.DoubleVar(value=15.0)  # Default high threshold
        self.processing_thread = None
        self.progress_queue = queue.Queue()
        
        # Create GUI components
        self.create_widgets()
    
    def create_widgets(self):
        # ---------------------------- Folder Selection ---------------------------- #
        folder_frame = ttk.Frame(self.root)
        folder_frame.pack(padx=10, pady=10, fill='x')
        
        ttk.Label(folder_frame, text="Parent Folder:").pack(side='left', padx=(0,5))
        ttk.Entry(folder_frame, textvariable=self.parent_folder, width=50).pack(side='left', fill='x', expand=True)
        ttk.Button(folder_frame, text="Select Folder", command=self.select_folder).pack(side='left', padx=(5,0))
        
        # ---------------------------- Thresholds ---------------------------- #
        threshold_frame = ttk.Frame(self.root)
        threshold_frame.pack(padx=10, pady=5, fill='x')
        
        ttk.Label(threshold_frame, text="Low Gray Threshold (%):").pack(side='left', padx=(0,5))
        ttk.Entry(threshold_frame, textvariable=self.low_threshold, width=10).pack(side='left', padx=(0,15))
        
        ttk.Label(threshold_frame, text="High Gray Threshold (%):").pack(side='left', padx=(0,5))
        ttk.Entry(threshold_frame, textvariable=self.high_threshold, width=10).pack(side='left')
        
        # ---------------------------- Run Button ---------------------------- #
        run_frame = ttk.Frame(self.root)
        run_frame.pack(padx=10, pady=10, fill='x')
        
        ttk.Button(run_frame, text="Run Script", command=self.run_script).pack(side='left')
        
        # ---------------------------- Progress Bar ---------------------------- #
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(padx=10, pady=10, fill='x')
        
        self.progress = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate')
        self.progress.pack(fill='x', expand=True)
        
        # ---------------------------- Log Display ---------------------------- #
        log_frame = ttk.Frame(self.root)
        log_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled')
        self.log_text.pack(fill='both', expand=True)
        
        # ---------------------------- Open Log Buttons ---------------------------- #
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(padx=10, pady=10, fill='x')
        
        ttk.Button(buttons_frame, text="Open TSV Log", command=self.open_tsv_log_file).pack(side='left', padx=(0,5))
        ttk.Button(buttons_frame, text="Open Excel Log", command=self.open_excel_log_file).pack(side='left')
    
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.parent_folder.set(folder_selected)
    
    def run_script(self):
        if not self.parent_folder.get():
            messagebox.showerror("Error", "Please select a parent folder.")
            return
        
        # Disable the Run button to prevent multiple runs
        for widget in self.root.pack_slaves():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child['text'] == "Run Script":
                        child.config(state='disabled')
        
        # Clear previous logs
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        
        # Initialize progress
        self.progress['value'] = 0
        self.progress['maximum'] = 100  # Will be updated dynamically
        
        # Start the processing in a separate thread
        self.processing_thread = threading.Thread(
            target=self.process,
            args=()
        )
        self.processing_thread.start()
        
        # Start polling the queue
        self.root.after(100, self.process_queue)
    
    def process(self):
        input_dir_jpg = os.path.join(self.parent_folder.get(), "JPG")
        input_dir_tiff = os.path.join(self.parent_folder.get(), "TIF")
        log_file_tsv = os.path.join(self.parent_folder.get(), "selection_log.tsv")
        log_file_xlsx = os.path.join(self.parent_folder.get(), "selection_log.xlsx")
        
        # Call the processing function
        process_documents(
            input_dir_jpg,
            input_dir_tiff,
            log_file_tsv,
            log_file_xlsx,
            self.progress_queue,
            self.low_threshold.get(),
            self.high_threshold.get()
        )
    
    def process_queue(self):
        try:
            while True:
                message = self.progress_queue.get_nowait()
                if message[0] == "current_file":
                    self.log_text.configure(state='normal')
                    self.log_text.insert(tk.END, f"Processing: {message[1]}\n")
                    self.log_text.configure(state='disabled')
                elif message[0] == "progress":
                    processed, total = message[1], message[2]
                    if total > 0:
                        progress_value = (processed / total) * 100
                        self.progress['value'] = progress_value
                elif message[0] == "error":
                    self.log_text.configure(state='normal')
                    self.log_text.insert(tk.END, f"Error: {message[1]}\n")
                    self.log_text.configure(state='disabled')
                    messagebox.showerror("Error", message[1])
                elif message[0] == "complete":
                    self.log_text.configure(state='normal')
                    self.log_text.insert(tk.END, f"{message[1]}\nFlagged Files Count: {message[2]}\n")
                    self.log_text.configure(state='disabled')
                    messagebox.showinfo("Complete", message[1])
                    
                    # Load the logs into the GUI
                    self.load_log()
                    
                    # Re-enable the Run button
                    for widget in self.root.pack_slaves():
                        if isinstance(widget, ttk.Frame):
                            for child in widget.winfo_children():
                                if isinstance(child, ttk.Button) and child['text'] == "Run Script":
                                    child.config(state='normal')
        except queue.Empty:
            pass
        if self.processing_thread.is_alive():
            self.root.after(100, self.process_queue)
    
    def load_log(self):
        # Functionality to load log content can be implemented here if needed
        pass
    
    def open_tsv_log_file(self):
        log_file_tsv = os.path.join(self.parent_folder.get(), "selection_log.tsv")
        if os.path.exists(log_file_tsv):
            self.open_file(log_file_tsv)
        else:
            messagebox.showerror("Error", "TSV log file not found.")
    
    def open_excel_log_file(self):
        log_file_xlsx = os.path.join(self.parent_folder.get(), "selection_log.xlsx")
        if os.path.exists(log_file_xlsx):
            self.open_file(log_file_xlsx)
        else:
            messagebox.showerror("Error", "Excel log file not found.")
    
    def open_file(self, filepath):
        try:
            if sys.platform.startswith('darwin'):
                subprocess.call(['open', filepath])
            elif os.name == 'nt':
                os.startfile(filepath)
            elif os.name == 'posix':
                subprocess.call(['xdg-open', filepath])
            else:
                messagebox.showerror("Unsupported OS", "Cannot open log file on this operating system.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open log file: {str(e)}")
