# Inside the create_sidebar method, add a secure chat button:
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
