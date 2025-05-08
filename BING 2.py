import tkinter as tk
from PIL import Image, ImageTk
import os
import requests, io, base64
import tkinter.messagebox as messagebox
import os
import sys
import subprocess
import threading
import time
import webbrowser



class BINGtalkStyledApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BINGTalk Styled GUI")
        self.geometry("1000x600")
        self.configure(bg="#f5f7fa")

        self.sidebar_width = 160

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.icons = {}
        self.load_icons()
        self.create_topbar()
        self.create_sidebar()
        self.create_main_area()

    def load_icons(self):
        icon_names = ["chat", "tools", "logo"]  # 添加 logo
        for name in icon_names:
            path = os.path.join("/Users/zhangjingsen/Desktop/cursor/coursenotes/project/tryout5/icons", f"{name}.png")
            try:
                image = Image.open(path).resize((20, 20) if name != "logo" else (40, 40), Image.Resampling.LANCZOS)
                self.icons[name] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"❌ Failed to load icon {name}: {e}")
                self.icons[name] = None

    def create_topbar(self):
        topbar = tk.Frame(self, height=60, bg="#3c8dbc")
        topbar.grid(row=0, column=0, columnspan=2, sticky="new")

        if self.icons.get("logo"):
            tk.Label(topbar, image=self.icons["logo"], bg="#3c8dbc").pack(side="left", padx=(10, 5), pady=10)

        tk.Label(topbar, text="BINGTalk Simulation System", font=("Helvetica", 16), fg="white", bg="#3c8dbc").pack(side="left", pady=10)


    def create_sidebar(self):
        self.sidebar = tk.Frame(self, width=self.sidebar_width, bg="#ecf0f1")
        self.sidebar.grid(row=1, column=0, sticky="ns")

        buttons = [
            ("Chat", self.icons.get("chat"), self.show_chat),
            ("Tools", self.icons.get("tools"), self.show_tools),
        ]

        for label, icon, command in buttons:
            btn = tk.Button(
                self.sidebar,
                text=f"  {label}",
                image=icon,
                compound="left",
                font=("Arial", 12),
                anchor="w",
                bg="#ecf0f1",
                relief="flat",
                command=command
            )
            btn.pack(fill="x", pady=10, padx=10)

    def create_main_area(self):
        self.main_area = tk.Frame(self, bg="#f5f7fa")
        self.main_area.grid(row=1, column=1, sticky="nsew")
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

        self.content_frame = tk.Frame(self.main_area, bg="#ffffff", padx=20, pady=20, bd=1, relief="solid")
        self.content_frame.grid(row=0, column=0, sticky="nsew")

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_chat(self):
        self.clear_content()
        tk.Label(self.content_frame, text="📨 Chat zone", font=("Arial", 16)).pack(pady=10)
        for label in ["Chat", "Search", "Who", "Connect", "Disconnect"]:
            tk.Button(self.content_frame, text=label, width=25, height=2, bg="#f0f0f0").pack(pady=5)

    def show_tools(self):
        self.clear_content()
        tk.Label(self.content_frame, text="🛠 toolkit", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.content_frame, text="Time", width=25, height=2, bg="#f0f0f0").pack(pady=5)
        tk.Button(self.content_frame, text="Get Poem", width=25, height=2, bg="#f0f0f0").pack(pady=5)

        # CNN canvas 区
        tk.Label(self.content_frame, text="✍ CNN canva", font=("Arial", 14)).pack(pady=10)
        self.canvas = tk.Canvas(self.content_frame, bg="white", width=200, height=200, relief="ridge", bd=2)
        self.canvas.pack(pady=5)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.prev_x = None
        self.prev_y = None

        tk.Button(self.content_frame, text="识别", command=self.predict_drawing, width=20).pack(pady=5)
        tk.Button(self.content_frame, text="清空", command=self.clear_canvas, width=20).pack()
        tk.Button(self.content_frame, text="🌐 打开网页版识别", command=self.launch_web_recognizer, width=25, height=2, bg="#d0eaff").pack(pady=10)

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
        self.canvas.update()
        ps = self.canvas.postscript(colormode='mono')
        img = Image.open(io.BytesIO(ps.encode('utf-8'))).convert('L')
        img = img.resize((28, 28), Image.LANCZOS)
        # 2. 转为 base64 PNG
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        img_uri = f"data:image/png;base64,{img_b64}"

        # 3. 发出 POST 请求给 Flask API
        try:
            res = requests.post(
                url="http://127.0.0.1:5000/predict",
                json={"image": img_uri}
            )
            res.raise_for_status()
            data = res.json()
            label = data["label"]
            probs = data["probabilities"]

            # 4. 在 GUI 中显示结果
            tk.messagebox.showinfo("识别结果", f"预测数字为：{label}")
        except Exception as e:
            tk.messagebox.showerror("识别失败", f"错误信息：{e}")

    def create_sidebar(self):
        self.sidebar = tk.Frame(self, width=self.sidebar_width, bg="#ecf0f1")
        self.sidebar.grid(row=1, column=0, sticky="ns")

        buttons = [
            ("Chat", self.icons.get("chat"), self.show_chat),
            ("Secure Chat", self.icons.get("chat"), self.show_secure_chat),  # Add secure chat option
            ("Tools", self.icons.get("tools"), self.show_tools),
        ]

        for label, icon, command in buttons:
            btn = tk.Button(
                self.sidebar,
                text=f"  {label}",
                image=icon,
                compound="left",
                font=("Arial", 12),
                anchor="w",
                bg="#ecf0f1",
                relief="flat",
                command=command
            )
            btn.pack(fill="x", pady=10, padx=10)

    # Add a method to show the secure chat interface
    def show_secure_chat(self):
        # Import and initialize the secure chat interface
        from secure_bingtalk_gui import SecureBINGtalkApp
        secure_chat = SecureBINGtalkApp()
        secure_chat.mainloop()
    def launch_web_recognizer(self):
        """启动 Flask 服务器并打开浏览器访问"""
        def run():
            os.chdir('/Users/justinbian/PycharmProjects/hand_written_digit_recognition_CNN/flask_api')  # 修改为你的 app.py 所在目录
            subprocess.call([sys.executable, 'app.py'])

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        time.sleep(1.5)  # 等待服务器启动
        webbrowser.open('http://127.0.0.1:5000/')

import requests
import base64
import io

def predict_drawing(self):
    # 1. 截取 canvas 区域为 PIL 图像
    self.canvas.update()
    ps = self.canvas.postscript(colormode='mono')
    img = Image.open(io.BytesIO(ps.encode('utf-8'))).convert('L')
    img = img.resize((28, 28), Image.LANCZOS)

    # 2. 转为 base64 PNG
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    img_uri = f"data:image/png;base64,{img_b64}"

    # 3. 发出 POST 请求给 Flask API
    try:
        res = requests.post(
            url="http://127.0.0.1:5000/predict",
            json={"image": img_uri}
        )
        res.raise_for_status()
        data = res.json()
        label = data["label"]
        probs = data["probabilities"]

        # 4. 在 GUI 中显示结果
        tk.messagebox.showinfo("识别结果", f"预测数字为：{label}")
    except Exception as e:
        tk.messagebox.showerror("识别失败", f"错误信息：{e}")


if __name__ == "__main__":
    app = BINGtalkStyledApp()
    app.mainloop()
