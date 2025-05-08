"""
Enhanced version of chat_server.py with support for encryption
"""

import time
import socket
import select
import sys
import string
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp
import indexer


class SecureServer:
    def __init__(self):
        self.new_clients = []  # list of new sockets of which the user id is not known
        self.logged_name2sock = {}  # dictionary mapping username to socket
        self.logged_sock2name = {}  # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        
        # start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        
        # initialize past chat indices
        self.indices = {}
        
        # sonnet
        self.sonnet = indexer.PIndex("AllSonnets.txt")
        
        # Store public keys for encryption
        self.public_keys = {}  # username -> public_key
        
        # Store unencrypted messages for searching
        self.plain_messages = []  # [{from, content, timestamp}]
        
        print('Secure Server initialized')

    def new_client(self, sock):
        # add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        # read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            if len(msg) > 0:
                if msg["action"] == "login":
                    name = msg["name"]
                    
                    # Store public key if provided
                    if "public_key" in msg:
                        self.public_keys[name] = msg["public_key"]
                        print(f"Received public key from {name}")
                    
                    if not self.group.is_member(name):
                        # move socket from new clients list to logged clients
                        self.new_clients.remove(sock)
                        # add into the name to sock mapping
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        # load chat history of that user
                        if name not in self.indices.keys():
                            try:
                                self.indices[name] = pkl.load(
                                    open(name + '.idx', 'rb'))
                            except IOError:  # chat index does not exist, then create one
                                self.indices[name] = indexer.Index(name)
                        print(name + ' logged in')
                        self.group.join(name)
                        
                        # Create login response
                        login_response = {"action": "login", "status": "ok"}
                        
                        # Add public keys of other users if requested
                        if "get_public_keys" in msg and msg["get_public_keys"]:
                            login_response["public_keys"] = self.public_keys
                            
                        mysend(sock, json.dumps(login_response))
                    else:  # a client under this name has already logged in
                        mysend(sock, json.dumps(
                            {"action": "login", "status": "duplicate"}))
                        print(name + ' duplicate login attempt')
                else:
                    print('wrong code received')
            else:  # client died unexpectedly
                self.logout(sock)
        except Exception as e:
            print(f"Error in login: {str(e)}")
            self.all_sockets.remove(sock)

    def logout(self, sock):
        # remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx', 'wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()
        
        # Keep the public key in case the user logs back in later
        # This prevents the need to re-exchange keys

    def handle_msg(self, from_sock):
        # read msg code
        msg = myrecv(from_sock)
        if len(msg) > 0:
            # ==============================================================================
            # handle connect request with public key exchange
            # ==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                
                # Update public key if provided
                if "public_key" in msg:
                    self.public_keys[from_name] = msg["public_key"]
                
                if to_name == from_name:
                    msg = json.dumps({"action": "connect", "status": "self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    
                    # Include the peer's public key in the success response
                    connect_response = {
                        "action": "connect", 
                        "status": "success"
                    }
                    
                    # Add peer's public key if available
                    if to_name in self.public_keys:
                        connect_response["peer_key"] = self.public_keys[to_name]
                    
                    msg = json.dumps(connect_response)
                    
                    # Notify other connected users about this connection with public key
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        
                        # Include public key in the connection notification
                        connect_notification = {
                            "action": "connect", 
                            "status": "request", 
                            "from": from_name
                        }
                        
                        # Add public key if available
                        if from_name in self.public_keys:
                            connect_notification["public_key"] = self.public_keys[from_name]
                        
                        mysend(to_sock, json.dumps(connect_notification))
                else:
                    msg = json.dumps(
                        {"action": "connect", "status": "no-user"})
                mysend(from_sock, msg)
# ==============================================================================
# handle encrypted or plain message exchange
# ==============================================================================
            elif msg["action"] == "exchange":
                from_name = self.logged_sock2name[from_sock]
                
                # Check if message is encrypted
                is_encrypted = "encrypted" in msg and msg["encrypted"]
                message_content = msg["message"]
                
                # Only index unencrypted messages for search functionality
                if not is_encrypted and self.indices.get(from_name, None) is not None:
                    # For plain text messages, add to the index for search
                    self.indices[from_name].add_msg(message_content)
                    
                    # Also store in plain messages history for search across users
                    self.plain_messages.append({
                        "from": from_name,
                        "content": message_content,
                        "timestamp": time.time()
                    })
                    
                    # Limit history size
                    if len(self.plain_messages) > 100:
                        self.plain_messages.pop(0)
                
                # Forward the message to all recipients in the group
                the_guys = self.group.list_me(from_name)[1:]
                for g in the_guys:
                    to_sock = self.logged_name2sock[g]
                    
                    # Create the forwarded message, preserving encryption status
                    forward_msg = {
                        "action": "exchange",
                        "from": msg["from"],
                        "message": message_content
                    }
                    
                    if is_encrypted:
                        forward_msg["encrypted"] = True
                    
                    mysend(to_sock, json.dumps(forward_msg))
# ==============================================================================
# handle disconnect request
# ==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps(
                        {"action": "disconnect", "msg": "everyone left, you are alone"}))
