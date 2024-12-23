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
        logo_path = "C:/Color_Image_Detection_Project/Color_Image_Detection_Project/test_folder/ls/archSCAN_logo.png"

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

        # Scrollable Navigation Bar
        self.nav_canvas = tk.Canvas(self, height=50, bg="#f0f0f0", highlightthickness=0)
        self.nav_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.nav_canvas.xview)
        self.navbar_frame = tk.Frame(self.nav_canvas, bg="#f0f0f0")

        self.nav_canvas.create_window((0, 0), window=self.navbar_frame, anchor="nw")
        self.nav_canvas.configure(xscrollcommand=self.nav_scrollbar.set)

        self.nav_canvas.pack(fill="x", padx=20, pady=(0, 10))
        self.nav_scrollbar.pack(fill="x", padx=20)

        # Canvas for file display
        canvas_frame = tk.Frame(self, bg='white')
        canvas_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Back button
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

    def on_show(self, box_path_output, box_path_raw, box_name):
        self.box_path_output = box_path_output
        self.box_path_raw = box_path_raw
        self.box_name = box_name

        # Clear previous navigation bar and grid
        for widget in self.navbar_frame.winfo_children():
            widget.destroy()

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Get folders and add buttons to the navigation bar
        self.folders = self.get_folders(self.box_path_output)

        for folder in self.folders:
            folder_name = os.path.basename(folder)
            btn = tk.Button(
                self.navbar_frame,
                text=folder_name,
                bg="#4a90e3",
                fg="white",
                font=("Merriweather", 10, "bold"),
                command=lambda f=folder: self.display_folder_contents(f)
            )
            btn.pack(side="left", padx=5, pady=5)

        # Adjust scrollregion
        self.nav_canvas.update_idletasks()
        self.nav_canvas.configure(scrollregion=self.nav_canvas.bbox("all"))

    def display_folder_contents(self, folder_path):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        tif_files = self.get_image_files(folder_path, (".tif", ".tiff"))
        jpg_folder = os.path.join(self.box_path_raw, os.path.basename(folder_path), "JPG")
        jpg_files = self.get_image_files(jpg_folder, (".jpg",))

        row = 0

        for tif_file, jpg_file in zip(tif_files, jpg_files):
            # Load and display TIF image
            tif_image = self.load_image(os.path.join(folder_path, tif_file))
            jpg_image = self.load_image(os.path.join(jpg_folder, jpg_file))

            if tif_image and jpg_image:
                # Create a frame to center both images
                image_frame = tk.Frame(self.scrollable_frame, bg="white")
                image_frame.grid(row=row, column=0, pady=10)

                # Place TIF image inside the frame
                tif_label = tk.Label(image_frame, image=tif_image, bg="white")
                tif_label.image = tif_image  # Keep a reference to prevent garbage collection
                tif_label.pack(side="left", padx=10)

                # Place JPG image inside the frame
                jpg_label = tk.Label(image_frame, image=jpg_image, bg="white")
                jpg_label.image = jpg_image  # Keep a reference to prevent garbage collection
                jpg_label.pack(side="left", padx=10)

        row += 1

    def get_folders(self, path):
        return [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    def get_image_files(self, path, extensions):
        if not os.path.exists(path):
            return []
        return [f for f in os.listdir(path) if f.lower().endswith(extensions)]

    def load_image(self, file_path):
        try:
            img = Image.open(file_path)
            img = img.resize((200, 200), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")
            return None





def main():    
    # Initialize and run the GUI
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
