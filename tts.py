import socket
import os
from dotenv import load_dotenv
import pystray          # type: ignore
import PIL.Image        # type: ignore
import threading
from azure_tts import AzureTTSManager
import re
import utils

def main():
    # Connection Variables
    load_dotenv()
    server = 'irc.chat.twitch.tv'
    port = 6667

    # Config stuff
    nickname = 'turtletoofast'              # Twich account name
    token = os.getenv('key')                # Auth key (in .env)
    channel = '#aiiboba'                    # Channel to monitor

    #################################
    #       Socket Connection       #
    #################################
    
    sock = socket.socket()

    print("connecting...", flush=True)
    sock.connect((server, port))
    print("connected", flush=True)

    sock.send(f"PASS {token}\n".encode('utf-8'))
    sock.send(f"NICK {nickname}\n".encode('utf-8'))
    sock.send(f"JOIN {channel}\n".encode('utf-8'))

    # Listener for twitch chat.
    while True:
        try:
            resp = sock.recv(2048).decode('utf-8')
            
            # Twitch apparently sends PING randomly, so just make sure we respond.
            if resp.startswith('PING'):
                sock.send("PONG\n".encode('utf-8'))
            
            # Switch Cases for commands
            elif(len(resp) > 0):
                try:
                    match = re.search(r'@(\w+)\.tmi', resp)
                    if match is not None and 'PRIVMSG' in resp:
                        user = match.group(1)
                        text = re.search(r' :(.*)', resp)
                        if(text.group(1).startswith('!')):
                            if "prefix" in text.group(1).lower():
                                utils.send_message(sock, channel, "avaliable prefixes are: angry, cheerful, excited, hopeful, sad, shouting, terrified, unfriendly, whispering")
                        else: 
                            AzureTTSManager.text_to_speech(text.group(1), user)  
                # Repeated messages give an error, just ignore it.
                except UnicodeEncodeError:
                    continue
        except socket.error:
            print("error connecting", flush=True)

# Sets up the script to be appearable in the system tray when running
def setup_system_tray():
    # Load the icon image
    image = PIL.Image.open("icon.png")
    
    # Define the action to be taken on clicking 'Exit'
    def on_clicked(icon, item):
        icon.stop()  # This stops the system tray icon's loop
        print("Terminating...", flush=True)
        os._exit(0)  # Terminate the program immediately with exit status 0
    
    # Set up the system tray icon with the menu
    icon = pystray.Icon("Twitch Bot", image, menu=pystray.Menu(pystray.MenuItem("Exit", on_clicked)))
    icon.run()

if __name__ == '__main__':
    #System Tray handling
    tray_thread = threading.Thread(target=setup_system_tray)
    tray_thread.start()
    main()