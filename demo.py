"""
Demo file to test out code without affecting main file
"""

import speech_recognition as sr
from gtts import gTTS as tts
from playsound3 import playsound as ps

r = sr.Recognizer()
sr.Microphone.list_microphone_names()
mic = sr.Microphone(device_index=0)
with mic as source:
    audio = r.listen(source)
r.recognize_google(audio, language="en-EN")
