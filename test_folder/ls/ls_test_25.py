import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from PIL import Image, ImageTk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Post Scan Output QC")
        self.root.geometry("800x700")  # Adjust as needed

        # Initialize variables 
        self.post_scan_output_folder = None
        # self.post_scan_raw_folder = None  # Uncomment if using

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
        # self.post_scan_raw_path = tk.StringVar()  # Uncomment if using

        # Frame for "Post Scan Output"
        output_frame = tk.LabelFrame(self, text="Post Scan Output", bg='white', font=("Merriweather", 14, "bold"))
        output_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.create_folder_selection(
            parent=output_frame,
            label_var=self.post_scan_output_path,
            expected_name="Post Scan Output"
        )

        # If you need to select "Post Scan Raw", uncomment the following lines
        """
        raw_frame = tk.LabelFrame(self, text="Post Scan Raw", bg='white', font=("Merriweather", 14, "bold"))
        raw_frame.pack(fill="x", padx=20, pady=(10, 20))

        self.create_folder_selection(
            parent=raw_frame,
            label_var=self.post_scan_raw_path,
            expected_name="Post Scan Raw"
        )
        """

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

        # If you have multiple folders, adjust the trace accordingly
        self.post_scan_output_path.trace_add('write', self.check_folders_selected)
        # self.post_scan_raw_path.trace_add('write', self.check_folders_selected)  # Uncomment if using

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
        Checks if the required folders are selected and enables the Next button accordingly.
        """
        output = self.post_scan_output_path.get()
        # raw = self.post_scan_raw_path.get()  # Uncomment if using
        # Adjust the condition based on the number of required folders
        if output:  # If only "Post Scan Output" is required
            self.next_button.config(state='normal')
        else:
            self.next_button.config(state='disabled')
        """
        # If using both Post Scan Output and Post Scan Raw, use the following condition:
        if output and raw:
            self.next_button.config(state='normal')
        else:
            self.next_button.config(state='disabled')
        """

class TreeViewFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller

        # Initialize a dictionary to map node IDs to their full paths
        self.node_path_map = {}

        # Header label
        header_label = tk.Label(self, text="Directory Structure", font=("Merriweather", 16, "bold"), bg='white')
        header_label.pack(pady=10)

        # Create a Treeview widget
        self.tree = ttk.Treeview(self)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Add a vertical scrollbar to the treeview
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        # Define columns
        self.tree["columns"] = ("Type")
        self.tree.column("#0", width=400, anchor='w')
        self.tree.column("Type", width=100, anchor='center')
        self.tree.heading("#0", text="Name", anchor='w')
        self.tree.heading("Type", text="Type", anchor='center')

        # Bind the treeview's item expansion to load subdirectories dynamically
        self.tree.bind("<<TreeviewOpen>>", self.on_open)

    def on_show(self):
        self.populate_tree()

    def populate_tree(self):
        # Clear existing tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Clear the node_path_map
        self.node_path_map.clear()

        # Get the selected Post Scan Output folder from the controller
        folder_path = self.controller.post_scan_output_folder

        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("Error", "Invalid 'Post Scan Output' folder path.")
            return

        # Insert the root folder
        root_node = self.tree.insert("", "end", text=os.path.basename(folder_path), values=("Folder"), open=False)
        # Map the root node to its full path
        self.node_path_map[root_node] = folder_path
        self.insert_subdirectories(root_node, folder_path)

    def insert_subdirectories(self, parent, path):
        """
        Inserts subdirectories into the tree. Adds a dummy child to make the node expandable.
        """
        try:
            # Sort entries: directories first, then files
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                if entry.is_dir():
                    node = self.tree.insert(parent, "end", text=entry.name, values=("Folder"), open=False)
                    # Map the node to its full path
                    self.node_path_map[node] = entry.path
                    # Insert a dummy child to make the node expandable
                    self.tree.insert(node, "end")  # Dummy child
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

def main():    
    # Initialize and run the GUI
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
