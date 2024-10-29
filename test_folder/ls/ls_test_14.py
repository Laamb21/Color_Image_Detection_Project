'''
Test to implement screen transition
States to add:
    1. Welcome 
        When app is first ran, user is greeted with a welcome screen
    2. Upload RAW
        User can upload set folder/post scan raw folder (must contain JPG AND TIF folders)
    3. Threshold 
        User can set low & high grayscale thresholds
    4. Verify 
        User must select checkboxes to verify file path for set/post scan raw folder as well as grayscale thresholds before 
        running script
    5. Run 
        Progress bar to indicate script is running
    6. Results 
        After script is completed, results will show log files, selected files, and flagged files. User can either run another set
        or exit the app
'''

#Import libraries
import queue
import tkinter as tk
from tkinter import ttk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JPG and TIFF Processor ")
        self.geometry("600x600")

        #Container for state frames 
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (WelcomeScreen, 
                  #UploadScreen, 
                  #ThresholdScreen, 
                  #VerifyScreen, 
                  #RunScreen, 
                  #ResultsScreen
                  ):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.current_state = None
        self.user_data = {}

        self.show_frame("WelcomeScreen")
        
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        self.current_state = page_name
        
        
        
        '''
        Come back and use these later 
        

        #Initialize variables
        self.parent_folder = tk.StringVar()                 
        self.low_threshold = tk.DoubleVar(value = 10.0)     #Default low threshold
        self.high_threshold = tk.DoubleVar(value = 15.0)    #Default high threshold
        self.processing_thread = None
        self.process_queue = queue.Queue()

        #Initialize lists
        self.flagged_files = []     #List to keep track of flagged files
        self.selected_files = []    #List to keep track of selected files
        self.log_entries = []       #List to store log data

        #Define all possible states
        self.STATE_WELCOME = "welcome"
        self.STATE_UPLOAD = "upload"
        self.STATE_THRESHOLD = "threshold"
        self.STATE_VERIFY_INPUT = "verify_input"
        self.STATE_RUN = "run"
        self.STATE_RESULTS = "results"
        self.STATE_VERIFY_OUTPUT = "verify_output"

        #Store states in an array
        self.states = [self.STATE_WELCOME, 
                       self.STATE_UPLOAD, 
                       self.STATE_THRESHOLD, 
                       self.STATE_VERIFY_INPUT,
                       self.STATE_RUN,
                       self.STATE_RESULTS,
                       self.STATE_VERIFY_OUTPUT]

        #Initialize current state
        self.current_state = 0
        '''
        
class WelcomeScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill='x')

        company_name = tk.Label(self, image='archSCAN_logo.png', font=("Helvetica", 24, "bold"))
        company_name.pack(expand=True, fill='x', padx=20, pady=20)
        #company_name.place(relx=0.5, rely=0.5, anchor='center')

        welcome_label = tk.Label(self, text="Welcome to the JPG and TIF Processor!")
        welcome_label.pack(expand=True)

        start_button = tk.Button(self, text="Get Started", command=lambda: controller.show_frame("UploadScreen"))
        start_button.pack()

if __name__ == "__main__":
    app = App()
    app.mainloop()


