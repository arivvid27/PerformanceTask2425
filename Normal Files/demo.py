"""
Demo file to test out code without affecting main file
"""

import speech_recognition as sr
# from gtts import gTTS as tts
# from playsound3 import playsound as ps

language_codes = {

}

sr.Microphone.list_microphone_names()
mic = sr.Microphone(device_index=0)
r = sr.Recognizer()

with mic as source:
    print("Say something")
    audio = r.listen(source)

try:
    print("You said: " + r.recognize_google(audio))
except sr.UnknownValueError:
    print("Could not understand audio")
    