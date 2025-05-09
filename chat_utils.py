import socket
import time


# use local loop back address by default
#For Server Holder:
#CHAT_IP = socket.gethostbyname(socket.gethostname()) #returns '10.209.86.65' on my computer ---Phil

#For Client Runners:
# CHAT_IP = "10.209.91.36" # the IP of Justin's laptop

CHAT_PORT = 1112
# SERVER = (CHAT_IP, CHAT_PORT)
SERVER = ('127.0.0.1', 12345)

menu = "\n++++ Choose one of the following commands ++++\n \
        time: calendar time in the system\n \
        who: to find out who else are there\n \
        connect _peer_: to connect to the _peer_ and chat\n \
        ? _term_: to search your chat logs where _term_ appears\n \
        p _#_: to get number <#> sonnet\n \
        chess: to play a multiplayer chess game\n \
        create ttt room ***: to create a tic-tac-toe game at room ***\n \
        join ttt room ***: to join tic-tac-toe game at room ***\n \
        ps: room number is 1 to 999 \n \
        q: to leave the chat system\n\n" #The menu has been modified ---Phil

S_OFFLINE = 0
S_CONNECTED = 1
S_LOGGEDIN = 2
S_CHATTING = 3

SIZE_SPEC = 5

CHAT_WAIT = 0.2


def print_state(state):
    print('**** State *****::::: ')
    if state == S_OFFLINE:
        print('Offline')
    elif state == S_CONNECTED:
        print('Connected')
    elif state == S_LOGGEDIN:
        print('Logged in')
    elif state == S_CHATTING:
        print('Chatting')
    else:
        print('Error: wrong state')


def mysend(s, msg):
    # append size to message and send it
    msg = ('0' * SIZE_SPEC + str(len(msg)))[-SIZE_SPEC:] + str(msg)
    msg = msg.encode()
    total_sent = 0
    while total_sent < len(msg):
        sent = s.send(msg[total_sent:])
        if sent == 0:
            print('server disconnected')
            break
        total_sent += sent

def myrecv(s):
    # receive size first
    size = ''
    while len(size) < SIZE_SPEC:
        text = s.recv(SIZE_SPEC - len(size)).decode()
        if not text:
            print('disconnected')
            return('')
        size += text
    size = int(size)
    # now receive message
    msg = ''
    while len(msg) < size:
        text = s.recv(size-len(msg)).decode()
        if text == b'':
            print('disconnected')
            break
        msg += text
    #print ('received '+message)
    return (msg)


def text_proc(text, user):
    ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
    # message goes directly to screen
    return('(' + ctime + ') ' + user + ' : ' + text)
