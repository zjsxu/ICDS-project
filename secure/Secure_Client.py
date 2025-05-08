import socket
import time
import sys
from secure_client_state_machine import SecureClientSM
from chat_utils import *
import json
import threading
import select

class SecureClient:
    def __init__(self, args):
        self.peer = ''
        self.console_input = []
        self.state = S_OFFLINE
        self.system_msg = ''
        self.local_msg = ''
        self.peer_msg = ''
        self.args = args
        
    def quit(self):
        self.socket.close()

    def init_chat(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        svr = SERVER if self.args.d == None else (self.args.d, CHAT_PORT)
        self.socket.connect(svr)
        self.sm = SecureClientSM(self.socket)
        reading_thread = threading.Thread(target=self.read_input)
        reading_thread.daemon = True
        reading_thread.start()

    def shutdown_chat(self):
        return

    def send(self, msg):
        mysend(self.socket, msg)

    def recv(self):
        return myrecv(self.socket)

    def get_name(self):
        return self.sm.get_myname()

    def proc(self):
        my_msg, peer_msg = self.get_msgs()
        self.system_msg += self.sm.proc(my_msg, peer_msg)
        self.output()
        time.sleep(CHAT_WAIT)

    def get_msgs(self):
        read, write, error = select.select([self.socket], [], [], 0)
        my_msg = ''
        peer_msg = ''
        if self.socket in read:
            peer_msg = self.recv()
        if len(self.console_input) > 0:
            my_msg = self.console_input.pop(0)
        return my_msg, peer_msg

    def output(self):
        if len(self.system_msg) > 0:
            print(self.system_msg)
            self.system_msg = ''

    def login(self):
        my_msg, peer_msg = self.get_msgs()
        if len(my_msg) > 0:
            self.name = my_msg
            msg = json.dumps({"action":"login", "name":self.name, "public_key":self.sm.get_public_key()})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == "ok":
                self.state = S_LOGGEDIN
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(self.name)
                self.print_instructions()
                return True
            elif response["status"] == "duplicate":
                self.system_msg += 'Duplicate username, try again'
                return False
        else:
            self.system_msg += 'Please enter your name: '
        return False

    def read_input(self):
        while True:
            text = sys.stdin.readline()[:-1]
            self.console_input.append(text) 

    def print_instructions(self):
        self.system_msg += menu

    def run_chat(self):
        self.init_chat()
        
        self.system_msg += 'Welcome to the Secure BINGtalk\n'
        self.system_msg += 'Please enter your name: '
        self.output()
        
        while self.login() != True:
            self.output()
        
        self.system_msg += 'Welcome, ' + self.get_name() + '!\n'
        self.system_msg += 'Encryption is enabled by default.\n'
        self.system_msg += 'Use "encrypt on/off" to toggle encryption.\n'
        self.output()
        
        while self.sm.get_state() != S_OFFLINE:
            self.proc()
            
        self.quit()

# Main function
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Secure chat client')
    parser.add_argument('-d', type=str, default=None, help='server IP addr')
    args = parser.parse_args()

    client = SecureClient(args)
    client.run_chat()
