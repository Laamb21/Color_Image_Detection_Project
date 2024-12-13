import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from PIL import Image, ImageTk
import tkinter.font as tkFont
import shutil
import threading
import queue
import re  # Importing regex module
import platform  # Importing platform module to detect OS

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
        self.root.geometry("1600x1000")  # Increased size for better UI

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
            "treeview": TreeViewFrame,      # Frame for displaying the tree view
            "qc": QCFrame,                   # New frame for Quality Control
            # Add other frames here if needed
        }

        for name, F in frame_classes.items():
            frame = F(parent=self.container, controller=self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid to center the frames
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def show_frame(self, frame_name, **kwargs):
        frame = self.frames.get(frame_name)
        if frame:
            frame.tkraise()
            print(f"Switched to frame: {frame_name}")
            if hasattr(frame, "on_show"):
                frame.on_show(**kwargs)
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

        # Trace changes in both folder path variables to enable/disable the Next button
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
            text="Process Selected Box",
            bg="#4a90e3",
            fg='white',
            padx=20,
            font=("Merriweather", 14, "bold"),
            command=self.process_box,  # Updated command
            state='disabled'  # Initially disabled
        )
        self.box_button.pack(side='right')

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
        # Insert subdirectories (Boxes)
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
                        # Insert the directory node (Box)
                        node = self.tree.insert(parent, "end", text=entry.name, values=("Box"), open=False)
                        # Map the node to its full path
                        self.node_path_map[node] = entry.path
                        # Insert a dummy child to make the node expandable
                        self.tree.insert(node, "end")  # Dummy child
                    else:
                        # Insert the directory node without a dummy child
                        node = self.tree.insert(parent, "end", text=entry.name, values=("Folder"), open=False)
                        # Map the node to its full path
                        self.node_path_map[node] = entry.path
        except PermissionError:
            # Skip directories for which the user does not have permissions
            print(f"Permission denied: {path}")
        except FileNotFoundError as e:
            # Handle cases where the directory was removed during runtime
            print(f"FileNotFoundError: {e}")
            messagebox.showerror("Error", f"Directory not found: {path}\n{e}")
        except Exception as e:
            # Handle other unforeseen exceptions
            print(f"Error accessing {path}: {e}")
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
        Initiates the processing of the selected Box and navigates to QCFrame.
        """
        selected_node = self.tree.focus()
        box_path_output = self.node_path_map.get(selected_node)
        if not box_path_output:
            messagebox.showerror("Error", "Selected Box path not found.")
            return

        # Derive the corresponding Box path in Post Scan Raw without appending 'JPG'
        post_scan_raw_root = self.controller.post_scan_raw_folder
        box_name = os.path.basename(os.path.normpath(box_path_output))
        box_path_raw = os.path.join(post_scan_raw_root, box_name)  # Remove 'JPG' subdirectory

        print(f"Box Path Raw: {box_path_raw}")  # Debugging log

        if not os.path.isdir(box_path_raw):
            messagebox.showerror("Error", f"Corresponding Box in Post Scan Raw not found:\n{box_path_raw}")
            return

        # Navigate to QCFrame, passing the Box paths
        self.controller.show_frame("qc", box_path_output=box_path_output, box_path_raw=box_path_raw, box_name=box_name)

class QCFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller

        # Header label
        header_label = tk.Label(self, text="Quality Control", font=("Merriweather", 16, "bold"), bg='white')
        header_label.pack(pady=10)

        # Create a canvas with a scrollbar for the grid view
        canvas_frame = tk.Frame(self, bg='white')
        canvas_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Back button to return to TreeViewFrame
        back_button = tk.Button(
            self,
            text="Back",
            bg="#4a90e3",
            fg='white',
            padx=20,
            font=("Merriweather", 12, "bold"),
            command=lambda: controller.show_frame("treeview")
        )
        back_button.pack(pady=10)

        # Overlay frame for loading indicator
        self.overlay_frame = tk.Frame(self, bg='white')
        self.overlay_frame.place(relx=0.5, rely=0.5, anchor='center')  # Center in the window
        self.overlay_frame.lift()  # Ensure it stays on top
        self.overlay_frame.pack_propagate(False)  # Prevent frame from resizing to its content
        self.overlay_frame.place_forget()  # Hide it initially

        # Loading label and progress bar inside the overlay frame
        self.loading_label = tk.Label(self.overlay_frame, text="Loading TIF and JPG files...", font=("Merriweather", 14), bg='white')
        self.loading_label.pack(padx=20, pady=(10, 5))

        self.progress_bar = ttk.Progressbar(self.overlay_frame, mode='indeterminate')
        self.progress_bar.pack(padx=20, pady=(5, 10))

        # Initialize queue and threading
        self.queue = queue.Queue()
        self.thread = None

        # Store the Box paths
        self.box_path_output = None
        self.box_path_raw = None
        self.box_name = None

        # To keep references to PhotoImage objects to prevent garbage collection
        self.photo_images = []

        # Initialize a variable to track the current row
        self.current_row = 1  # Start after loading frame

        # Bind mouse wheel events for scrolling
        system = platform.system()
        if system == 'Windows' or system == 'Darwin':
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        else:
            self.canvas.bind_all("<Button-4>", self._on_linux_scroll)
            self.canvas.bind_all("<Button-5>", self._on_linux_scroll)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling for Windows and macOS."""
        if platform.system() == 'Windows':
            # For Windows, event.delta is a multiple of 120
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            # For macOS, event.delta needs different scaling
            self.canvas.yview_scroll(int(-1*(event.delta)), "units")

    def _on_linux_scroll(self, event):
        """Handle mouse wheel scrolling for Linux."""
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def on_show(self, box_path_output, box_path_raw, box_name):
        """
        Called when the frame is shown. Sets up the grid view.
        """
        self.box_path_output = box_path_output
        self.box_path_raw = box_path_raw
        self.box_name = box_name

        # Reset row counter
        self.current_row = 1  # Start after loading frame

        # Clear any existing widgets in the scrollable frame except the overlay frame
        for widget in self.scrollable_frame.winfo_children():
            if widget != self.overlay_frame:
                widget.destroy()

        # Show the loading indicator
        self.overlay_frame.place(relx=0.5, rely=0.5, anchor='center')
        self.overlay_frame.lift()  # Bring to front
        self.progress_bar.start(10)  # Start the indeterminate progress bar

        # Start the worker thread to load TIF and JPG files
        self.thread = threading.Thread(target=self.load_files, daemon=True)
        self.thread.start()

        # Start checking the queue
        self.after(100, self.process_queue)

    def load_files(self):
        """
        Worker thread function to load TIF and JPG file paths and enqueue them as pairs.
        """
        folders_output = self.get_folders(self.box_path_output)
        if not folders_output:
            self.queue.put(("error", f"No Folders found in Box: {self.box_name}"))
            return

        for folder_output in folders_output:
            folder_name = os.path.basename(os.path.normpath(folder_output))
            tif_files = self.get_tif_files(folder_output)
            if not tif_files:
                self.queue.put(("message", f"No TIF files found in Folder: {folder_name}"))
                continue

            # Build the path to the 'JPG' subdirectory in Post Scan Raw for this Folder
            folder_raw_jpg = os.path.join(self.box_path_raw, folder_name, 'JPG')
            if not os.path.isdir(folder_raw_jpg):
                self.queue.put(("error", f"Corresponding 'JPG' Folder not found: {folder_raw_jpg}"))
                continue

            jpg_files = self.get_jpg_files(folder_raw_jpg)
            jpg_mapping = self.build_jpg_mapping(jpg_files)

            # Log the mapping for debugging
            print(f"\nProcessing Folder: {folder_name}")
            print("JPG Mapping (Last Four Digits -> JPG Filenames):")
            for digits, jpg_list in jpg_mapping.items():
                print(f"  {digits}: {jpg_list}")

            for tif in tif_files:
                tif_path = os.path.join(folder_output, tif)
                last_four = self.extract_last_four_digits(tif)
                if not last_four:
                    self.queue.put(("message", f"Could not extract last four digits from TIF: {tif}"))
                    self.queue.put(("pair", (tif_path, None)))
                    continue

                corresponding_jpgs = jpg_mapping.get(last_four, [])
                if corresponding_jpgs:
                    # If multiple JPGs match, enqueue each pair
                    for jpg in corresponding_jpgs:
                        jpg_path = os.path.join(folder_raw_jpg, jpg)
                        self.queue.put(("pair", (tif_path, jpg_path)))
                else:
                    self.queue.put(("pair", (tif_path, None)))

        # Indicate that loading is complete
        self.queue.put(("done", None))

    def process_queue(self):
        """
        Processes items in the queue. Should be called periodically using `after`.
        """
        try:
            while True:
                item = self.queue.get_nowait()
                if item[0] == "pair":
                    tif_path, jpg_path = item[1]
                    self.display_pair(tif_path, jpg_path)
                elif item[0] == "message":
                    message = item[1]
                    self.display_message(message)
                elif item[0] == "error":
                    error_msg = item[1]
                    self.display_error(error_msg)
                elif item[0] == "done":
                    self.overlay_frame.place_forget()  # Hide the loading indicator
                    self.progress_bar.stop()
        except queue.Empty:
            pass
        finally:
            if self.thread.is_alive() or not self.queue.empty():
                self.after(100, self.process_queue)  # Continue checking the queue
            else:
                # Loading complete
                self.overlay_frame.place_forget()
                self.progress_bar.stop()

    def display_pair(self, tif_path, jpg_path):
        """
        Displays a pair of TIF and corresponding JPG files side by side in the grid.
        """
        folder_name = os.path.basename(os.path.dirname(tif_path))
        tif_name = os.path.basename(tif_path)
        jpg_name = os.path.basename(jpg_path) if jpg_path else "No Corresponding JPG"

        # If it's the first pair in a Folder, add a Folder label
        if not hasattr(self, 'current_folder') or self.current_folder != folder_name:
            self.current_folder = folder_name
            folder_label = tk.Label(self.scrollable_frame, text=f"Folder: {folder_name}", font=("Merriweather", 12, "bold"), bg='white')
            folder_label.grid(row=self.current_row, column=0, columnspan=2, pady=(10, 5), sticky='w')
            self.current_row += 1

        row = self.current_row

        # Load and create thumbnails for TIF
        try:
            img_tif = Image.open(tif_path)
            img_tif.thumbnail((300, 300))
            photo_tif = ImageTk.PhotoImage(img_tif)
            print(f"Loaded TIF: {tif_path}")
        except Exception as e:
            print(f"Error loading image {tif_path}: {e}")
            photo_tif = None

        # Load and create thumbnails for JPG
        if jpg_path and os.path.isfile(jpg_path):
            try:
                img_jpg = Image.open(jpg_path)
                img_jpg.thumbnail((300, 300))
                photo_jpg = ImageTk.PhotoImage(img_jpg)
                print(f"Loaded JPG: {jpg_path}")
            except Exception as e:
                print(f"Error loading image {jpg_path}: {e}")
                photo_jpg = None
        else:
            photo_jpg = None
            print(f"No corresponding JPG found for TIF: {tif_path}")

        # Display TIF Image
        if photo_tif:
            tif_label = tk.Label(self.scrollable_frame, image=photo_tif, bg='white')
            tif_label.grid(row=row, column=0, padx=10, pady=10)

            # Filename label for TIF
            tif_filename_label = tk.Label(self.scrollable_frame, text=tif_name, bg='white')
            tif_filename_label.grid(row=row+1, column=0, padx=10, pady=(0, 10))
        else:
            tif_error_label = tk.Label(self.scrollable_frame, text=f"Failed to load {tif_name}", bg='white', fg='red')
            tif_error_label.grid(row=row, column=0, padx=10, pady=10)

        # Display JPG Image
        if photo_jpg:
            jpg_label = tk.Label(self.scrollable_frame, image=photo_jpg, bg='white')
            jpg_label.grid(row=row, column=1, padx=10, pady=10)

            # Filename label for JPG
            jpg_filename_label = tk.Label(self.scrollable_frame, text=jpg_name, bg='white')
            jpg_filename_label.grid(row=row+1, column=1, padx=10, pady=(0, 10))
        else:
            jpg_error_label = tk.Label(self.scrollable_frame, text="No Corresponding JPG", bg='white', fg='orange')
            jpg_error_label.grid(row=row, column=1, padx=10, pady=10)

        # Keep a reference to PhotoImage objects to prevent garbage collection
        if photo_tif:
            self.photo_images.append(photo_tif)
        if photo_jpg:
            self.photo_images.append(photo_jpg)

        # Optionally, you can add more columns for additional images or information

        # Increment row counter
        self.current_row += 2  # Move past the image and filename labels

    def display_message(self, message):
        """
        Displays informational messages in the scrollable frame.
        """
        row = self.current_row
        msg_label = tk.Label(self.scrollable_frame, text=message, bg='white', fg='blue')
        msg_label.grid(row=row, column=0, columnspan=2, pady=5, sticky='w')
        self.current_row += 1

    def display_error(self, error_msg):
        """
        Displays error messages in the scrollable frame.
        """
        row = self.current_row
        error_label = tk.Label(self.scrollable_frame, text=error_msg, bg='white', fg='red')
        error_label.grid(row=row, column=0, columnspan=2, pady=5, sticky='w')
        self.current_row += 1

    def get_next_row(self):
        """
        Determines the next available row in the grid.
        """
        current_rows = self.scrollable_frame.grid_size()[1]
        return current_rows

    def get_folders(self, box_path_output):
        """
        Retrieves all Folder paths within a Box in Post Scan Output.
        """
        try:
            return [os.path.join(box_path_output, d) for d in os.listdir(box_path_output)
                    if os.path.isdir(os.path.join(box_path_output, d))]
        except Exception as e:
            self.show_error(f"Error accessing folders in Box: {box_path_output}: {e}")
            return []

    def get_tif_files(self, folder_path):
        """
        Retrieves all TIF files within a Folder in Post Scan Output.
        """
        try:
            return [f for f in os.listdir(folder_path) if f.lower().endswith(('.tif', '.tiff'))]
        except Exception as e:
            self.show_error(f"Error accessing TIF files in Folder: {folder_path}: {e}")
            return []

    def get_jpg_files(self, folder_path):
        """
        Retrieves all JPG files within the 'JPG' Subdirectory in Post Scan Raw.
        """
        try:
            return [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]
        except Exception as e:
            self.show_error(f"Error accessing JPG files in Folder: {folder_path}: {e}")
            return []

    def build_jpg_mapping(self, jpg_files):
        """
        Builds a mapping from the last four digits to JPG filenames.
        """
        mapping = {}
        for jpg in jpg_files:
            last_four = self.extract_last_four_digits(jpg)
            if last_four:
                # If multiple JPGs have the same last four digits, store them in a list
                if last_four in mapping:
                    mapping[last_four].append(jpg)
                else:
                    mapping[last_four] = [jpg]
        return mapping

    def extract_last_four_digits(self, filename):
        """
        Extracts the last four numerical digits from the filename before the extension using regex.
        """
        match = re.search(r'(\d{4})\D*$', filename)
        if match:
            return match.group(1)
        return None

    def show_error(self, message):
        """
        Displays an error message box.
        """
        messagebox.showerror("Error", message)


def main():    
    # Initialize and run the GUI
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
