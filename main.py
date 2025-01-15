"""
The Main code for the Pythonese application
"""
# ! All External Modules or Python Package imports are not my work. Credit is as listed:
# ! SpeechRecognition by Anthony Zhang https://pypi.org/project/SpeechRecognition/
# ! gTTS by Pierre Nicolas Durette https://pypi.org/project/gTTS/
# ! playsound by Szymon Mikler https://pypi.org/project/playsound3/

# import speech_recognition as sr
from gtts import gTTS
# from playsound3 import playsound as ps

tts = gTTS('hello')
tts.save('hello.mp3')
