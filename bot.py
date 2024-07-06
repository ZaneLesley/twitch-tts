import os
from dotenv import load_dotenv
import pystray          # type: ignore
import PIL.Image        # type: ignore
from azure_tts import AzureTTSManager
from obs_socket import OBSSocketManager
from twitchio.ext import commands
import sys
from pynput import keyboard
import threading
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit
import asyncio
from time import sleep
from rich import print
import random
from datetime import timedelta, datetime
import pytz
from voices_manager import TTSManager

# Global Variables
tts_toggle = True

#########################
#       Socket IO       #
#########################
app = Flask(__name__)
socketio = SocketIO(app, async_mode ="threading")
try:
    obs_manager = OBSSocketManager()
except Exception as e:
    print(f"[red]{e}")

@app.route("/")
def home():
    return render_template('index.html') #redirects to index.html in templates folder

@socketio.event
def connect(): #when socket connects, send data confirming connection
    socketio.emit('message_send', {'message': "Connected successfully!", 'current_user': "Temp User", 'user_number': "1"})

@socketio.on("tts")
def toggletts(value):
    print("TTS: Received the value " + str(value['checked']))
    if value['user_number'] == "1":
        bot.tts_enabled_1 = value['checked']
    elif value['user_number'] == "2":
        bot.tts_enabled_2 = value['checked']
    elif value['user_number'] == "3":
        bot.tts_enabled_3 = value['checked']

@socketio.on("pickrandom")
def pickrandom(value):
    bot.randomUser(value['user_number'])
    print("Getting new random user for user " + value['user_number'])

@socketio.on("choose")
def chooseuser(value):
    if value['user_number'] == "1":
        bot.current_user_1 = value['chosen_user'].lower()
        socketio.emit('message_send',
            {'message': f"{bot.current_user_1} was picked!",
            'current_user': f"{bot.current_user_1}",
            'user_number': value['user_number']})
    elif value['user_number'] == "2":
        bot.current_user_2 = value['chosen_user'].lower()
        socketio.emit('message_send',
            {'message': f"{bot.current_user_2} was picked!",
            'current_user': f"{bot.current_user_2}",
            'user_number': value['user_number']})
    elif value['user_number'] == "3":
        bot.current_user_3 = value['chosen_user'].lower()
        socketio.emit('message_send',
            {'message': f"{bot.current_user_3} was picked!",
            'current_user': f"{bot.current_user_3}",
            'user_number': value['user_number']})

@socketio.on("voicename")
def choose_voice_name(value):
    if (value['voice_name']) != None:
        bot.update_voice_name(value['user_number'], value['voice_name'])
        print("Updating voice name to: " + value['voice_name'])

@socketio.on("voicestyle")
def choose_voice_style(value):
    if (value['voice_style']) != None:
        bot.update_voice_style(value['user_number'], value['voice_style'])
        print("Updating voice style to: " + value['voice_style'])



