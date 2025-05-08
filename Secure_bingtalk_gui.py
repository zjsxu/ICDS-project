 def receive_messages(self):
        """Thread function to receive and process messages from the server"""
        while self.receiving_active and self.socket:
            try:
                read, _, _ = select.select([self.socket], [], [], 0.1)
                
                if self.socket in read:
                    msg = myrecv(self.socket)
                    if len(msg) > 0:
                        self.process_incoming_message(msg)
                    else:
                        # Connection closed by server
                        self.log_message("Disconnected from server")
                        self.reset_connection_ui()
                        break
            except Exception as e:
                self.log_message(f"Error receiving message: {str(e)}")
                self.reset_connection_ui()
                break
    
    def process_incoming_message(self, msg):
        """Process a message received from the server"""
        try:
            msg = json.loads(msg)
            
            if msg["action"] == "connect" and msg["status"] == "request":
                # Someone wants to connect to us
                from_name = msg["from"]
                
                # Store public key if provided
                if "public_key" in msg:
                    self.rsa.add_public_key(from_name, tuple(msg["public_key"]))
                    
                self.log_message(f"Connection request from {from_name}")
                self.log_message(f"You are now chatting with {from_name}")
                self.status_label.config(text=f"Chatting with {from_name}", fg="blue")
                self.state = S_CHATTING
                self.peer = from_name
                
            elif msg["action"] == "list":
                # Update user list
                users_info = msg["results"]
                self.update_user_list(users_info)
                
            elif msg["action"] == "time":
                time_info = msg["results"]
                self.log_message(f"Server time: {time_info}")
                
            elif msg["action"] == "search":
                results = msg["results"]
                if results:
                    self.log_message(f"Search results:")
                    for result in results:
                        self.log_message(f"- {result}")
                else:
                    self.log_message("No results found")
                    
            elif msg["action"] == "disconnect":
                self.log_message("Chat disconnected")
                if "msg" in msg:
                    self.log_message(msg["msg"])
                self.state = S_LOGGEDIN
                self.peer = ""
                self.status_label.config(text="Logged in", fg="green")
                
            elif msg["action"] == "exchange":
                from_name = msg["from"]
                
                # Handle encrypted messages
                if "encrypted" in msg and msg["encrypted"]:
                    try:
                        encrypted_msg = msg["message"]
                        decrypted_msg = self.rsa.decrypt(encrypted_msg)
                        self.log_message(f"{from_name} [Encrypted]: {decrypted_msg}")
                    except Exception as e:
                        self.log_message(f"Failed to decrypt message from {from_name}: {str(e)}")
                else:
                    # Regular unencrypted message
                    message = msg["message"]
                    self.log_message(f"{from_name}: {message}")
                    
            else:
                # Other messages
                self.log_message(f"Received: {msg}")
                
        except Exception as e:
            self.log_message(f"Error processing message: {str(e)}")
    
    def update_user_list(self, users_info):
        """Update the list of online users"""
        # Parse the users info string
        # This is a simple parser for the format in your existing Group.list_all method
        try:
            # Clear current list
            self.user_list.delete(0, tk.END)
            
            # Extract usernames from the users_info string
            users_section = users_info.split("Users: ------------\n")[1].split("\n")[0]
            users_dict = eval(users_section)
            
            # Add online users to the listbox (except self)
            for user in users_dict:
                if user != self.username:
                    self.user_list.insert(tk.END, user)
                    
            self.log_message(f"Updated user list: {len(users_dict)} users online")
        except Exception as e:
            self.log_message(f"Error updating user list: {str(e)}")
    
    def on_user_select(self, event):
        """Handle user selection from the list"""
        if self.state != S_LOGGEDIN:
            return
            
        selection = self.user_list.curselection()
        if selection:
            selected_user = self.user_list.get(selection[0])
            
            # Ask for confirmation
            if messagebox.askyesno("Connect", f"Connect to {selected_user}?"):
                self.connect_to_peer(selected_user)
    
    def connect_to_peer(self, peer):
        """Connect to a chat peer"""
        if not self.socket or self.state != S_LOGGEDIN:
            self.log_message("You must be logged in to connect")
            return
            
        # Send connect request with public key
        connect_msg = json.dumps({
            "action": "connect",
            "target": peer,
            "public_key": self.rsa.public_key
        })
        
        mysend(self.socket, connect_msg)
        self.log_message(f"Connecting to {peer}...")
    
    def disconnect_from_peer(self):
        """Disconnect from current chat peer"""
        if not self.socket or self.state != S_CHATTING:
            return
            
        # Send disconnect message
        disconnect_msg = json.dumps({"action": "disconnect"})
        mysend(self.socket, disconnect_msg)
        
        self.state = S_LOGGEDIN
        self.peer = ""
        self.status_label.config(text="Logged in", fg="green")
        self.log_message("Disconnected from chat")
    
    def send_message(self):
        """Send a chat message"""
        if not self.socket:
            messagebox.showerror("Error", "Not connected to server")
            return
            
        if self.state != S_CHATTING:
            self.log_message("You must be in a chat to send messages")
            return
            
        message = self.msg_entry.get().strip()
        if not message:
            return
            
        # Check if we should encrypt the message
        if self.encryption_enabled and self.peer and self.peer in self.rsa.other_public_keys:
            # Encrypt the message
            try:
                encrypted_msg = self.rsa.encrypt_for_user(message, self.peer)
                
                # Send encrypted message
                msg_data = {
                    "action": "exchange",
                    "from": f"[{self.username}]",
                    "message": encrypted_msg,
                    "encrypted": True
                }
                
                mysend(self.socket, json.dumps(msg_data))
                self.log_message(f"[You encrypted]: {message}")
            except Exception as e:
                self.log_message(f"Encryption failed: {str(e)}")
                return
        else:
            # Send unencrypted message
            msg_data = {
                "action": "exchange",
                "from": f"[{self.username}]",
                "message": message
            }
            
            mysend(self.socket, json.dumps(msg_data))
            self.log_message(f"You: {message}")
        
        # Clear the input field
        self.msg_entry.delete(0, tk.END)
    
    def send_command(self, command):
        """Send a command to the server"""
        if not self.socket:
            messagebox.showerror("Error", "Not connected to server")
            return
            
        if command == "time":
            mysend(self.socket, json.dumps({"action": "time"}))
            
        elif command == "who":
            mysend(self.socket, json.dumps({"action": "list"}))
    
    def search_messages(self):
        """Search for messages"""
        if not self.socket:
            messagebox.showerror("Error", "Not connected to server")
            return
            
        search_term = self.search_entry.get().strip()
        if not search_term:
            return
            
        # Send search request
        search_msg = json.dumps({
            "action": "search",
            "target": search_term
        })
        
        mysend(self.socket, search_msg)
        self.log_message(f"Searching for: {search_term}")
    
    def toggle_encryption(self):
        """Toggle message encryption"""
        self.encryption_enabled = self.encrypt_var.get()
        status = "enabled" if self.encryption_enabled else "disabled"
        self.log_message(f"Encryption {status}")
    
    def reset_connection_ui(self):
        """Reset UI when disconnected"""
        self.socket = None
        self.state = S_OFFLINE
        self.peer = ""
        self.username = None
        self.receiving_active = False
        
        self.connect_btn.config(state=tk.NORMAL)
        self.username_entry.config(state=tk.NORMAL)
        self.server_entry.config(state=tk.NORMAL)
        self.port_entry.config(state=tk.NORMAL)
        self.status_label.config(text="Disconnected", fg="red")
        
        self.user_list.delete(0, tk.END)
    
    def quit(self):
        """Clean up before exiting"""
        if self.socket:
            self.receiving_active = False
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except:
                pass
        super().quit()

# Run the application
if __name__ == "__main__":
    app = SecureBINGtalkApp()
    app.mainloop()
