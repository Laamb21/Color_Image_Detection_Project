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

import csv  # Needed for parsing the TSV log file
import shutil  # Needed for copying files

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("JPG and TIFF Processor")
        self.root.geometry("800x600")
        
        # Initialize variables
        self.parent_folder = tk.StringVar()
        self.low_threshold = tk.DoubleVar(value=10.0)   # Default low threshold
        self.high_threshold = tk.DoubleVar(value=15.0)  # Default high threshold
        self.processing_thread = None
        self.progress_queue = queue.Queue()
        
        # List to keep track of flagged files
        self.flagged_files = []
        
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
        # Adding validation to ensure only numeric input
        vcmd = (self.root.register(self.validate_threshold), '%P')
        ttk.Entry(threshold_frame, textvariable=self.low_threshold, width=10, validate='key', validatecommand=vcmd).pack(side='left', padx=(0,15))
        
        ttk.Label(threshold_frame, text="High Gray Threshold (%):").pack(side='left', padx=(0,5))
        ttk.Entry(threshold_frame, textvariable=self.high_threshold, width=10, validate='key', validatecommand=vcmd).pack(side='left')
        
        # ---------------------------- Run Button ---------------------------- #
        run_frame = ttk.Frame(self.root)
        run_frame.pack(padx=10, pady=10, fill='x')
        
        self.run_button = ttk.Button(run_frame, text="Run Script", command=self.run_script)
        self.run_button.pack(side='left')
        
        # ---------------------------- Progress Bar ---------------------------- #
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(padx=10, pady=10, fill='x')
        
        self.progress = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate')
        self.progress.pack(fill='x', expand=True)
        
        # Adding a label to show percentage
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.pack(pady=(5,0))
        
        # ---------------------------- Log Display ---------------------------- #
        log_frame = ttk.Frame(self.root)
        log_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled')
        self.log_text.pack(fill='both', expand=True)
        
        # ---------------------------- Open Log Buttons ---------------------------- #
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(padx=10, pady=10, fill='x')
        
        self.open_tsv_button = ttk.Button(buttons_frame, text="Open TSV Log", command=self.open_tsv_log_file, state='disabled')
        self.open_tsv_button.pack(side='left', padx=(0,5))
        
        self.open_excel_button = ttk.Button(buttons_frame, text="Open Excel Log", command=self.open_excel_log_file, state='disabled')
        self.open_excel_button.pack(side='left')
        
        # ---------------------------- Download Flagged Files Button ---------------------------- #
        self.download_flagged_button = ttk.Button(buttons_frame, text="Download Flagged Files", command=self.download_flagged_files, state='disabled')
        self.download_flagged_button.pack(side='left', padx=(5,0))
    
    def validate_threshold(self, P):
        """Validate that the input is a valid float."""
        if P == "":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False
    
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.parent_folder.set(folder_selected)
    
    def run_script(self):
        if not self.parent_folder.get():
            messagebox.showerror("Error", "Please select a parent folder.")
            return
        
        # Validate that low_threshold is less than high_threshold
        if self.low_threshold.get() >= self.high_threshold.get():
            messagebox.showerror("Error", "Low threshold must be less than High threshold.")
            return
        
        # Disable the Run button to prevent multiple runs
        self.run_button.config(state='disabled')
        
        # Clear previous logs
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        
        # Initialize progress
        self.progress['value'] = 0
        self.progress['maximum'] = 100  # Will be updated dynamically
        self.progress_label.config(text="0%")
        
        # Reset flagged files list
        self.flagged_files = []
        self.download_flagged_button.config(state='disabled')  # Disable until processing is complete
        
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
                        self.progress_label.config(text=f"{progress_value:.2f}%")
                elif message[0] == "error":
                    self.log_text.configure(state='normal')
                    self.log_text.insert(tk.END, f"Error: {message[1]}\n")
                    self.log_text.configure(state='disabled')
                    messagebox.showerror("Error", message[1])
                elif message[0] == "complete":
                    self.log_text.configure(state='normal')
                    self.log_text.insert(tk.END, f"{message[1]}\nFlagged Files Count: {message[2]}\n")
                    self.log_text.configure(state='disabled')
                    messagebox.showinfo("Complete", f"{message[1]}\nFlagged Files Count: {message[2]}")
                    
                    # Enable the Open Log Buttons
                    self.open_tsv_button.config(state='normal')
                    self.open_excel_button.config(state='normal')
                    
                    # Enable the Download Flagged Files Button
                    self.download_flagged_button.config(state='normal')
                    
                    # Re-enable the Run button
                    self.run_button.config(state='normal')
                    
                    # Populate the flagged_files list by reading the TSV log
                    self.populate_flagged_files()
                    
        except queue.Empty:
            pass
        if self.processing_thread.is_alive():
            self.root.after(100, self.process_queue)
    
    def populate_flagged_files(self):
        """Reads the TSV log file and populates the flagged_files list."""
        log_file_tsv = os.path.join(self.parent_folder.get(), "selection_log.tsv")
        input_dir_jpg = os.path.join(self.parent_folder.get(), "JPG")
        
        if not os.path.exists(log_file_tsv):
            messagebox.showerror("Error", "TSV log file not found.")
            return
        
        try:
            with open(log_file_tsv, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile, delimiter='\t')
                for row in reader:
                    if row['Selected_Format'] == "JPG (Intermediate)":
                        document = row['Document']
                        # Reconstruct the filename (assuming .jpg extension)
                        # If the original filename had different extensions, adjust accordingly
                        possible_extensions = ['.jpg', '.jpeg']
                        for ext in possible_extensions:
                            filename = document + ext
                            filepath = os.path.join(input_dir_jpg, filename)
                            if os.path.exists(filepath):
                                self.flagged_files.append(filepath)
                                break
                        else:
                            # If none of the extensions matched, notify the user
                            self.log_text.configure(state='normal')
                            self.log_text.insert(tk.END, f"Flagged file '{document}' not found with extensions .jpg or .jpeg.\n")
                            self.log_text.configure(state='disabled')
            if not self.flagged_files:
                self.log_text.configure(state='normal')
                self.log_text.insert(tk.END, "No flagged files found.\n")
                self.log_text.configure(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read TSV log file: {str(e)}")
    
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
    
    def download_flagged_files(self):
        if not self.flagged_files:
            messagebox.showinfo("No Flagged Files", "There are no flagged files to download.")
            return
        
        destination_folder = filedialog.askdirectory()
        if not destination_folder:
            return  # User cancelled the dialog
        
        # Start copying in a separate thread to keep GUI responsive
        copy_thread = threading.Thread(target=self.copy_flagged_files, args=(destination_folder,))
        copy_thread.start()
    
    def copy_flagged_files(self, destination_folder):
        copied_count = 0
        failed_files = []
        
        for filepath in self.flagged_files:
            try:
                shutil.copy2(filepath, destination_folder)
                copied_count += 1
            except Exception as e:
                failed_files.append((filepath, str(e)))
        
        # Notify the user upon completion
        if failed_files:
            error_messages = "\n".join([f"{os.path.basename(f[0])}: {f[1]}" for f in failed_files])
            message = f"Copied {copied_count} flagged files successfully.\nFailed to copy {len(failed_files)} files:\n{error_messages}"
            messagebox.showwarning("Download Completed with Errors", message)
        else:
            message = f"All {copied_count} flagged files were copied successfully."
            messagebox.showinfo("Download Completed", message)
    
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
