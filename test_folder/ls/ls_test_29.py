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

        # Bind mouse wheel events for all platforms
        self._bind_mouse_wheel_events()

    def _bind_mouse_wheel_events(self):
        """Bind mouse wheel events for all platforms."""
        self.nav_canvas.bind("<Enter>", self._enable_mouse_wheel)
        self.nav_canvas.bind("<Leave>", self._disable_mouse_wheel)

    def _enable_mouse_wheel(self, event):
        """Enable mouse wheel scrolling."""
        # Windows and macOS
        self.nav_canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)
        # Linux (Button-4 and Button-5 for scroll events)
        self.nav_canvas.bind_all("<Button-4>", lambda e: self._on_mouse_wheel_linux(-1))
        self.nav_canvas.bind_all("<Button-5>", lambda e: self._on_mouse_wheel_linux(1))

    def _disable_mouse_wheel(self, event):
        """Disable mouse wheel scrolling."""
        self.nav_canvas.unbind_all("<MouseWheel>")
        self.nav_canvas.unbind_all("<Button-4>")
        self.nav_canvas.unbind_all("<Button-5>")

    def _on_mouse_wheel(self, event):
        """Handle horizontal scrolling with the mouse wheel."""
        direction = -1 if event.delta > 0 else 1  # Scroll direction
        self.nav_canvas.xview_scroll(direction, "units")
        self._clamp_scroll_position()

    def _on_mouse_wheel_linux(self, direction):
        """Handle horizontal scrolling for Linux."""
        self.nav_canvas.xview_scroll(direction, "units")
        self._clamp_scroll_position()

    def _clamp_scroll_position(self):
        """Clamp the scrollbar position to prevent over-scrolling."""
        left, right = self.nav_canvas.xview()
        if left <= 0:
            self.nav_canvas.xview_moveto(0)
        elif right >= 1.0:
            self.nav_canvas.xview_moveto(1.0)

    def on_show(self, box_path_output, box_path_raw, box_name):
        """Called when the frame is shown. Sets up the navigation bar."""
        # Clear previous navigation bar
        for widget in self.navbar_frame.winfo_children():
            widget.destroy()

        # Add folder buttons
        self.folders = self.get_folders(box_path_output)
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
        """Placeholder to display folder contents."""
        print(f"Displaying contents of {folder_path}")

    def get_folders(self, path):
        """Retrieve subdirectories within a folder."""
        return [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
