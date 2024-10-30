# Test to connect welcome screen to upload screen

# Import libraries
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox  # Import messagebox explicitly
from PIL import Image, ImageTk
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("JPG TIF Processor")
        self.root.geometry("800x600")  # Increased width for better alignment
        self.root.configure(bg='white')  # Set background color to match frames

        # Initialize variables
        self.parent_folder = tk.StringVar()
        self.low_threshold = tk.DoubleVar(value=10.0)   # Default low threshold
        self.high_threshold = tk.DoubleVar(value=15.0)  # Default high threshold

        # Function call to create header
        self.create_header()

        # Create frames for different states
        self.create_frames()

        # Show welcome state initially
        self.show_frame("welcome")

    def create_header(self):
        # Create header frame
        header_frame = tk.Frame(self.root, bg='#4a90e3', height=160)
        header_frame.pack(fill='x')

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
            print("Image converted to PhotoImage successfully.")
        except Exception as e:
            print(f"Error converting Image to PhotoImage: {e}")
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
            "welcome": WelcomeFrame,
            "upload": UploadFrame,
            "threshold": ThresholdFrame, 
            "verify": VerifyFrame
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

        # Create an inner frame to center content
        inner_frame = tk.Frame(self, bg='white')
        inner_frame.pack(expand=True)

        # Create "Welcome!" label inside inner_frame
        welcome_label = tk.Label(
            inner_frame, 
            text="Welcome to the \nJPG and TIF Processor!", 
            font=("Merriweather", 24, "bold"), 
            bg='white'
        )
        welcome_label.pack(pady=(0, 20))  # Reduced top padding

        # Create "Get Started" button inside inner_frame
        get_started_button = tk.Button(
            inner_frame, 
            text="Get Started", 
            bg="#4a90e3", 
            fg='white', 
            padx=40, 
            pady=15, 
            font=("Merriweather", 16, "bold"), 
            command=lambda: controller.show_frame("upload")
        )
        get_started_button.pack(pady=10)

class UploadFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller

        # Create an inner frame to center content
        inner_frame = tk.Frame(self, bg='white')
        inner_frame.pack(expand=True, padx=20, pady=20)

        # Create "Upload Set" label inside inner_frame
        upload_set_label = tk.Label(
            inner_frame, 
            text="Upload Set \n(set must contain \n'JPG' and 'TIF' folders)", 
            font=("Merriweather", 24, "bold"), 
            bg='white'
        )
        upload_set_label.pack(pady=(0, 20))  # Reduced top padding

        # Create upload entry inside inner_frame
        upload_set_entry = tk.Entry(inner_frame, textvariable=controller.parent_folder, width=75, font=("Arial", 12))
        upload_set_entry.pack(pady=10)

        # Create upload button inside inner_frame
        upload_set_button = tk.Button(
            inner_frame, 
            text="Upload",  # Consider renaming to "Select Folder" for clarity
            bg="#4a90e3", 
            fg='white', 
            padx=20, 
            pady=10, 
            font=("Merriweather", 16, "bold"),
            command=self.select_folder
        )
        upload_set_button.pack(pady=10)

        # Create a frame for the "Next" button
        next_button_frame = tk.Frame(self, bg='white')
        next_button_frame.pack(fill='both', expand=False, padx=20, pady=10)

        # Create "Next" button inside next_button_frame
        self.next_button = tk.Button(
            next_button_frame, 
            text="Next", 
            bg="#4a90e3", 
            fg='white', 
            padx=20, 
            font=("Merriweather", 16, "bold"),
            state='disabled',  # Initially disabled
            command=lambda: controller.show_frame("threshold")  # Placeholder for future command
        )
        self.next_button.pack(side='right')

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.controller.parent_folder.set(folder_selected)
            messagebox.showinfo("Folder Selected", f"Selected folder: {folder_selected}")
            self.next_button.config(state='normal')  # Enable the "Next" button

    def upload_action(self):
        folder = self.controller.parent_folder.get()
        if os.path.isdir(folder):
            # Add your upload handling logic here
            print(f"Folder '{folder}' is valid and ready for processing.")
            messagebox.showinfo("Success", f"Folder '{folder}' uploaded successfully!")
        else:
            print(f"Invalid folder path: {folder}")
            messagebox.showerror("Error", f"Folder '{folder}' does not exist.")

class ThresholdFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller

        # Create an inner frame to center content
        inner_frame = tk.Frame(self, bg='white')
        inner_frame.pack(expand=True, padx=20, pady=20)

        # Create "Set Grayscale Threshold" label
        set_grayscale_threshold_label = tk.Label(
            inner_frame, 
            text="Set Grayscale Threshold",
            font=("Merriweather", 24, "bold"), 
            bg='white'
        )
        set_grayscale_threshold_label.pack(pady=(0, 20))

        # Create a frame for Low Grayscale Threshold
        low_threshold_frame = tk.Frame(inner_frame, bg='white')
        low_threshold_frame.pack(pady=10, anchor='w')  # Anchor to west (left)

        # Create "Low Grayscale Threshold" label inside low_threshold_frame
        low_grayscale_threshold_label = tk.Label(
            low_threshold_frame,
            text="Low Grayscale Threshold:",
            font=("Merriweather", 18, "bold"), 
            bg='white'
        )
        low_grayscale_threshold_label.grid(row=0, column=0, sticky='w')

        # Create Low Grayscale Threshold entry inside low_threshold_frame
        low_grayscale_threshold_entry = tk.Entry(
            low_threshold_frame,
            textvariable=controller.low_threshold,
            width=10,
            font=("Arial", 12)
        )
        low_grayscale_threshold_entry.grid(row=0, column=1, padx=10, pady=5)

        # Optionally, create High Grayscale Threshold
        high_threshold_frame = tk.Frame(inner_frame, bg='white')
        high_threshold_frame.pack(pady=10, anchor='w')  # Anchor to west (left)

        # Create "High Grayscale Threshold" label inside high_threshold_frame
        high_grayscale_threshold_label = tk.Label(
            high_threshold_frame,
            text="High Grayscale Threshold:",
            font=("Merriweather", 18, "bold"), 
            bg='white'
        )
        high_grayscale_threshold_label.grid(row=0, column=0, sticky='w')

        # Create High Grayscale Threshold entry inside high_threshold_frame
        high_grayscale_threshold_entry = tk.Entry(
            high_threshold_frame,
            textvariable=controller.high_threshold,
            width=10,
            font=("Arial", 12)
        )
        high_grayscale_threshold_entry.grid(row=0, column=1, padx=10, pady=5)

        # Create a frame for navigation buttons (e.g., Back, Next)
        nav_button_frame = tk.Frame(self, bg='white')
        nav_button_frame.pack(fill='both', expand=False, pady=20)

        # Create "Back" button
        back_button = tk.Button(
            nav_button_frame, 
            text="Back", 
            bg="#4a90e3", 
            fg='white', 
            padx=20, 
            font=("Merriweather", 16, "bold"),
            command=lambda: controller.show_frame("upload")
        )
        back_button.pack(side='left')

        # Create "Next" button (if needed)
        next_button = tk.Button(
             nav_button_frame, 
             text="Next", 
             bg="#4a90e3", 
             fg='white', 
             padx=20, 
             font=("Merriweather", 16, "bold"),
             command=lambda: controller.show_frame("verify")
         )
        next_button.pack(side='right')


class VerifyFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller

        # Create an inner frame to center content
        inner_frame = tk.Frame(self, bg='white')
        inner_frame.pack(expand=True, padx=20, pady=20)

        #Create label to prompt user to verify information before running script
        verify_info_label = tk.Label(
            inner_frame, 
            text="Check the boxes to verify \nthe folder and thresholds \nbefore running script",
            font=("Merriweather", 24, "bold"), 
            bg='white'
        )
        verify_info_label.pack(pady=(0, 20))

        #Create label that shows uploaded folder
        folder_label = tk.Label(
            inner_frame,
            text="Folder: ",
            font=("Merriweather", 24, "bold"),
            bg='white'
        )
        folder_label.pack(pady=(0, 20))

def main():    
    # Initialize and run the GUI
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
