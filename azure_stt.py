import azure.cognitiveservices.speech as speechsdk
import os
import keyboard
import time

class AzureTTSManager:
    azure_speech_config = None
    azure_audio_config = None
    azure_speech_recognizer = None

    def __init__(self):
        try:
            # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
            speech_key = os.environ.get('SPEECH_KEY')
            speech_region = os.environ.get('SPEECH_REGION')
            
            self.azure_speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
            # Use get_device_id.py to get speaker output (use use_default_speaker = True for default output)
            self.azure_speech_config.speech_recognition_language = "en-US"
        except Exception as e:
            print(f"Error in __init__: {e}")

    def speechtotext_from_mic_continuous(self, stop_key='p'):
        try:
            self.azure_speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.azure_speech_config)
            done = False

            all_results = []
            def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
                #print('RECOGNIZED: {}'.format(evt))
                #print(f"Result Text: {evt.result.text}")
                all_results.append(evt.result.text)
            
            def stop_cb(evt: speechsdk.SessionEventArgs):
                print('CLOSING speech recognition on {}'.format(evt))
                nonlocal done
                done = True

            self.azure_speech_recognizer.session_stopped.connect(stop_cb)
            self.azure_speech_recognizer.canceled.connect(stop_cb)
            self.azure_speech_recognizer.recognized.connect(recognized_cb)
            
            result_future = self.azure_speech_recognizer.start_continuous_recognition_async()
            result_future.get()
            print('Continuous Speech Recognition is now running, say something.')

            while not done:
                if keyboard.read_key() == stop_key:
                    print("\nEnding azure speech recognition\n")
                    self.azure_speech_recognizer.stop_continuous_recognition_async()
                    time.sleep(2)
                    break
            final_result = " ".join(all_results).strip()
            print(f"\n\nHere's the result we got!\n\n{final_result}\n\n")
            return final_result
        except Exception as e:
            print(f"Error in speechtotext_from_mic_continuous: {e}")
            return ""

if __name__ == '__main__':
    # Tests
    try:
        speechtotext_manager = AzureTTSManager()
        while True:
            if keyboard.read_key() != "f4":
                time.sleep(0.1)
                continue

            print("User pressed F4 key! Now listening to your microphone:")
            mic_result = speechtotext_manager.speechtotext_from_mic_continuous()
            
            if mic_result == '':
                print("Did not receive any input from your microphone!")
                continue

    except Exception as e:
        print(f"Error in main: {e}")
