import time
import keyboard
from rich import print
import re
from azure_stt import AzureTTSManager
from openAI_connector import OpenAiManager
from obs_socket import OBSSocketManager
from elevenlabs_connector import ElevenLabsManager
from audio_manager import AudioManager

from language_exchange import replace_words

ELEVENLABS_VOICE = "Zane GR"

BACKUP_FILE = "CharacterHistoryBackup.txt"

try:
    print("[purple]Trying to connect to Azure TTS Manager")
    azure_stt_manager = AzureTTSManager()
    print("[green]Connected to Azure TTS Manager")
except Exception as e:
    print(f"[red]Couldn't connect to Azure TTS Manager: {e}")

try:
    print("[purple]Trying to connect to OBS Socket Manager")
    obs_manager = OBSSocketManager()
    print("[green]Connected to OBS Socket Manager")
except Exception as e:
    print(f"[red]Couldn't connect to OBS Socket Manager: {e}")

try:
    print("[purple]Trying to connect to OpenAI Manager")
    openAI_manager = OpenAiManager()
    print("[green]Connected to OpenAI Manager")
except Exception as e:
    print(f"[red]Couldn't connect to OpenAI Manager: {e}")

try:
    print("[purple]Trying to connect to Audio Manager")
    audio_player = AudioManager()
    print("[green]Connected to Audio Manager")
except Exception as e:
    print(f"[red]Couldn't connect to Audio Manager: {e}")

try:
    print("[purple]Trying to connect to ElevenLabs Manager")
    elevenlabs_manager = ElevenLabsManager()
    print("[green]Connected to ElevenLabs Manager")
except Exception as e:
    print(f"[red]Couldn't connect to ElevenLabs Manager: {e}")


FIRST_SYSTEM_MESSAGE = {"role": "system", "content" : '''
You are Gordon Ramsey, you are distinctively intense and commanding, often marked by a Scottish accent. He is known for his powerful, assertive, and sometimes abrasive tone, especially when 
critiquing culinary skills on his television shows. Despite your often harsh delivery, your voice also conveys passion and a deep commitment to culinary excellence. You are currently helping
a resturant chef named Zane run his kitchen for Twitch chat. They will be customers and you will be helping Zane cook his meals.
                        
While responding as Gordon, you must obey the following rules: 
1) Provide short responses, about 1-2 paragraphs. 
2) Always stay in character, no matter what. 
3) Most of your responses should be abbrasive and rude, you are disapointed with the chef most of the time.
4) Where curse words usually would appear, you can replace these with lesser forms of the words such as 'freak' for 'fuck', 'dangit' for 'damn', 'poop' for 'shit', 'idiot' for 'bitch'. Please use these a lot.
5) Occasionally get extremly disapointed in the entire situation that you find yourself in, you really don't want to be here. 
6) You sometimes like to reminisce on the days that you spent growing up in scottland, please introduce facts about this sometimes.
7) You Like to say 'Bloody Hell' all the time.       
8) Please use many exclamation points when you are yelling.
9) Remeber to use the words mentioned in 4).
Lastly) Keep your answers limited to just a few sentences. About two paragraphs worth.
                        
Okay, let the conversation begin!                      
'''}

openAI_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)

print("[green]Starting the loop, press F4 to begin")
while True:
    # Wait until user presses "f4" key
    if keyboard.read_key() != "f4":
        time.sleep(0.1)
        continue

    print("[green]User pressed F4 key! Now listening to your microphone:")

    # Get question from mic
    mic_result = azure_stt_manager.speechtotext_from_mic_continuous()
        
    if mic_result == '':
        print("[red]Did not receive any input from your microphone!")
        continue

    chatgpt_result = openAI_manager.chat_with_history(mic_result)

    with open(BACKUP_FILE, "w") as file:
        file.write(str(openAI_manager.chat_with_history))

    # Perform replacements (peforms replacement of words, utility function)
    chatgpt_result = replace_words(chatgpt_result)
        
    voice_output = elevenlabs_manager.text_to_audio(chatgpt_result, ELEVENLABS_VOICE, False)

    #TODO PUT THE THING ON THE SCREEN

    audio_player.play_audio(voice_output, sleep_during_playback=True, delete_file=True, play_using_music=True)

    #TODO DISABLE WEBSOCKET THINGIE

    print("[green] FINISHED PROCESSSING INPUT, READY FOR NEXT INPUT")