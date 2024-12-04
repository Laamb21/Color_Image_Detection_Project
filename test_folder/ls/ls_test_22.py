#Test code for file upload ui

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class FolderUploadUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multiple Folder Upload")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        # Frame for the buttons
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10)

        # Button to select folders
        self.select_button = ttk.Button(self.button_frame, text="Select Folder", command=self.select_folder)
        self.select_button.grid(row=0, column=0, padx=10)

        # Button to remove selected folders
        self.remove_button = ttk.Button(self.button_frame, text="Remove Selected", command=self.remove_selected, state='disabled')
        self.remove_button.grid(row=0, column=1, padx=10)

        # Button to upload folders
        self.upload_button = ttk.Button(self.button_frame, text="Upload Folders", command=self.upload_folders, state='disabled')
        self.upload_button.grid(row=0, column=2, padx=10)

        # Label for the listbox
        self.list_label = ttk.Label(self.root, text="Selected Folders:")
        self.list_label.pack(anchor='w', padx=20)

        # Frame for the listbox and scrollbar
        self.list_frame = ttk.Frame(self.root)
        self.list_frame.pack(padx=20, pady=10, fill='both', expand=True)

        # Scrollbar for the listbox
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox to display selected folders
        self.folder_listbox = tk.Listbox(
            self.list_frame,
            selectmode=tk.MULTIPLE,
            yscrollcommand=self.scrollbar.set,
            width=70,
            height=15
        )
        self.folder_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.folder_listbox.yview)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress.pack(pady=10)

        # Initialize folder list
        self.folders = []

        # Bind selection event to enable/disable remove button
        self.folder_listbox.bind('<<ListboxSelect>>', self.on_select)

    def select_folder(self):
        # Open directory dialog to select a folder
        selected_folder = filedialog.askdirectory(
            title="Select Folder",
        )
        if selected_folder:
            if selected_folder not in self.folders:
                self.folders.append(selected_folder)
                self.folder_listbox.insert(tk.END, selected_folder)
                self.upload_button.config(state='normal')
            else:
                messagebox.showinfo("Duplicate Folder", "The selected folder is already in the list.")

    def remove_selected(self):
        selected_indices = list(self.folder_listbox.curselection())
        if not selected_indices:
            return
        for index in reversed(selected_indices):
            self.folder_listbox.delete(index)
            del self.folders[index]
        if not self.folders:
            self.upload_button.config(state='disabled')
        self.remove_button.config(state='disabled')

    def upload_folders(self):
        if not self.folders:
            messagebox.showwarning("No Folders", "Please select folders to upload.")
            return

        # Example upload action with progress bar
        self.upload_button.config(state='disabled')
        self.select_button.config(state='disabled')
        self.remove_button.config(state='disabled')
        self.progress['maximum'] = len(self.folders)
        self.progress['value'] = 0

        for idx, folder in enumerate(self.folders, start=1):
            # Simulate upload delay
            self.root.update_idletasks()
            self.root.after(100)  # Replace with actual upload code
            self.progress['value'] = idx
            self.root.update_idletasks()

            # Example: Print folder path (replace with actual upload logic)
            print(f"Uploaded folder: {folder}")

        messagebox.showinfo("Upload Successful", f"Uploaded {len(self.folders)} folders.")
        # Reset the UI
        self.folder_listbox.delete(0, tk.END)
        self.folders = []
        self.upload_button.config(state='disabled')
        self.select_button.config(state='normal')
        self.progress['value'] = 0

    def on_select(self, event):
        selected = self.folder_listbox.curselection()
        if selected:
            self.remove_button.config(state='normal')
        else:
            self.remove_button.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderUploadUI(root)
    root.mainloop()


'''
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class FileUploadUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multiple File Upload")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # Frame for the buttons
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=20)

        # Button to select files
        self.select_button = ttk.Button(self.button_frame, text="Select Files", command=self.select_files)
        self.select_button.grid(row=0, column=0, padx=10)

        # Button to upload files
        self.upload_button = ttk.Button(self.button_frame, text="Upload Files", command=self.upload_files, state='disabled')
        self.upload_button.grid(row=0, column=1, padx=10)

        # Label for the listbox
        self.list_label = ttk.Label(self.root, text="Selected Files:")
        self.list_label.pack(anchor='w', padx=20)

        # Frame for the listbox and scrollbar
        self.list_frame = ttk.Frame(self.root)
        self.list_frame.pack(padx=20, pady=10, fill='both', expand=True)

        # Scrollbar for the listbox
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox to display selected files
        self.file_listbox = tk.Listbox(
            self.list_frame,
            selectmode=tk.MULTIPLE,
            yscrollcommand=self.scrollbar.set,
            width=60,
            height=15
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.file_listbox.yview)

        # Initialize file list
        self.files = []

    def select_files(self):
        # Open file dialog to select multiple files
        selected_files = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=(("All Files", "*.*"), ("Text Files", "*.txt"), ("Images", "*.png;*.jpg;*.jpeg;*.gif"))
        )
        if selected_files:
            # Clear the current list
            self.file_listbox.delete(0, tk.END)
            self.files = list(selected_files)
            for file in self.files:
                self.file_listbox.insert(tk.END, file)
            self.upload_button.config(state='normal')
        else:
            self.upload_button.config(state='disabled')

    def upload_files(self):
        if not self.files:
            messagebox.showwarning("No Files", "Please select files to upload.")
            return

        # Example upload action: display file paths
        # Replace this with actual upload logic (e.g., to a server)
        uploaded_files = "\n".join(self.files)
        messagebox.showinfo("Upload Successful", f"Uploaded {len(self.files)} files:\n{uploaded_files}")

        # Optionally, clear the list after upload
        self.file_listbox.delete(0, tk.END)
        self.files = []
        self.upload_button.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = FileUploadUI(root)
    root.mainloop()
'''
