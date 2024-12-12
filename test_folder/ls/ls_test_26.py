import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from PIL import Image, ImageTk
import tkinter.font as tkFont
import shutil
import threading

def has_subdirectories(path):
    """
    Checks if the given directory path contains any subdirectories.
    Returns True if at least one subdirectory is found, False otherwise.
    """
    try:
        with os.scandir(path) as entries:
            return any(entry.is_dir() for entry in entries)
    except (PermissionError, FileNotFoundError) as e:
        print(f"Cannot access {path}: {e}")
        return False

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Post Scan Output QC")
        self.root.geometry("1000x800")  # Adjusted size for better UI

        # Initialize variables 
        self.post_scan_output_folder = None
        self.post_scan_raw_folder = None  # Now using Post Scan Raw

        # Function call to create header
        self.create_header()

        # Function call to create frames 
        self.create_frames()

        # Function call to show initial frame
        self.show_frame("upload")

    def create_header(self):
        # Create header frame
        header_frame = tk.Frame(self.root, bg='#4a90e3', height=160)
        header_frame.pack(fill="x")

        # Define logo path
        logo_path = "C:/Users/liams/ArchScan_Capture_Project/color_image_detection/archSCAN_logo.png"

        # Check if file for logo exists 
        if not os.path.isfile(logo_path):
            print(f"Error: Logo image file not found at specified file path: {logo_path}")
            return

        # Load logo image using Pillow library
        try:
            logo_image = Image.open(logo_path).convert("RGBA")
            print(f"Successfully loaded image: {logo_path}")
        except Exception as e:
            print(f"Error loading image: {e}")
            return

        # Resize image
        width = 200
        width_percentage = (width / float(logo_image.size[0]))
        height_size = int((float(logo_image.size[1]) * float(width_percentage)))
        try:
            # Update the resize method to use Resampling.LANCZOS
            logo_image = logo_image.resize((width, height_size), Image.Resampling.LANCZOS)
            print(f"Resized image to: {width} x {height_size}")
        except AttributeError:
            # Fallback for older Pillow versions
            logo_image = logo_image.resize((width, height_size), Image.LANCZOS)
            print(f"Resized image to: {width} x {height_size} using Image.LANCZOS")

        # Convert Image object into TkPhoto object 
        try:
            logo_photo = ImageTk.PhotoImage(logo_image)
            print("Pillow Image converted to Tk PhotoImage successfully.")
        except Exception as e:
            print(f"Error converting Pillow Image to TkPhotoImage: {e}")
            return

        # Create label to hold logo image
        try:
            logo_label = tk.Label(header_frame, image=logo_photo, bg='#4a90e3')
            logo_label.image = logo_photo
            logo_label.pack(pady=30)
            print("Logo label created and packed successfully")
        except Exception as e:
            print(f"Error creating or packing the logo label: {e}")
            return

    def create_frames(self):
        # Container for switching frames
        self.container = tk.Frame(self.root, bg='white')
        self.container.pack(fill='both', expand=True)

        # Dictionary to hold different frames
        self.frames = {}

        # Define frame names and corresponding classes
        frame_classes = {
            "upload": UploadFrame,           # Frame for uploading Post Scan Output and Post Scan Raw
            "treeview": TreeViewFrame,      # New frame for displaying the tree view
            # Add other frames here if needed
        }

        for name, F in frame_classes.items():
            frame = F(parent=self.container, controller=self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid to center the frames
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def show_frame(self, frame_name):
        frame = self.frames.get(frame_name)
        if frame:
            frame.tkraise()
            print(f"Switched to frame: {frame_name}")
            if hasattr(frame, "on_show"):
                frame.on_show()
        else:
            print(f"Error: Frame '{frame_name}' does not exist.")

class UploadFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller

        # Initialize variables to store folder paths
        self.post_scan_output_path = tk.StringVar()
        self.post_scan_raw_path = tk.StringVar()  

        # Frame for "Post Scan Output"
        output_frame = tk.LabelFrame(self, text="Post Scan Output", bg='white', font=("Merriweather", 14, "bold"))
        output_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.create_folder_selection(
            parent=output_frame,
            label_var=self.post_scan_output_path,
            expected_name="Post Scan Output"
        )

        # Frame for "Post Scan Raw"
        raw_frame = tk.LabelFrame(self, text="Post Scan Raw", bg='white', font=("Merriweather", 14, "bold"))
        raw_frame.pack(fill="x", padx=20, pady=(10, 20))

        self.create_folder_selection(
            parent=raw_frame,
            label_var=self.post_scan_raw_path,
            expected_name="Post Scan Raw"
        )
        

        # Frame for navigation buttons
        nav_button_frame = tk.Frame(self, bg="white")
        nav_button_frame.pack(fill="both", padx=20, pady=10, side="bottom")

        # Next button 
        self.next_button = tk.Button(
            nav_button_frame,
            text="Next",
            bg="#4a90e3", 
            fg='white', 
            padx=20, 
            font=("Merriweather", 16, "bold"),
            command=lambda: controller.show_frame("treeview"),  # Navigate to TreeViewFrame
            state='disabled'  # Initially disabled
        )
        self.next_button.pack(side="right", pady=10)

        self.post_scan_output_path.trace_add('write', self.check_folders_selected)
        self.post_scan_raw_path.trace_add('write', self.check_folders_selected)  # Now tracking both folders

    def create_folder_selection(self, parent, label_var, expected_name):
        """
        Creates a folder selection interface within the given parent frame.
        """
        # Frame for buttons and label
        selection_frame = tk.Frame(parent, bg='white')
        selection_frame.pack(fill="x", padx=10, pady=10)

        # Select Folder button
        select_button = tk.Button(
            selection_frame, 
            text="Select Folder",  
            bg="#4a90e3", 
            fg='white', 
            padx=10, 
            pady=5, 
            font=("Merriweather", 12, "bold"),
            command=lambda: self.select_folder(label_var, expected_name)
        )
        select_button.pack(side='left')

        # Label to display selected path
        path_label = tk.Label(selection_frame, textvariable=label_var, bg='white', anchor='w', font=("Merriweather", 12))
        path_label.pack(side='left', fill='x', expand=True, padx=10)

        # Clear button
        clear_button = tk.Button(
            selection_frame, 
            text="Clear",  
            bg="#e74c3c", 
            fg='white', 
            padx=10, 
            pady=5, 
            font=("Merriweather", 12, "bold"),
            command=lambda: self.clear_folder(label_var)
        )
        clear_button.pack(side='right')

    def select_folder(self, label_var, expected_name):
        """
        Opens a dialog to select a folder and validates its name.
        """
        selected_folder = filedialog.askdirectory(title=f"Select '{expected_name}' Folder")
        if selected_folder:
            folder_name = os.path.basename(os.path.normpath(selected_folder))
            if folder_name != expected_name:
                messagebox.showerror("Invalid Folder", f"Please select a folder named '{expected_name}'.\nSelected folder name: '{folder_name}'")
                return
            label_var.set(selected_folder)
            if expected_name == "Post Scan Raw":
                # Update the controller with the Post Scan Raw path
                self.controller.post_scan_raw_folder = selected_folder
            if expected_name == "Post Scan Output":
                self.controller.post_scan_output_folder = selected_folder

    def clear_folder(self, label_var):
        """
        Clears the selected folder path.
        """
        label_var.set('')

    def check_folders_selected(self, *args):
        """
        Checks if both required folders are selected and enables the Next button accordingly.
        """
        output = self.post_scan_output_path.get()
        raw = self.post_scan_raw_path.get()
        if output and raw:
            self.next_button.config(state='normal')
        else:
            self.next_button.config(state='disabled')

class TreeViewFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller

        # Initialize a dictionary to map node IDs to their full paths
        self.node_path_map = {}

        # Header label
        header_label = tk.Label(self, text="Directory Structure", font=("Merriweather", 16, "bold"), bg='white')
        header_label.pack(pady=10)

        # Define custom fonts
        item_font = tkFont.Font(family="Merriweather", size=12, weight="bold")
        heading_font = tkFont.Font(family="Merriweather", size=14, weight="bold")

        # Configure Treeview style
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Custom.Treeview",
                        font=item_font,  # Set the font for Treeview items
                        rowheight=25)    # Optional: set row height

        style.configure("Custom.Treeview.Heading",
                font=heading_font)  # Set the font for headings

        # Create a container frame for Treeview and Scrollbar
        tree_container = tk.Frame(self, bg='white')
        tree_container.pack(fill='both', expand=True, padx=30, pady=10)

        # Create a Treeview widget
        self.tree = ttk.Treeview(tree_container, style="Custom.Treeview")
        self.tree.pack(side='left', fill='both', expand=True)

        # Add a vertical scrollbar to the Treeview
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')

        # Configure the Treeview to use the scrollbar
        self.tree.configure(yscrollcommand=vsb.set)

        # Define columns
        self.tree["columns"] = ("Type")
        self.tree.column("#0", width=400, anchor='w')
        self.tree.column("Type", width=100, anchor='center')
        self.tree.heading("#0", text="Name", anchor='w')
        self.tree.heading("Type", text="Type", anchor='center')

        # Bind the Treeview's item expansion to load subdirectories dynamically
        self.tree.bind("<<TreeviewOpen>>", self.on_open)

        # Bind the selection event to handle button state
        self.tree.bind("<<TreeviewSelect>>", self.on_selection)

        # Create a frame for the button at the bottom
        button_frame = tk.Frame(self, bg='white')
        button_frame.pack(fill='x', padx=30, pady=10)

        # Add the button, initially disabled
        self.box_button = tk.Button(
            button_frame,
            text="Process Selected Box",  # Placeholder text
            bg="#4a90e3",
            fg='white',
            padx=20,
            font=("Merriweather", 14, "bold"),
            command=self.process_box,  # Updated command
            state='disabled'  # Initially disabled
        )
        self.box_button.pack(side='right')

        # Add a text widget to display logs
        self.log_text = tk.Text(self, height=10, state='disabled', bg='#f0f0f0')
        self.log_text.pack(fill='both', padx=30, pady=(0,10), expand=True)

        # Add a progress bar
        self.progress = ttk.Progressbar(self, orient='horizontal', mode='determinate')
        self.progress.pack(fill='x', padx=30, pady=(0,10))

    def on_show(self):
        self.populate_tree()

    def populate_tree(self):
        # Clear existing tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Clear the node_path_map
        self.node_path_map.clear()

        # Get the selected Post Scan Output and Raw folders from the controller
        folder_path_output = self.controller.post_scan_output_folder
        folder_path_raw = self.controller.post_scan_raw_folder

        if not folder_path_output or not os.path.isdir(folder_path_output):
            messagebox.showerror("Error", "Invalid 'Post Scan Output' folder path.")
            return

        if not folder_path_raw or not os.path.isdir(folder_path_raw):
            messagebox.showerror("Error", "Invalid 'Post Scan Raw' folder path.")
            return

        # Insert the root folder for Post Scan Output
        root_node = self.tree.insert("", "end", text=os.path.basename(folder_path_output), values=("Post Scan Output"), open=False)
        # Map the root node to its full path
        self.node_path_map[root_node] = folder_path_output
        # Store the root node ID for reference
        self.root_node = root_node
        # Insert subdirectories
        self.insert_subdirectories(root_node, folder_path_output)

    def insert_subdirectories(self, parent, path):
        """
        Inserts subdirectories into the tree. Adds a dummy child only if the directory contains subdirectories.
        """
        try:
            # Sort entries: directories first, then files
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                if entry.is_dir():
                    # Check if this directory has any subdirectories
                    if has_subdirectories(entry.path):
                        # Insert the directory node
                        node = self.tree.insert(parent, "end", text=entry.name, values=("Box" if parent == self.root_node else "Folder"), open=False)
                        # Map the node to its full path
                        self.node_path_map[node] = entry.path
                        # Insert a dummy child to make the node expandable
                        self.tree.insert(node, "end")  # Dummy child
                    else:
                        # Insert the directory node without a dummy child
                        node = self.tree.insert(parent, "end", text=entry.name, values=("Box" if parent == self.root_node else "Folder"), open=False)
                        # Map the node to its full path
                        self.node_path_map[node] = entry.path
        except PermissionError:
            # Skip directories for which the user does not have permissions
            self.log(f"Permission denied: {path}")
        except FileNotFoundError as e:
            # Handle cases where the directory was removed during runtime
            self.log(f"FileNotFoundError: {e}")
            messagebox.showerror("Error", f"Directory not found: {path}\n{e}")
        except Exception as e:
            # Handle other unforeseen exceptions
            self.log(f"Error accessing {path}: {e}")
            messagebox.showerror("Error", f"An error occurred while accessing: {path}\n{e}")

    def on_open(self, event):
        """
        Called when a node is expanded. It removes the dummy child and inserts actual subdirectories.
        """
        node = self.tree.focus()
        children = self.tree.get_children(node)
        # If the first child is a dummy, remove it and insert actual children
        if len(children) == 1 and self.tree.item(children[0], "text") == '':
            self.tree.delete(children[0])
            folder_path = self.node_path_map.get(node)
            if folder_path:
                self.insert_subdirectories(node, folder_path)

    def on_selection(self, event):
        """
        Callback function when a tree item is selected. Enables the button if a Box is selected.
        """
        selected_node = self.tree.focus()
        if not selected_node:
            self.box_button.config(state='disabled')
            return

        parent_node = self.tree.parent(selected_node)

        # Check if the parent node is the root node
        if parent_node == self.root_node:
            # It's a Box
            self.box_button.config(state='normal')
        else:
            # Not a Box
            self.box_button.config(state='disabled')

    def process_box(self):
        """
        Initiates the processing of the selected Box in a separate thread.
        """
        selected_node = self.tree.focus()
        box_path_output = self.node_path_map.get(selected_node)
        if not box_path_output:
            messagebox.showerror("Error", "Selected Box path not found.")
            return

        # Derive the corresponding Box path in Post Scan Raw
        post_scan_raw_root = self.controller.post_scan_raw_folder
        box_name = os.path.basename(os.path.normpath(box_path_output))
        box_path_raw = os.path.join(post_scan_raw_root, box_name)

        if not os.path.isdir(box_path_raw):
            messagebox.showerror("Error", f"Corresponding Box in Post Scan Raw not found:\n{box_path_raw}")
            return

        # Disable the button and other interactive elements
        self.box_button.config(state='disabled')
        self.log(f"Starting processing of Box: {box_name}")

        # Start the processing in a new thread
        processing_thread = threading.Thread(target=self.process_box_thread, args=(box_path_output, box_path_raw, box_name))
        processing_thread.start()

    def process_box_thread(self, box_path_output, box_path_raw, box_name):
        """
        The actual processing logic running in a separate thread.
        """
        try:
            # Retrieve all Folders within the Box in Post Scan Output
            folders_output = self.get_folders(box_path_output)
            total_folders = len(folders_output)
            if total_folders == 0:
                self.log(f"No Folders found in Box: {box_name}")
                self.enable_button()
                return

            self.progress['maximum'] = total_folders
            current_progress = 0

            for folder_output in folders_output:
                folder_name = os.path.basename(os.path.normpath(folder_output))
                folder_raw = os.path.join(box_path_raw, folder_name)
                jpg_dir_raw = os.path.join(folder_raw, "JPG")

                if not os.path.isdir(jpg_dir_raw):
                    self.log(f"JPG directory not found in Raw for Folder: {folder_name}")
                    current_progress += 1
                    self.update_progress(current_progress)
                    continue

                # Build mappings for TIF and JPG files
                tiff_mapping_output = self.build_tiff_mapping(folder_output)
                jpg_mapping_raw = self.build_jpg_mapping(jpg_dir_raw)

                if not tiff_mapping_output:
                    self.log(f"No valid TIF files to process in Folder: {folder_name}")
                    current_progress += 1
                    self.update_progress(current_progress)
                    continue

                for key, tiff_files in tiff_mapping_output.items():
                    first_digit, last_four = key
                    jpg_filename = f"{first_digit}1{last_four}.jpg"
                    jpg_path_raw = os.path.join(jpg_dir_raw, jpg_filename)

                    if os.path.isfile(jpg_path_raw):
                        for tiff_file in tiff_files:
                            tif_path_output = os.path.join(folder_output, tiff_file)

                            # Backup the TIF file
                            backup_path = tif_path_output + ".bak"
                            shutil.copy2(tif_path_output, backup_path)
                            self.log(f"Backed up {tif_path_output} to {backup_path}")

                            # Replace TIF with JPG
                            shutil.copy2(jpg_path_raw, tif_path_output)
                            self.log(f"Replaced {tif_path_output} with {jpg_path_raw}")

                            # Optionally, remove the original TIF file if needed
                            # os.remove(tif_path_output)
                            # self.log(f"Removed original TIF file: {tif_path_output}")
                    else:
                        for tiff_file in tiff_files:
                            self.log(f"No corresponding JPG found for TIF: {tiff_file} in Folder: {folder_name}")

                # Update progress after processing each Folder
                current_progress += 1
                self.update_progress(current_progress)

            self.log(f"Processing completed for Box: {box_name}")
            messagebox.showinfo("Success", f"Processing completed for Box: {box_name}")
        except Exception as e:
            self.log(f"Error during processing: {e}")
            messagebox.showerror("Error", f"An error occurred during processing:\n{e}")
        finally:
            # Re-enable the button after processing
            self.enable_button()

    def extract_last_four_digits(self, filename):
        """
        Extract the last four numerical digits before the file extension.
        
        Parameters:
            filename (str): The filename to extract digits from.
        
        Returns:
            str or None: The last four digits as a string, or None if extraction fails.
        """
        base, _ = os.path.splitext(filename)
        digits = ''.join(filter(str.isdigit, base))
        if len(digits) < 4:
            return None
        return digits[-4:]

    def extract_first_digit(self, filename):
        """
        Extract the first numerical digit of the filename before the extension.
        
        Parameters:
            filename (str): The filename to extract the first digit from.
        
        Returns:
            str or None: The first digit as a string, or None if extraction fails.
        """
        base, _ = os.path.splitext(filename)
        for char in base:
            if char.isdigit():
                return char
        return None

    def is_valid_tiff(self, filename):
        """
        Validates if the TIFF file follows the naming convention.
        Specifically, checks if the second character in the base name is '0'.
        
        Parameters:
            filename (str): The TIFF filename to validate.
        
        Returns:
            bool: True if valid, False otherwise.
        """
        if len(filename) < 6:
            return False
        second_digit = filename[1]
        return second_digit == '0'

    def is_valid_jpg(self, filename):
        """
        Validates if the JPG file follows the naming convention.
        Specifically, checks if the second character in the base name is '1'.
        
        Parameters:
            filename (str): The JPG filename to validate.
        
        Returns:
            bool: True if valid, False otherwise.
        """
        if len(filename) < 6:
            return False
        second_digit = filename[1]
        return second_digit == '1'

    def build_tiff_mapping(self, input_dir_tiff):
        """
        Build a dictionary mapping (first_digit, last_four_digits) to corresponding TIFF filenames.
        Only include TIFF files where the second character in the base name is '0'.

        Parameters:
            input_dir_tiff (str): Directory containing TIFF files.

        Returns:
            dict: Mapping of (first_digit, last_four_digits) to list of TIFF filenames.
        """
        tiff_mapping = {}
        try:
            all_tiff_files = [
                f for f in os.listdir(input_dir_tiff)
                if f.lower().endswith(('.tif', '.tiff')) and self.is_valid_tiff(f)
            ]

            self.log(f"Found {len(all_tiff_files)} valid TIFF files in '{input_dir_tiff}'.")

            for tiff in all_tiff_files:
                first_digit = self.extract_first_digit(tiff)
                last_four = self.extract_last_four_digits(tiff)
                if not first_digit or not last_four:
                    self.log(f"Could not extract necessary digits from TIFF '{tiff}'. Skipping.")
                    continue

                key = (first_digit, last_four)
                if key in tiff_mapping:
                    tiff_mapping[key].append(tiff)
                    self.log(f"Appending to existing key {key}: {tiff}")
                else:
                    tiff_mapping[key] = [tiff]
                    self.log(f"Mapping {key} to {tiff}")

        except Exception as e:
            self.log(f"Error building TIFF mapping: {str(e)}")
            raise  # Re-raise exception to be handled by the caller

        return tiff_mapping

    def build_jpg_mapping(self, input_dir_jpg):
        """
        Build a dictionary mapping (first_digit, last_four_digits) to corresponding JPG filenames.
        Only include JPG files where the second character in the base name is '1'.

        Parameters:
            input_dir_jpg (str): Directory containing JPG files.

        Returns:
            dict: Mapping of (first_digit, last_four_digits) to list of JPG filenames.
        """
        jpg_mapping = {}
        try:
            all_jpg_files = [
                f for f in os.listdir(input_dir_jpg)
                if f.lower().endswith('.jpg') and self.is_valid_jpg(f)
            ]

            self.log(f"Found {len(all_jpg_files)} valid JPG files in '{input_dir_jpg}'.")

            for jpg in all_jpg_files:
                first_digit = self.extract_first_digit(jpg)
                last_four = self.extract_last_four_digits(jpg)
                if not first_digit or not last_four:
                    self.log(f"Could not extract necessary digits from JPG '{jpg}'. Skipping.")
                    continue

                key = (first_digit, last_four)
                if key in jpg_mapping:
                    jpg_mapping[key].append(jpg)
                    self.log(f"Appending to existing key {key}: {jpg}")
                else:
                    jpg_mapping[key] = [jpg]
                    self.log(f"Mapping {key} to {jpg}")

        except Exception as e:
            self.log(f"Error building JPG mapping: {str(e)}")
            raise  # Re-raise exception to be handled by the caller

        return jpg_mapping

    def get_folders(self, box_path_output):
        """
        Retrieves all Folder paths within a Box in Post Scan Output.
        """
        try:
            return [os.path.join(box_path_output, d) for d in os.listdir(box_path_output)
                    if os.path.isdir(os.path.join(box_path_output, d))]
        except Exception as e:
            self.log(f"Error accessing folders in Box: {box_path_output}: {e}")
            return []

    def log(self, message):
        """
        Logs messages to the log_text widget.
        """
        self.log_text.config(state='normal')
        self.log_text.insert('end', message + '\n')
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def update_progress(self, value):
        """
        Updates the progress bar. Must be called from the main thread.
        """
        self.progress.after(0, lambda: self.progress.config(value=value))

    def enable_button(self):
        """
        Re-enables the process button. Must be called from the main thread.
        """
        self.progress.after(0, lambda: self.box_button.config(state='normal'))

def main():    
    # Initialize and run the GUI
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
