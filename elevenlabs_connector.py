from elevenlabs.client import ElevenLabs
from elevenlabs import save
import time
import os
from dotenv import load_dotenv
from rich import print


class ElevenLabsManager():
    def __init__(self):
        load_dotenv()
        self.elevenlabs_manager = ElevenLabs(api_key=os.getenv('ELEVENLABS_KEY'))
        # Get all available voices and extract their names
        response = self.elevenlabs_manager.voices.get_all()
        voice_names = [voice.name for voice in response.voices]
        print(f"[blue] all avaliable voices are \n{voice_names}\n")
        
    
    def text_to_audio(self, input_text, voice="Zane GR", save_as_wave=True, subdirectory=""):
        audio_saved = self.elevenlabs_manager.generate(
            text=input_text,
            voice=voice,
            model="eleven_multilingual_v2"
        )

        if save_as_wave:
          file_name = f"___Msg{str(hash(input_text))}.wav"
        else:
          file_name = f"___Msg{str(hash(input_text))}.mp3"
        tts_file = os.path.join(os.path.abspath(os.curdir), subdirectory, file_name)
        save(audio_saved,tts_file)
        return tts_file