class Bot(commands.Bot):
    current_user_1 = None
    current_user_2 = None
    current_user_3 = None
    tts_enabled_1 = True
    tts_enabled_2 = True
    tts_enabled_3 = True
    keypassphrase_1 = "!player1"
    keypassphrase_2 = "!player2"
    keypassphrase_3 = "!player3"
    user_pool_1 = {} #dict of username and time last chatted
    user_pool_2 = {} #dict of username and time last chatted
    user_pool_3 = {} #dict of username and time last chatted
    seconds_active = 450 # of seconds until a chatter is booted from the list
    max_users = 2000 # of users who can be in user pool
    tts_manager = None

    def __init__(self):
        super().__init__(token=os.getenv('ACCESS_TOKEN'), prefix='!', initial_channels=['Turtletoofast'])
        self.tts_manager = TTSManager()

    async def event_ready(self):
        print(f'[green]Logged in as | {self.nick}')
    
    async def event_message(self, message):
        if message.author is not None:
            print(message.author.name, message.content)
            if tts_toggle and not message.content.startswith('!'):
                obs_manager.set_text(source_name="weinerText", new_text=message.content)
                AzureTTSManager.text_to_speech(message.content, message.author.name)
            await self.handle_commands(message)

    @commands.command()
    async def prefix(self, ctx: commands.Context):
        await ctx.send("avaliable prefixes are: angry, cheerful, excited, hopeful, sad, shouting, terrified, unfriendly, whispering")

    # Doug Doug Code
    async def process_message(self, message):
        # print("We got a message from this person: " + message.author.name)
        # print("Their message was " + message.content)

        # If this is our current_user, read out their message
        if message.author.name == self.current_user_1:
            socketio.emit('message_send',
                {'message': f"{message.content}",
                'current_user': f"{self.current_user_1}",
                'user_number': "1"})
            if self.tts_enabled_1:
                self.tts_manager.text_to_audio(message.content, "1")
        elif message.author.name == self.current_user_2:
            socketio.emit('message_send',
                {'message': f"{message.content}",
                'current_user': f"{self.current_user_2}",
                'user_number': "2"})
            if self.tts_enabled_2:
                self.tts_manager.text_to_audio(message.content, "2")
        elif message.author.name == self.current_user_3:
            socketio.emit('message_send',
                {'message': f"{message.content}",
                'current_user': f"{self.current_user_3}",
                'user_number': "3"})
            if self.tts_enabled_3:
                self.tts_manager.text_to_audio(message.content, "3")

        # Add this chatter to the user_pool
        if message.content == self.keypassphrase_1:
            if message.author.name.lower() in self.user_pool_1: # Remove this chatter from pool if they're already there
                self.user_pool_1.pop(message.author.name.lower())
            self.user_pool_1[message.author.name.lower()] = message.timestamp # Add user to end of pool with new msg time
            # Now we remove the oldest viewer if they're past the activity threshold, or if we're past the max # of users
            activity_threshold = datetime.now(pytz.utc) - timedelta(seconds=self.seconds_active) # calculate the cutoff time
            oldest_user = list(self.user_pool_1.keys())[0] # The first user in the dict is the user who chatted longest ago
            if self.user_pool_1[oldest_user].replace(tzinfo=pytz.utc) < activity_threshold or len(self.user_pool_1) > self.max_users:
                self.user_pool_1.pop(oldest_user) # remove them from the list
                if len(self.user_pool_1) == self.max_users:
                    print(f"{oldest_user} was popped due to hitting max users")
                else:
                    print(f"{oldest_user} was popped due to not talking for {self.seconds_active} seconds")
        elif message.content == self.keypassphrase_2:
            if message.author.name.lower() in self.user_pool_2: # Remove this chatter from pool if they're already there
                self.user_pool_2.pop(message.author.name.lower())
            self.user_pool_2[message.author.name.lower()] = message.timestamp # Add user to end of pool with new msg time
            # Now we remove the oldest viewer if they're past the activity threshold, or if we're past the max # of users
            activity_threshold = datetime.now(pytz.utc) - timedelta(seconds=self.seconds_active) # calculate the cutoff time
            oldest_user = list(self.user_pool_2.keys())[0] # The first user in the dict is the user who chatted longest ago
            if self.user_pool_2[oldest_user].replace(tzinfo=pytz.utc) < activity_threshold or len(self.user_pool_2) > self.max_users:
                self.user_pool_2.pop(oldest_user) # remove them from the list
                if len(self.user_pool_2) == self.max_users:
                    print(f"{oldest_user} was popped due to hitting max users")
                else:
                    print(f"{oldest_user} was popped due to not talking for {self.seconds_active} seconds")
        elif message.content == self.keypassphrase_3:
            if message.author.name.lower() in self.user_pool_3: # Remove this chatter from pool if they're already there
                self.user_pool_3.pop(message.author.name.lower())
            self.user_pool_3[message.author.name.lower()] = message.timestamp # Add user to end of pool with new msg time
            # Now we remove the oldest viewer if they're past the activity threshold, or if we're past the max # of users
            activity_threshold = datetime.now(pytz.utc) - timedelta(seconds=self.seconds_active) # calculate the cutoff time
            oldest_user = list(self.user_pool_3.keys())[0] # The first user in the dict is the user who chatted longest ago
            if self.user_pool_3[oldest_user].replace(tzinfo=pytz.utc) < activity_threshold or len(self.user_pool_3) > self.max_users:
                self.user_pool_3.pop(oldest_user) # remove them from the list
                if len(self.user_pool_3) == self.max_users:
                    print(f"{oldest_user} was popped due to hitting max users")
                else:
                    print(f"{oldest_user} was popped due to not talking for {self.seconds_active} seconds")
                
                
    #picks a random user from the queue
    def randomUser(self, user_number):
        try:
            if user_number == "1":
                self.current_user_1 = random.choice(list(self.user_pool_1.keys()))
                socketio.emit('message_send',
                    {'message': f"{self.current_user_1} was picked!",
                    'current_user': f"{self.current_user_1}",
                    'user_number': user_number})
                print("Random User is: " + self.current_user_1)
            elif user_number == "2":
                self.current_user_2 = random.choice(list(self.user_pool_2.keys()))
                socketio.emit('message_send',
                    {'message': f"{self.current_user_2} was picked!",
                    'current_user': f"{self.current_user_2}",
                    'user_number': user_number})
                print("Random User is: " + self.current_user_2)
            elif user_number == "3":
                self.current_user_3 = random.choice(list(self.user_pool_3.keys()))
                socketio.emit('message_send',
                    {'message': f"{self.current_user_3} was picked!",
                    'current_user': f"{self.current_user_3}",
                    'user_number': user_number})
                print("Random User is: " + self.current_user_3)
        except Exception:
            return

    def update_voice_name(self, user_number, voice_name):
        self.tts_manager.update_voice_name(user_number, voice_name)

    def update_voice_style(self, user_number, voice_style):
        self.tts_manager.update_voice_style(user_number, voice_style)



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

def start_bot():
    global bot
    sys.stdout.reconfigure(line_buffering=True)         # Load script with print('', flush=True)
    sys.stdout.reconfigure(encoding='utf-8')            # Use utf-8 encoding
    asyncio.set_event_loop(asyncio.new_event_loop())
    bot = Bot()
    bot.run()

# Sets up the script to be appearable in the system tray when running
def setup_system_tray():
    image = PIL.Image.open("icon.png")
    
    # Define the action to be taken on clicking 'Exit'
    def on_clicked(icon, item):
        icon.stop()  # This stops the system tray icon's loop
        print("[red]Terminating...", flush=True)
        os._exit(0)  # Terminate
    
    # Set up the system tray icon with the menu
    icon = pystray.Icon("Twitch Bot", image, menu=pystray.Menu(pystray.MenuItem("Exit", on_clicked)))
    icon.run()

if __name__ == '__main__':
    ## System Tray handling (optional)
    tray_thread = threading.Thread(target=setup_system_tray)
    tray_thread.name = 'system_tray'
    tray_thread.start()

    ## Keyboard Reading (optional)
    # keyboard_thread = threading.Thread(target=start_listener)
    # keyboard_thread.start()
    
    load_dotenv()
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.name = 'bot'
    bot_thread.start()
    socketio.run(app, allow_unsafe_werkzeug=True, port=8000)
    