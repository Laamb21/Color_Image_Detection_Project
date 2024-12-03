'''
Script to do the following:
    Upload Post Scan Output and Post Scan Raw
    Map JPG to TIF files from Post Scan Raw
    Find all TIF files from Post Scan Output and corresponding JPG from mapping
    Display both TIF (from Post Scan Output) and JPG(from Post Scan Raw)
    Allow user to select whether to keep current TIF file or replace TIF with JPG
    Update Post Scan Raw based on user selection
'''

#Imports here
import tkinter as tk
import os
from PIL import Image, ImageTk


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Post Scan Output QC")
        self.root.geometry("800x700") #Change to fill screen 

        #Initialize variables 

        #Function call to create header
        self.create_header()

        #Function call ro create frame 
        self.create_frames

        #Function call to show initial frame
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
        #Containter for switching frames
        self.container = tk.Frame(self.root, bg='white')
        self.container.pack(fill='both', expand=True)

        # Dictionary to hold different frames
        self.frames = {}

        #Define frame names and corresponding classes
        frame_classes = {
            "welcome": WelcomeFrame        #Frame for introducing user and displaying instructions
            #"upload": UploadFrame          #Frame for uploading Post Scan Output and Post Scan Raw
            #"mapping": MappingFrame        #Frame to map JPGs and TIF from Post Scan Raw
            #"analyze": AnalyzeFrame        #Frame to extract all TIF files from Post Scan Output and corresponding JPGs
            #"qc": QCFrame                  #Frame to let user either keep TIF in Post Scan raw or update with corresponding JPG
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



def main():    
    # Initialize and run the GUI
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()