import select
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import os
import threading
import subprocess
import sys
import webbrowser
import time
import json
import threading
from tkinter.scrolledtext import ScrolledText
from chat_utils import *

# Constants (adjust paths as needed)
SERVER = ('127.0.0.1', 12345)  # your chat server address
APP_PY_PATH = '/Users/justinbian/PycharmProjects/hand_written_digit_recognition_CNN/app.py'

class BINGtalkStyledApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BINGTalk Styled GUI")
        self.geometry("1000x600")
        self.configure(bg="#f5f7fa")
        self.s = None  # Placeholder for socket
        self.client_sm = None  # Placeholder for ClientSM
        self.username = None  # Placeholder for username
        self.chat_display = None  # Placeholder for chat display widget


        # Socket & state machine omitted for brevity
        # self.s = socket.socket(...)
        # self.client_sm = ClientSM(self.s)

        self.sidebar_width = 160
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.icons = {}
        self.load_icons()
        self.create_topbar()
        self.create_sidebar()
        self.create_main_area()
# new
    def receive_messages(self):
        while True:
            try:
                msg = myrecv(self.s)
                if msg:
                    self.client_sm.proc('', msg)
                    self.after(0, self.update_chat_display, self.client_sm.out_msg)
            except Exception as e:
                print(f"Connection error: {e}")
                break
# new
    def update_chat_display(self, text):
        if self.chat_display:
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, text + "\n")
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.see(tk.END)

    def load_icons(self):
        icon_names = ["chat", "tools", "logo"]
        for name in icon_names:
            path = os.path.join(os.path.dirname(__file__), 'icons', f"{name}.png")
            try:
                img = Image.open(path)
                size = (40, 40) if name == "logo" else (20, 20)
                img = img.resize(size, Image.Resampling.LANCZOS)
                self.icons[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Failed to load icon {name}: {e}")
                self.icons[name] = None

    def create_topbar(self):
        topbar = tk.Frame(self, height=60, bg="#3c8dbc")
        topbar.grid(row=0, column=0, columnspan=2, sticky="new")
        if self.icons.get("logo"):
            tk.Label(topbar, image=self.icons["logo"], bg="#3c8dbc").pack(side="left", padx=10)
        tk.Label(topbar, text="BINGTalk Simulation System", font=("Helvetica", 16), fg="white", bg="#3c8dbc").pack(side="left")

    def create_sidebar(self):
        sidebar = tk.Frame(self, width=self.sidebar_width, bg="#ecf0f1")
        sidebar.grid(row=1, column=0, sticky="ns")
        buttons = [
            ("Chat", self.icons.get("chat"), self.show_chat),
            ("Tools", self.icons.get("tools"), self.show_tools),
            ("Launch Demo", None, self.launch_server)
        ]
        for label, icon, cmd in buttons:
            btn = tk.Button(
                sidebar, text=f"  {label}", image=icon, compound="left",
                command=cmd, bg="#ecf0f1", relief="flat", anchor="w"
            )
            btn.pack(fill="x", pady=5, padx=10)

    def create_main_area(self):
        self.main_area = tk.Frame(self, bg="#f5f7fa")
        self.main_area.grid(row=1, column=1, sticky="nsew")
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.content_frame = tk.Frame(self.main_area, bg="white")
        self.content_frame.grid(row=0, column=0, sticky="nsew")

    def clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

    def launch_server(self):
        def run():
            os.chdir(os.path.dirname(APP_PY_PATH))
            subprocess.call([sys.executable, APP_PY_PATH])
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        time.sleep(1)
        webbrowser.open('http://127.0.0.1:5000/')

    def show_chat(self):
        self.clear_content()
        tk.Label(self.content_frame, text="📨 Chat zone", font=("Arial", 16)).pack(pady=10)

        # Add chat buttons from BINGtalk_vertical
        for label in ["Chat", "Search", "Who", "Connect", "Disconnect"]:
            tk.Button(
                self.content_frame,
                text=label,
                width=25,
                height=2,
                bg="#f0f0f0"
            ).pack(pady=5)

            # Buttons
            buttons = [
                ("Who", lambda: self.send_command('who')),
                ("Search", self.handle_search),
                ("Connect", self.handle_connect),
                ("Disconnect", lambda: self.send_command('bye')),
            ]
            for text, cmd in buttons:
                btn = tk.Button(
                    self.content_frame,
                    text=text,
                    width=25,
                    height=2,
                    bg="#f0f0f0",
                    command=cmd
                )
                btn.pack(pady=5)

            # Chat display
            self.chat_display = ScrolledText(self.content_frame, wrap=tk.WORD, height=15)
            self.chat_display.pack(fill=tk.BOTH, expand=True)
            self.chat_display.config(state=tk.DISABLED)

    def send_command(self, cmd):
        def task():
            self.client_sm.proc(cmd, '')
            self.update_chat_display(self.client_sm.out_msg)

        threading.Thread(target=task, daemon=True).start()

    def handle_search(self):
        term = simpledialog.askstring("Search", "Enter term:")
        if term:
            self.send_command(f'? {term}')

    def handle_connect(self):
        peer = simpledialog.askstring("Connect", "Peer name:")
        if peer:
            self.send_command(f'c {peer}')

    def show_tools(self):
        self.clear_content()
        tk.Label(self.content_frame, text="🛠 Tools", font=("Arial", 16)).pack(pady=10)

        # Add tools buttons from BINGtalk_vertical
        tk.Button(self.content_frame, text="Time", width=25, height=2, bg="#f0f0f0").pack(pady=5)
        tk.Button(self.content_frame, text="Get Poem", width=25, height=2, bg="#f0f0f0").pack(pady=5)

        # Add CNN canvas section
        tk.Label(self.content_frame, text="✍ CNN Canvas", font=("Arial", 14)).pack(pady=10)
        self.canvas = tk.Canvas(self.content_frame, bg="white", width=200, height=200, relief="ridge", bd=2)
        self.canvas.pack(pady=5)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.prev_x = None
        self.prev_y = None

        # Add recognition buttons
        tk.Button(self.content_frame, text="识别", command=self.predict_drawing, width=20).pack(pady=5)
        tk.Button(self.content_frame, text="清空", command=self.clear_canvas, width=20).pack()

    def handle_poem(self):
        num = simpledialog.askinteger("Poem", "Enter sonnet number:")
        if num:
            self.send_command(f'p {num}')
            
    # New methods from BINGtalk_vertical
    def paint(self, event):
        if self.prev_x and self.prev_y:
            self.canvas.create_line(self.prev_x, self.prev_y, event.x, event.y, width=5)
        self.prev_x = event.x
        self.prev_y = event.y

    def clear_canvas(self):
        self.canvas.delete("all")
        self.prev_x = None
        self.prev_y = None

    def predict_drawing(self):
        print("👉 Simulating recognition (potential CNN structure attached)")


if __name__ == "__main__":
    app = BINGtalkStyledApp()
    app.mainloop()
