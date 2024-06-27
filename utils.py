from time import sleep

trivia_flag = False
resp = "Initilization Variable"

# Sends a message to twitch channel
def send_message(sock, channel, message):
    sock.send(f"PRIVMSG {channel} :{message}\n".encode('utf-8'))
    sleep(5)    #12 messages per minute 

def get_resp():
    return resp

def set_resp(arg):
    global resp
    resp = arg