"""
The Main CLI code for the Pythonese application
"""
# ! All External Modules or Python Package imports are not my work. Credit is as listed:
# ! asyncio by Guido van Rossum https://docs.python.org/3/library/asyncio.html
# ! threading by Guido van Rossum https://docs.python.org/3/library/threading.html
# ! keyboard by BoppreH https://pypi.org/project/keyboard/
# ! SpeechRecognition by Anthony Zhang https://pypi.org/project/SpeechRecognition/
# ! gTTS by Pierre Nicolas Durette https://pypi.org/project/gTTS/
# ! playsound by Szymon Mikler https://pypi.org/project/playsound3/
# ! googletrans by SuHun Han https://pypi.org/project/googletrans/

# ! The code below is written by me, Videsh Arivazhagan, the author of this project.

import asyncio
import threading
import keyboard
import speech_recognition as sr
from gtts import gTTS
from playsound3 import playsound as ps
from googletrans import Translator

LANGUAGE_CODES = {
    'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar',
    'armenian': 'hy', 'azerbaijani': 'az', 'bengali': 'bn', 'chinese': 'zh-CN',
    'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 'dutch': 'nl',
    'english': 'en', 'french': 'fr', 'german': 'de', 'hindi': 'hi',
    'italian': 'it', 'japanese': 'ja', 'korean': 'ko', 'portuguese': 'pt',
    'russian': 'ru', 'spanish': 'es', 'swahili': 'sw', 'tamil': 'ta',
    'telugu': 'te', 'thai': 'th', 'turkish': 'tr', 'vietnamese': 'vi',
    'zulu': 'zu'
}

EXIT_FLAG = False

def get_language_code(prompt):
    """Prompt the user for a language and return its code
    Parameters:
        prompt (str): Prompt to display to the user
    """
    while True:
        language = input(prompt).strip().lower()
        if language in LANGUAGE_CODES:
            return language, LANGUAGE_CODES[language]
        print("Language not recognized. Please try again.")

def monitor_exit():
    """Monitor keyboard input to exit on 'q' press.
    Sets the global EXIT_FLAG to True when 'q' is pressed.
    """
    global EXIT_FLAG
    keyboard.wait('q')
    EXIT_FLAG = True
    print("\nExit key detected. Quitting application...")

async def main():
    """Main function to run the Pythonese application.
    Uses speech recognition to listen for audio input and translates it to another language.
    """

    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=0)

    input_language, input_lang_code = get_language_code("Enter the input language: ")
    output_lang_code = get_language_code("Enter the output language: ")

    while not EXIT_FLAG:
        try:
            with mic as source:
                print("Adjusting for ambient noise. Please wait...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"Listening in {input_language}. Press 'q' to quit.")

                audio = recognizer.listen(source, timeout=None, phrase_time_limit=10)

            recognized_text = recognizer.recognize_google(audio, language=input_lang_code)
            print(f"You said: {recognized_text}")

            translator = Translator()
            translated = translator.translate(recognized_text,
                                              src=input_lang_code,
                                              dest=output_lang_code)
            translated_text = translated.text
            print(f"Translated text: {translated_text}")

            tts = gTTS(text=translated_text, lang=output_lang_code)
            tts.save("translated.mp3")
            print("Playing translated speech...")
            ps("translated.mp3")

        except sr.UnknownValueError:
            print("Could not understand audio. Please try again.")
        except sr.RequestError as e:
            print(f"Request error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    print("Exiting program. Goodbye!")

if __name__ == "__main__":
    exit_thread = threading.Thread(target=monitor_exit, daemon=True)
    exit_thread.start()
    asyncio.run(main())
