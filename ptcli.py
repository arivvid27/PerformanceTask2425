"""
Credits:
- SpeechRecognition (https://pypi.org/project/SpeechRecognition/): Library for performing speech recognition
- googletrans (https://pypi.org/project/googletrans/): Free and Unlimited Google translate API
- gTTS (https://pypi.org/project/gTTS/): Google Text-to-Speech interface
- playsound (https://pypi.org/project/playsound/): Pure Python, cross platform, single function module for playing sounds
- pynput (https://pypi.org/project/pynput/): Monitor and control input devices
"""

import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
from playsound import playsound
import time
from pynput import keyboard
import threading

running = True
stats = {
    'translations': 0,
    'language_pairs': []
}

def on_press(key):
    global running
    try:
        if key.char == 'q':
            running = False
            return False
    except AttributeError:
        pass

def get_speech_input():
    """
    Function to capture speech input from microphone
    Uses speech_recognition module to convert speech to text
    Returns the recognized text as string
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Speak something!")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "Could not request results"

def translate_and_speak(text, target_lang):
    """
    Function to translate text and convert it to speech
    Parameters:
        text (str): Text to be translated
        target_lang (str): Target language code (e.g., 'es' for Spanish)
    Uses googletrans for translation and gtts for text-to-speech conversion
    """
    supported_languages = list(gTTS.LANGUAGES.keys())

    if target_lang not in supported_languages:
        print("Language not supported. Please choose from:", supported_languages)
        return

    translator = Translator()
    translation = translator.translate(text, dest=target_lang)

    stats['translations'] += 1
    stats['language_pairs'].append(f"'{translation.src}' to '{target_lang}'")

    tts = gTTS(text=translation.text, lang=target_lang)
    tts.save("translated_speech.mp3")

    print(f"Original text: {text}")
    print(f"Translated text: {translation.text}")
    playsound("translated_speech.mp3")
    os.remove("translated_speech.mp3")

def main():
    """
    Main function to run the speech translation program
    Demonstrates input/output and function calls
    """
    global running

    print("Enter target language code (e.g., 'es' for Spanish):")
    target_lang = input().lower()

    print("Press 'q' at any time to quit the program")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while running:
        speech_text = get_speech_input()
        if speech_text and speech_text not in ["Could not understand audio", "Could not request results"]:
            translate_and_speak(speech_text, target_lang)
            print("\nWaiting 5 seconds before next translation...")
            time.sleep(5)

    print("\nTranslation Statistics:")
    print(f"Total translations: {stats['translations']}")
    print("Language pairs translated:")
    for pair in stats['language_pairs']:
        print(f"- {pair}")

if __name__ == "__main__":
    main()