from chat_utils import *
import json
from encryption import RSA

class SecureClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        # Initialize RSA encryption
        self.rsa = RSA(key_size=512)  # Using smaller key size for demo
        self.encryption_enabled = True
        
    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name
        # Generate RSA keys when setting username
        self.public_key, self.private_key = self.rsa.generate_keys()

    def get_myname(self):
        return self.me
    
    def get_public_key(self):
        return self.rsa.public_key

    def connect_to(self, peer):
        # When connecting, include your public key
        msg = json.dumps({
            "action": "connect", 
            "target": peer,
            "public_key": self.rsa.public_key
        })
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            # If peer's public key is included in the response, store it
            if "peer_key" in response:
                self.rsa.add_public_key(peer, tuple(response["peer_key"]))
                self.out_msg += 'Secure channel established with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
        
        # Handle logged-in state
        if self.state == S_LOGGEDIN:
            if len(my_msg) > 0:
                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in
                
                elif my_msg[0:7] == 'encrypt':
                    # Toggle encryption
                    if my_msg[8:] == 'on':
                        self.encryption_enabled = True
                        self.out_msg += 'Encryption enabled\n'
                    elif my_msg[8:] == 'off':
                        self.encryption_enabled = False
                        self.out_msg += 'Encryption disabled\n'
                    else:
                        self.out_msg += 'Encryption status: ' + ('enabled' if self.encryption_enabled else 'disabled') + '\n'

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err:
                    self.out_msg += " json.loads failed " + str(err)
                    return self.out_msg
            
                if peer_msg["action"] == "connect":
                    # Handle connect request with public key exchange
                    from_name = peer_msg["from"]
                    if "public_key" in peer_msg:
                        # Store the peer's public key
                        self.rsa.add_public_key(from_name, tuple(peer_msg["public_key"]))
                        self.out_msg += 'Secure channel established with ' + from_name + '\n'
                    
                    self.out_msg += 'Request from ' + from_name + '\n'
                    self.out_msg += 'You are connected with ' + from_name + '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING
                    self.peer = from_name
                    
        # Handle chatting state
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                else:
                    # Determine whether to encrypt or not
                    if self.encryption_enabled and self.peer in self.rsa.other_public_keys:
                        # Encrypt the message
                        encrypted_msg = self.rsa.encrypt_for_user(my_msg, self.peer)
                        # Send encrypted message
                        mysend(self.s, json.dumps({
                            "action": "exchange",
                            "from": "[" + self.me + "]",
                            "message": encrypted_msg,
                            "encrypted": True
                        }))
                        # Show in UI that message was encrypted
                        self.out_msg += "[Encrypted] You: " + my_msg + '\n'
                    else:
                        # Send unencrypted message
                        mysend(self.s, json.dumps({
                            "action": "exchange",
                            "from": "[" + self.me + "]",
                            "message": my_msg
                        }))
                
            if len(peer_msg) > 0:    # peer's stuff, coming in
                try:
                    peer_msg = json.loads(peer_msg)
                    
                    if peer_msg["action"] == "connect":
                        from_name = peer_msg["from"]
                        # Store peer's public key if included
                        if "public_key" in peer_msg:
                            self.rsa.add_public_key(from_name, tuple(peer_msg["public_key"]))
                        self.out_msg += '(' + from_name + ' joined)\n'
                        
                    elif peer_msg["action"] == "disconnect":
                        if "msg" in peer_msg:
                            self.out_msg += peer_msg["msg"] + '\n'
                        else:
                            self.out_msg += "Everyone left, you are alone\n"
                        self.state = S_LOGGEDIN
                        self.peer = ''
                        
                    elif peer_msg["action"] == "exchange":
                        from_name = peer_msg["from"]
                        
                        # Check if message is encrypted
                        if "encrypted" in peer_msg and peer_msg["encrypted"]:
                            # Decrypt the message
                            try:
                                encrypted_msg = peer_msg["message"]
                                decrypted_msg = self.rsa.decrypt(encrypted_msg)
                                self.out_msg += from_name + ' ' + decrypted_msg + ' [Decrypted]\n'
                            except Exception as e:
                                self.out_msg += "Failed to decrypt message from " + from_name + ": " + str(e) + '\n'
                        else:
                            # Regular unencrypted message
                            message = peer_msg["message"]
                            self.out_msg += from_name + ' ' + message + '\n'
                            
                except Exception as err:
                    self.out_msg += " json.loads failed " + str(err)
                    print(err)
                
            # Display the menu again if returning to logged in state
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
                
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
