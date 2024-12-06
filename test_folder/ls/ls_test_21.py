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
from tkinter import filedialog, messagebox


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Post Scan Output QC")
        self.root.geometry("800x700") #Change to fill screen 

        #Initialize variables 
        self.post_scan_output_folder = tk.StringVar()
        self.post_scan_raw_folder = tk.StringVar()
        
        #Function call to create header
        self.create_header()

        #Function call ro create frame 
        self.create_frames()

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
            "welcome": WelcomeFrame,        #Frame for introducing user and displaying instructions
            "upload": UploadFrame           #Frame for uploading Post Scan Output and Post Scan Raw
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

        #Frame for Welcome frame content 
        inner_frame = tk.Frame(self, bg='white')
        inner_frame.pack(fill="x")

        #Welcome label
        welcome_label = tk.Label(
            inner_frame, 
            text="Welcome to the Post Scan Output QC Script", 
            font=("Merriweather", 24, "bold"), 
            bg='white'
        )
        welcome_label.pack(pady=20)  # Reduced top padding

        #Instructions text
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

        #Frame for next button
        next_button_frame = tk.Frame(self, bg='white')
        next_button_frame.pack(fill='both', expand=False, padx=20, pady=10, side="bottom")

        #Next button
        self.next_button = tk.Button(
            next_button_frame, 
            text="Next", 
            bg="#4a90e3", 
            fg='white', 
            padx=20, 
            font=("Merriweather", 16, "bold"),
            command=lambda: controller.show_frame("upload"),
        )
        self.next_button.pack(side='right', anchor='s')


class UploadFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller
        self.folders = []

        #Frame for buttons 
        button_frame = tk.Frame(self, bg="white")
        button_frame.pack()

        #Select folder button
        self.selcet_folder_button = tk.Button(
            button_frame, 
            text="Select Folder",  
            bg="#4a90e3", 
            fg='white', 
            padx=10, 
            pady=10, 
            font=("Merriweather", 14, "bold"),
            command=self.select_folder
        )
        self.selcet_folder_button.grid(row=0, column=0, padx=(10,10), pady=(10,10))

        #Remove selected button
        self.remove_selected_button = tk.Button(
            button_frame, 
            text="Remove Selected",  
            bg="#4a90e3", 
            fg='white', 
            padx=10, 
            pady=10, 
            font=("Merriweather", 14, "bold"),
            command=self.remove_folder,
            state="disabled"
        )
        self.remove_selected_button.grid(row=0, column=1, padx=(10,10), pady=(10,10))

        #Frame for displaying selected folders 
        folder_display_frame = tk.Frame(self, bg="white")
        folder_display_frame.pack(fill="both", expand=True)

        #Label for Selected Folders
        selected_folders_label = tk.Label(folder_display_frame, text="Selected Folders:", bg="white", font="Merriweahter")
        selected_folders_label.pack(anchor="w", padx=20)

        #Scrollbar for listbox
        scrollbar = tk.Scrollbar(folder_display_frame, orient='vertical')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        #Listbox to display selected folders
        self.folder_listbox = tk.Listbox(
            folder_display_frame,
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            width=70,
            height=15,
            font=("Merriweather", 12)
        )
        self.folder_listbox.pack(side=tk.LEFT, fill=tk.BOTH, padx=20, pady=20, expand=True)
        scrollbar.config(command=self.folder_listbox.yview)

        #Frame for nav buttons
        nav_button_frame = tk.Frame(self, bg="white")
        nav_button_frame.pack(fill="both")

        #Previous button 
        prev_button = tk.Button(
            nav_button_frame,
            text="Back to Instructions",
            bg="#4a90e3", 
            fg='white', 
            padx=20, 
            font=("Merriweather", 16, "bold"),
            command=lambda: controller.show_frame("welcome") 
        )
        prev_button.pack(side="left", pady=10, padx=10)

        #Next button
        next_button = tk.Button(
            nav_button_frame, 
            text="Next", 
            bg="#4a90e3", 
            fg='white', 
            padx=20, 
            font=("Merriweather", 16, "bold"),
            command=lambda: controller.show_frame("upload"),
        )
        next_button.pack(side='right', pady=10, padx=10)
        

    def select_folder(self):
        selected_folder = filedialog.askdirectory(title="Select Folder")
        if selected_folder:
            if selected_folder not in self.folders:
                self.folders.append(selected_folder)
                self.folder_listbox.insert(tk.END, selected_folder)
        else:
            messagebox.showinfo("Duplicate Folder", "The selected folder is already in the list.")
        self.remove_selected_button.config(state="normal")    

    def remove_folder(self):
        selected_indices = list(self.folder_listbox.curselection())
        if not selected_indices:
            return
        for index in reversed(selected_indices):
            self.folder_listbox.delete(index)
            del self.folders[index]
        #if not self.folders:
            #self.selcet_folder_button.config(state='disabled')
        self.remove_selected_button.config(state='disabled')



def main():    
    # Initialize and run the GUI
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()