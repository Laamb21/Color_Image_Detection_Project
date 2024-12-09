'''
Chat code for upload frame 
'''

# Imports
import tkinter as tk
import os
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox
import pydub
from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import which

AudioSegment.converter = which("ffmpeg")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Post Scan Output QC")
        self.root.geometry("800x700") #Change to fill screen 

        # Initialize variables 
        self.post_scan_output_folder = tk.StringVar()
        self.post_scan_raw_folder = tk.StringVar()

        # Function call to create header
        self.create_header()

        # Function call to create frame 
        self.create_frames()

        # Function call to show initial frame
        self.show_frame("welcome")

    def create_header(self):
        #Create header frame
        header_frame = tk.Frame(self.root,bg='#4a90e3', height=160)
        header_frame.pack(fill="x")

        #Define logo path
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
            "welcome": WelcomeFrame,        # Frame for introducing user and displaying instructions
            "upload": UploadFrame,          # Frame for uploading Post Scan Output and Post Scan Raw
            # "mapping": MappingFrame,      # Add your other frames here
            # "analyze": AnalyzeFrame,
            # "qc": QCFrame
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
        else:
            print(f"Error: Frame '{frame_name}' does not exist.")

class WelcomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller

        # Frame for Welcome frame content 
        inner_frame = tk.Frame(self, bg='white')
        inner_frame.pack(fill="both", expand=True)  # Fill all available space

        # Welcome label
        welcome_label = tk.Label(
            inner_frame, 
            text="Welcome to the Post Scan Output QC Script", 
            font=("Merriweather", 24, "bold"), 
            bg='white'
        )
        welcome_label.pack(pady=20)  # Reduced top padding

        # Instructions text
        instructions_text = tk.Text(
            inner_frame,
            font=("Merriweather", 14),
            bg="white",
            wrap="word",
            height=15,  # Adjust as needed
            borderwidth=0,
            highlightthickness=0
        )
        instructions_text.pack(anchor='w', padx=30, pady=(10, 20))

        # Insert instructions
        instructions_content = (
            "Instructions:\n"
            "1. Select the Post Scan Output and Post Scan Raw folder you would like to QC.\n"
            "2. Map JPG to TIF files from Post Scan Raw.\n"
            "3. Find all TIF files from Post Scan Output and corresponding JPG from mapping.\n"
            "4. Display both TIF (from Post Scan Output) and JPG (from Post Scan Raw).\n"
            "5. Select whether to keep the current TIF file or replace TIF with JPG.\n"
            "6. Update Post Scan Raw based on your selection."
        )
        instructions_text.insert(tk.END, instructions_content)
        instructions_text.tag_configure("spacing", spacing1=15)
        instructions_text.tag_add("spacing", "1.20", "end")

        # Frame for next button, packed at the bottom
        next_button_frame = tk.Frame(self, bg='white')
        next_button_frame.pack(side='bottom', fill='x', padx=20, pady=10)  # Positioned at the bottom

        # Next button
        self.next_button = tk.Button(
            next_button_frame, 
            text="Next", 
            bg="#4a90e3", 
            fg='white', 
            padx=20, 
            font=("Merriweather", 16, "bold"),
            command=lambda: controller.show_frame("upload")  
        )
        self.next_button.pack(side='right')

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
        nav_button_frame.pack(fill="both", padx=20, pady=10)

        # Previous button 
        prev_button = tk.Button(
            nav_button_frame,
            text="Back to Instructions",
            bg="#4a90e3", 
            fg='white', 
            padx=20, 
            font=("Merriweather", 16, "bold"),
            command=lambda: controller.show_frame("welcome") 
        )
        prev_button.pack(side="left", pady=10)

        # Next button 
        self.next_button = tk.Button(
            nav_button_frame,
            text="Next",
            bg="#4a90e3", 
            fg='white', 
            padx=20, 
            font=("Merriweather", 16, "bold"),
            command=lambda: controller.show_frame("mapping"),  # Adjust as per your frame names
            state='disabled'  # Initially disabled
        )
        self.next_button.pack(side="right", pady=10)

        # Trace changes to folder paths to enable/disable the Next button
        self.post_scan_output_path.trace_add('write', self.check_folders_selected)
        self.post_scan_raw_path.trace_add('write', self.check_folders_selected)

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
        #bob_auido = AudioSegment.from_file("C:/Users/liams/ArchScan_Capture_Project/color_image_detection/test_folder/ls/bob_wrong_one_dipshit.wav")
        if selected_folder:
            folder_name = os.path.basename(os.path.normpath(selected_folder))
            if folder_name != expected_name:
                messagebox.showerror("Invalid Folder", f"Please select a folder named '{expected_name}'.\nSelected folder name: '{folder_name}'")
                return
            label_var.set(selected_folder)

    def clear_folder(self, label_var):
        """
        Clears the selected folder path.
        """
        label_var.set('')

    def check_folders_selected(self, *args):
        """
        Checks if both folders are selected and enables the Next button accordingly.
        """
        output = self.post_scan_output_path.get()
        raw = self.post_scan_raw_path.get()
        if output and raw:
            self.next_button.config(state='normal')
        else:
            self.next_button.config(state='disabled')

def main():    
    # Initialize and run the GUI
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
