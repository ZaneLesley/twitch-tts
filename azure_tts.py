import os
import azure.cognitiveservices.speech as speechsdk
import random

# Some of this code is from https://github.com/DougDougGithub/ChatGodApp/blob/main/azure_text_to_speech.py

AZURE_VOICES = [
"en-US-DavisNeural",
"en-US-TonyNeural",
"en-US-JasonNeural",
"en-US-GuyNeural",
"en-US-JaneNeural",
"en-US-NancyNeural",
"en-US-JennyNeural",
"en-US-AriaNeural",
]

AZURE_VOICE_STYLES = [
    # Currently using the 9 of the 11 available voice styles
    # Note that certain styles aren't available on all voices
    "angry",
    "cheerful",
    "excited",
    "hopeful",
    "sad",
    "shouting",
    "terrified",
    "unfriendly",
    "whispering"
]

AZURE_PREFIXES = {
    "(angry)" : "angry",
    "(cheerful)" : "cheerful",
    "(excited)" : "excited",
    "(hopeful)" : "hopeful",
    "(sad)" : "sad",
    "(shouting)" : "shouting",
    "(shout)" : "shouting",
    "(terrified)" : "terrified",
    "(unfriendly)" : "unfriendly",
    "(whispering)" : "whispering",
    "(whisper)" : "whispering",
    "(random)" : "random"
}

class AzureTTSManager:
    def text_to_speech(text: str, user: str, voice_name = "random", voice_style = "random"):
        # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
        speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        
        if voice_name == "random":
            voice_name = random.choice(AZURE_VOICES)
        if voice_style == "random":
            voice_style = random.choice(AZURE_VOICE_STYLES)

        # Change the voice style if the message includes a prefix
        text = text.lower()
        print(text, flush=True)
        if text.startswith("(") and ")" in text:
            print("prefix found", flush=True)
            prefix = text[0:(text.find(")")+1)]
            if prefix in AZURE_PREFIXES:
                voice_style = AZURE_PREFIXES[prefix]
                text = text.removeprefix(prefix)
        if len(text) == 0:
            print("This message was empty", flush=True)
            return
        if voice_style == "random":
            voice_style = random.choice(AZURE_VOICE_STYLES)

        text = f"{user} said {text}"
       
        # The neural multilingual voice can speak different languages based on the input text. 
        ssml_text = f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts' xmlns:emo='http://www.w3.org/2009/10/emotionml' xml:lang='en-US'><voice name='{voice_name}'><mstts:express-as style='{voice_style}'>{text}</mstts:express-as></voice></speak>"

        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml_text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text), flush=True)
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details), flush=True)
                    print("Did you set the speech resource key and region values?", flush=True)