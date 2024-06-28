import os
from dotenv import load_dotenv
import pystray          # type: ignore
import PIL.Image        # type: ignore
from azure_tts import AzureTTSManager
from twitchio.ext import commands
import sys
from pynput import keyboard
import threading

tts_toggle = True

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=os.getenv('ACCESS_TOKEN'), prefix='!', initial_channels=['Turtletoofast'])

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
    
    async def event_message(self, message):
        if message.author is not None:
            print(message.author.name, message.content)
            if tts_toggle:
                AzureTTSManager.text_to_speech(message.content, message.author.name)
            await self.handle_commands(message)

    @commands.command()
    async def prefix(self, ctx: commands.Context):
        await ctx.send("avaliable prefixes are: angry, cheerful, excited, hopeful, sad, shouting, terrified, unfriendly, whispering")



#####################################
#     KEYBOARD LISTENER STUFF       #
#####################################

# The key combination to check
COMBINATION1 = {keyboard.Key.f8, keyboard.Key.ctrl_l}         # turn off TTS
COMBINATION2 = {keyboard.Key.f12, keyboard.Key.ctrl_l}        # Shut down keyboard thread

# The currently active modifiers
current = set()

def on_press(key):
    global tts_toggle       
    if key in COMBINATION1:
        current.add(key)
        if all (k in current for k in COMBINATION1):
            tts_toggle = not tts_toggle
            print(f"TTS Toggle is now {'on' if tts_toggle else 'off'}")
    
    if key in COMBINATION2:
        current.add(key)
        if all (k in current for k in COMBINATION2):
            return False

def on_release(key):
    try:
        current.remove(key)
    except KeyError:
        pass
        
def start_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def main():
    load_dotenv()
    sys.stdout.reconfigure(line_buffering=True)         # Load script with print('', flush=True)
    sys.stdout.reconfigure(encoding='utf-8')            # Use utf-8 encoding
    bot = Bot()
    bot.run()

# Sets up the script to be appearable in the system tray when running
def setup_system_tray():
    image = PIL.Image.open("icon.png")
    
    # Define the action to be taken on clicking 'Exit'
    def on_clicked(icon, item):
        icon.stop()  # This stops the system tray icon's loop
        print("Terminating...", flush=True)
        os._exit(0)  # Terminate
    
    # Set up the system tray icon with the menu
    icon = pystray.Icon("Twitch Bot", image, menu=pystray.Menu(pystray.MenuItem("Exit", on_clicked)))
    icon.run()

if __name__ == '__main__':
    ## System Tray handling (optional)
    # tray_thread = threading.Thread(target=setup_system_tray)
    # tray_thread.start()

    ## Keyboard Reading (optional)
    # keyboard_thread = threading.Thread(target=start_listener)
    # keyboard_thread.start()
    main()
    