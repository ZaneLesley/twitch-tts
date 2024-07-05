from obswebsocket import obsws, requests  # noqa: E402
from dotenv import load_dotenv
import os
from time import sleep

class OBSSocketManager:
    ws = None

    def __init__(self):
        load_dotenv()
        self.ws = obsws(host="localhost", port="4455", password=os.getenv('OBS_TOKEN'))
        try:
            self.ws.connect()
            print("Successfully connected to OBS")
        except Exception as e:
            raise


    def disconnect(self):
        self.ws.disconnect()

    def set_filter_visibility(self, scene_name, source_name, enabled):
        response = self.ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name))
        myItemID = response.datain['sceneItemId']
        self.ws.call(requests.SetSceneItemEnabled(sceneName=scene_name, sceneItemId=myItemID, sceneItemEnabled=enabled))
    
    def set_text(self, source_name, new_text):
        # Determine the appropriate font size based on the length of new_text
        max_font_size = 65  # Maximum font size
        min_font_size = 10  # Minimum font size
        max_length = 100    # Maximum length of text before minimum font size is used

        # Calculate font size
        font_size = max(min_font_size, max_font_size - (len(new_text) / max_length) * (max_font_size - min_font_size))
        font_size = int(font_size)

        # Set the text with the calculated font size
        settings = {
            'text': new_text,
            'font': {
                'face': "Runescape UF",  # Adjust as needed
                'size': font_size,
                'style': "Regular",
                'flags': 0
            }
        }
        self.ws.call(requests.SetInputSettings(inputName=source_name, inputSettings = settings))

if __name__ == '__main__':
    # Tests:
    print("Attempting to connect to OBS")
    obs_manager = OBSSocketManager()
    sleep(2)
    try:
        source_name = "weinerText"
        new_text = "Now im typing a pretty long message about sasuages and stuff like that"
        obs_manager.set_text(source_name, new_text)
    finally:
        obs_manager.disconnect()
