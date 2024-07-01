# Tool to get Speakers/Microphone IDs for the obs-socket.py
# https://stackoverflow.com/questions/67501540/while-working-with-azure-speech-sdk-on-windows-how-to-get-device-name-for-crea

import comtypes
from pycaw.pycaw import AudioUtilities, IMMDeviceEnumerator, EDataFlow, DEVICE_STATE
from pycaw.constants import CLSID_MMDeviceEnumerator

devices = []

deviceEnumerator = comtypes.CoCreateInstance(
    CLSID_MMDeviceEnumerator,
    IMMDeviceEnumerator,
    comtypes.CLSCTX_INPROC_SERVER)
if deviceEnumerator is None:
    devices = []
    raise ValueError("Couldn't find any devices.")

# Microphones (Capture Devices): Use EDataFlow.eCapture.value. Speakers (Render Devices): Use EDataFlow.eRender.value.
collection = deviceEnumerator.EnumAudioEndpoints(EDataFlow.eRender.value, DEVICE_STATE.ACTIVE.value)            
if collection is None:
    devices = []
    raise ValueError("Couldn't find any devices.")

count = collection.GetCount()
for i in range(count):
    dev = collection.Item(i)
    if dev is not None:
        if not ": None" in str(AudioUtilities.CreateDevice(dev)):
            devices.append(AudioUtilities.CreateDevice(dev))

for device in devices:
    print("Found output device.")
    print(device.FriendlyName)
    print(device.id)
    print("\n")
