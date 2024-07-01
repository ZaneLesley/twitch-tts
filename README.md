# twitch-tts

This is an application made for twitch that will allow the user to talk with twitch chat with their messages showing as TTS on screen. The user will be able to select how many characters 
should be allowed on screen at any given time. 

## Technical About 
The main script runs through the bot.py file. It will create seperate threads that each component of the app will run on. One thread handles twitch chat, one thread handles the localhost server, and
one thread will handle system tray management (allowing you to know when and exit the program from the system tray.)

Customazation will mainly be done in the obs_socket.py file, bot.py file, and the azure_tts.py file. (TODO Explain each)

The get_device_id.py file is a utility file that can help you find your audio device IDs to plug into the azure_tts.py file.

## Usage
TODO

## Requirements
(TODO)