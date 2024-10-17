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
        self.root.title("JPG TIF Selection Script")
        self.root.geometry("900x700")  # Increased width for better visibility
        
        # Configure grid weights to make the GUI responsive
        self.root.grid_rowconfigure(7, weight=1)  # Log Text
        self.root.grid_columnconfigure(1, weight=1)
        
        # Queue for thread communication
        self.progress_queue = queue.Queue()
        
        # Header
        header = ttk.Label(root, text="JPG TIF Selection Script", font=("Helvetica", 16))
        header.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky='w')
        
        # Folder Selection Frame
        folder_frame = ttk.Frame(root)
        folder_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky='ew')
        folder_frame.grid_columnconfigure(1, weight=1)
        
        # Store reference to the Select Folder button
        self.select_button = ttk.Button(folder_frame, text="Select Folder", command=self.select_folder)
        self.select_button.grid(row=0, column=0, padx=(0,10), pady=5, sticky='w')
        
        self.selected_folder = tk.StringVar()
        folder_label = ttk.Label(folder_frame, textvariable=self.selected_folder, foreground="blue")
        folder_label.grid(row=0, column=1, sticky='w')
        
        # ---------------------------- Threshold Adjustments ---------------------------- #
        threshold_frame = ttk.Frame(root)
        threshold_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky='ew')
        threshold_frame.grid_columnconfigure(1, weight=1)
        threshold_frame.grid_columnconfigure(3, weight=1)
        
        # Low Gray Threshold
        low_threshold_label = ttk.Label(threshold_frame, text="Low Gray Threshold (%)")
        low_threshold_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        
        self.low_threshold_var = tk.DoubleVar(value=10)  # Default value
        low_threshold_entry = ttk.Entry(threshold_frame, textvariable=self.low_threshold_var, width=10)
        low_threshold_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # High Gray Threshold
        high_threshold_label = ttk.Label(threshold_frame, text="High Gray Threshold (%)")
        high_threshold_label.grid(row=0, column=2, padx=5, pady=5, sticky='e')
        
        self.high_threshold_var = tk.DoubleVar(value=15)  # Default value
        high_threshold_entry = ttk.Entry(threshold_frame, textvariable=self.high_threshold_var, width=10)
        high_threshold_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        # Run Button
        self.run_button = ttk.Button(root, text="Run Script", command=self.run_script)
        self.run_button.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky='ew')
        
        # Progress Frame
        progress_frame = ttk.Frame(root)
        progress_frame.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky='ew')
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky='ew')
        
        # Progress Percentage Label
        self.progress_percentage_var = tk.StringVar(value="0%")
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_percentage_var)
        progress_label.grid(row=0, column=1, padx=(10,0), sticky='e')
        
        # Current File Label
        self.current_file_var = tk.StringVar(value="No file being processed.")
        current_file_label = ttk.Label(root, textvariable=self.current_file_var, foreground="green")
        current_file_label.grid(row=5, column=0, columnspan=2, pady=5, padx=10, sticky='w')
        
        # Text Window for selection_log.tsv and selection_log.xlsx
        log_label = ttk.Label(root, text="Selection Log (TSV & Excel):")
        log_label.grid(row=6, column=0, columnspan=2, pady=(20, 0), padx=10, sticky='w')
        
        self.log_text = scrolledtext.ScrolledText(root, width=100, height=20, state='disabled')
        self.log_text.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        
        # Status Label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(root, textvariable=self.status_var, foreground="green")
        self.status_label.grid(row=8, column=0, columnspan=2, pady=5, padx=10, sticky='w')
        
        # Open Log File Button
        self.open_log_button = ttk.Button(root, text="Open Log File", command=self.open_log_file)
        self.open_log_button.grid(row=9, column=0, columnspan=2, pady=10, padx=10, sticky='ew')
        
        # Initialize variables
        self.parent_folder = ""
        
        # Periodically check the queue
        self.root.after(100, self.process_queue)
    
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.parent_folder = folder_selected
            self.selected_folder.set(folder_selected)
    
    def run_script(self):
        if not self.parent_folder:
            messagebox.showwarning("No Folder Selected", "Please select a folder before running the script.")
            return
        
        # Retrieve threshold values from the GUI
        try:
            low_threshold = float(self.low_threshold_var.get())
            high_threshold = float(self.high_threshold_var.get())
            if low_threshold < 0 or high_threshold < 0:
                raise ValueError("Thresholds must be non-negative.")
            if low_threshold >= high_threshold:
                raise ValueError("Low Gray Threshold must be less than High Gray Threshold.")
        except ValueError as ve:
            messagebox.showerror("Invalid Thresholds", f"Please enter valid threshold values.\nError: {ve}")
            return
        
        # Define input directories based on the parent folder
        input_dir_jpg = os.path.join(self.parent_folder, "JPG")
        input_dir_tiff = os.path.join(self.parent_folder, "TIF")  # Ensure folder is named "TIF"
        log_file_tsv = os.path.join(self.parent_folder, "selection_log.tsv")
        log_file_xlsx = os.path.join(self.parent_folder, "selection_log.xlsx")
        
        # Check if input directories exist
        if not os.path.isdir(input_dir_jpg):
            messagebox.showerror("Invalid Directory", f"JPG directory not found: {input_dir_jpg}")
            return
        if not os.path.isdir(input_dir_tiff):
            messagebox.showerror("Invalid Directory", f"TIF directory not found: {input_dir_tiff}")
            return
        
        # Disable only the select, run, and open log buttons to prevent multiple runs
        self.select_button.configure(state='disabled')
        self.run_button.configure(state='disabled')
        self.open_log_button.configure(state='disabled')
        
        # Reset progress bar and current file label
        self.progress_var.set(0)
        self.progress_percentage_var.set("0%")
        self.current_file_var.set("Starting processing...")
        
        # Update status
        self.status_var.set("Processing...")
        
        # Start the processing in a separate thread
        processing_thread = threading.Thread(
            target=process_documents, 
            args=(
                input_dir_jpg, 
                input_dir_tiff, 
                log_file_tsv, 
                log_file_xlsx, 
                self.progress_queue, 
                low_threshold, 
                high_threshold
            )
        )
        processing_thread.start()
    
    def process_queue(self):
        try:
            while True:
                message = self.progress_queue.get_nowait()
                if message[0] == "progress":
                    processed, total = message[1], message[2]
                    percentage = (processed / total) * 100
                    self.progress_var.set(percentage)
                    self.progress_percentage_var.set(f"{percentage:.2f}%")
                elif message[0] == "complete":
                    self.status_var.set(message[1])
                    flagged_count = message[2]
                    self.load_log()
                    # Re-enable only the select, run, and open log buttons
                    self.select_button.configure(state='normal')
                    self.run_button.configure(state='normal')
                    self.open_log_button.configure(state='normal')
                    # Display the flagged count in the GUI
                    messagebox.showinfo(
                        "Processing Complete", 
                        f"{message[1]}\nFlagged Files Count: {flagged_count}"
                    )
                    # Reset current file label
                    self.current_file_var.set("Processing complete.")
                elif message[0] == "error":
                    self.status_var.set(message[1])
                    messagebox.showerror("Error", message[1])
                    # Re-enable only the select, run, and open log buttons
                    self.select_button.configure(state='normal')
                    self.run_button.configure(state='normal')
                    self.open_log_button.configure(state='normal')
                    # Reset current file label
                    self.current_file_var.set("Error encountered.")
                elif message[0] == "current_file":
                    current_file = message[1]
                    self.current_file_var.set(f"Processing: {current_file}")
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)
    
    def load_log(self):
        # Load TSV content into the ScrolledText widget
        log_file_tsv = os.path.join(self.parent_folder, "selection_log.tsv")
        if os.path.exists(log_file_tsv):
            with open(log_file_tsv, 'r') as file:
                content_tsv = file.read()
            self.log_text.configure(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, "----- TSV Log -----\n")
            self.log_text.insert(tk.END, content_tsv + "\n\n")
        else:
            self.log_text.configure(state='normal')
            self.log_text.insert(tk.END, "TSV Log file not found.\n\n")
        
        # Load Excel content as a table-like string
        log_file_xlsx = os.path.join(self.parent_folder, "selection_log.xlsx")
        if os.path.exists(log_file_xlsx):
            try:
                from openpyxl import load_workbook
                wb = load_workbook(log_file_xlsx)
                ws = wb.active
                content_xlsx = "----- Excel Log -----\n"
                for row in ws.iter_rows(values_only=True):
                    row_data = "\t".join([str(cell) if cell is not None else "" for cell in row])
                    content_xlsx += row_data + "\n"
                self.log_text.insert(tk.END, content_xlsx)
            except Exception as e:
                self.log_text.insert(tk.END, f"Failed to read Excel log file: {str(e)}")
        else:
            self.log_text.insert(tk.END, "Excel Log file not found.\n")
        
        self.log_text.configure(state='disabled')
    
    def open_log_file(self):
        # Open both TSV and Excel log files
        log_file_tsv = os.path.join(self.parent_folder, "selection_log.tsv")
        log_file_xlsx = os.path.join(self.parent_folder, "selection_log.xlsx")
        
        # Function to open a file based on OS
        def open_file(filepath):
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
        
        # Check and open TSV file
        if os.path.exists(log_file_tsv):
            open_file(log_file_tsv)
        else:
            messagebox.showerror("Error", "TSV log file not found.")
        
        # Check and open Excel file
        if os.path.exists(log_file_xlsx):
            open_file(log_file_xlsx)
        else:
            messagebox.showerror("Error", "Excel log file not found.")
