import customtkinter as tk
from PIL import Image


class ToplevelWindow(tk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")
        self.resizable(False, False)
        self.title("Logs")
        self.progressbar = tk.CTkProgressBar(self, orientation="horizontal", progress_color="green")
        self.progressbar.pack(fill="x", padx=10, pady=10)
        self.progressbar.set(0)
        self.textbox = tk.CTkTextbox(master=self, width=400, height=250, corner_radius=0)
        self.textbox.configure(state="disabled")
        self.textbox.pack(fill="x", padx=10, pady=10)


class GUI(tk.CTk):
    def __init__(self, process):
        super().__init__()
        self.process = process
        self.target_image = None
        tk.set_appearance_mode("dark")
        tk.set_default_color_theme("dark-blue")
        self.title("DIP")
        self.geometry("700x500")
        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame = tk.CTkFrame(master=self, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="ns")

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
        #
        preview_img = tk.CTkFrame(master=frame, fg_color="#333", width=300, height=300)
        preview_img.grid(row=0, column=0, columnspan=2, pady=10)
        preview_img.columnconfigure(0, weight=1)
        preview_img.rowconfigure(0, weight=1)
        preview_img.grid_propagate(False)
        #
        self.file_entry = tk.CTkEntry(master=frame, width=300, state="disabled")
        self.file_entry.grid(row=1, column=0, sticky="ew", padx=10)
        #
        browse_button = tk.CTkButton(master=frame, text="Browse", width=100, command=self.upload_img)
        browse_button.grid(row=1, column=1, padx=10)
        #
        self.option_menu = tk.CTkOptionMenu(frame, values=["edge_detection", "color_inversion", "blurring", "thresholding", "sharpening", "opening", "image_enhancement", "image_rotating"])
        self.option_menu.grid(row=2, column=0, sticky="ew", padx=10)
        #
        self.process_button = tk.CTkButton(master=frame, text="Process", width=100, fg_color="green", command=self.process_img)
        self.process_button.grid(row=2, column=1, padx=10)
        #
        self.image = tk.CTkLabel(master=preview_img, text="Browse an image to process")
        self.image.grid(row=0, column=0, sticky="nesw")

        self.toplevel_window = None

    def upload_img(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png")]
        filenames = tk.filedialog.askopenfilenames(filetypes=filetypes)
        print(filenames)
        if filenames:
            if len(filenames) > 1:
                img = None
                self.show_img(img, filenames)
            else:
                img = tk.CTkImage(Image.open(filenames[0]), size=(300, 300))
                self.show_img(img, filenames)

    def show_img(self, img, filenames):
        if filenames == "":
            img = tk.CTkImage(Image.fromarray(img), size=(300, 300))
            self.image.configure(image=img, text="")
        elif len(filenames) > 1:
            self.image.configure(text=f"Selected {len(filenames)} images", image="")
            self.target_image = ",".join(filenames)
            self.file_entry.configure(state="normal")
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, f"Selected {len(filenames)} images")
            self.file_entry.configure(state="disabled")
        elif len(filenames) == 1:
            self.image.configure(text="", image=img)
            self.file_entry.configure(state="normal")
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filenames[0])
            self.file_entry.configure(state="disabled")
            self.target_image = filenames[0]

    def process_img(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)
            self.toplevel_window.textbox.configure(state="normal")
            self.toplevel_window.textbox.delete(1.0, tk.END)
            self.toplevel_window.textbox.configure(state="disabled")
        else:
            self.toplevel_window.focus()
        operation = self.option_menu.get()
        self.process(self.target_image, operation)
        self.process_button.configure(state="disabled")

    def run(self):
        self.mainloop()

    def get_widgets(self):
        return self.toplevel_window.textbox, self.toplevel_window.progressbar

    def log(self, text):
        self.toplevel_window.textbox.configure(state="normal")
        self.toplevel_window.textbox.insert(tk.END, text + "\n")
        self.toplevel_window.textbox.configure(state="disabled")

    def update_progress(self, value):
        self.toplevel_window.progressbar.set(value)

    def enable_process_button(self):
        self.process_button.configure(state="normal")