# ==============================================================================
# listing available peers with their public keys
# ==============================================================================
            elif msg["action"] == "list":
                # Regular user list from group
                msg = self.group.list_all()
                
                # Additional response with public keys if requested
                if "get_keys" in msg and msg["get_keys"]:
                    response = {
                        "action": "list", 
                        "results": msg,
                        "public_keys": self.public_keys
                    }
                    mysend(from_sock, json.dumps(response))
                else:
                    # Normal response
                    mysend(from_sock, json.dumps(
                        {"action": "list", "results": msg}))
# ==============================================================================
# search functionality adapted for encrypted systems
# ==============================================================================
            elif msg["action"] == "search":
                term = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                
                # Search results list
                search_rslt = []
                
                # Search in user's indexed messages
                if self.indices.get(from_name, None) is not None:
                    search_rslt = self.indices[from_name].search(term)
                
                # If "search_all" option is enabled, search in all unencrypted messages
                if "search_all" in msg and msg["search_all"]:
                    # Search in the plain_messages list
                    for plain_msg in self.plain_messages:
                        if term.lower() in plain_msg["content"].lower():
                            search_item = (f'{plain_msg["from"]}', plain_msg["content"])
                            if search_item not in search_rslt:
                                search_rslt.append(search_item)
                
                print(f'Search for "{term}": {len(search_rslt)} results')
                mysend(from_sock, json.dumps(
                    {"action": "search", "results": search_rslt}))
# ==============================================================================
# sonnet retrieval
# ==============================================================================
            elif msg["action"] == "poem":
                poem_idx = msg["target"]
                poem = self.sonnet.get_poem(poem_idx)
                print(f'Retrieving poem {poem_idx}')
                mysend(from_sock, json.dumps(
                    {"action": "poem", "results": poem}))
# ==============================================================================
# time
# ==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps(
                    {"action": "time", "results": ctime}))
# ==============================================================================
# request public keys
# ==============================================================================
            elif msg["action"] == "get_keys":
                # Send all public keys to the requesting client
                mysend(from_sock, json.dumps({
                    "action": "public_keys",
                    "keys": self.public_keys
                }))
                
        else:
            # client died unexpectedly
            self.logout(from_sock)

    def run(self):
        print('starting secure server...')
        while(1):
            read, write, error = select.select(self.all_sockets, [], [])
            print('checking logged clients..')
            for logc in list(self.logged_name2sock.values()):
                if logc in read:
                    self.handle_msg(logc)
            print('checking new clients..')
            for newc in self.new_clients[:]:
                if newc in read:
                    self.login(newc)
            print('checking for new connections..')
            if self.server in read:
                # new client request
                sock, address = self.server.accept()
                self.new_client(sock)


def main():
    server = SecureServer()
    server.run()


if __name__ == '__main__':
    main()
