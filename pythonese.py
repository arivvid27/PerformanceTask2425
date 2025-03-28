"""
The Main code for the Pythonese application
"""
# ! All External Modules or Python Package imports are not my work. Credit is as listed:
# ! os by Guido van Rossum https://docs.python.org/3/library/os.html
# ! time by Guido van Rossum https://docs.python.org/3/library/time.html
# ! asyncio by Guido van Rossum https://docs.python.org/3/library/asyncio.html
# ! threading by Guido van Rossum https://docs.python.org/3/library/threading.html
# ! colorama by Jonathan Hartley https://pypi.org/project/colorama/
# ! keyboard by BoppreH https://pypi.org/project/keyboard/
# ! SpeechRecognition by Anthony Zhang https://pypi.org/project/SpeechRecognition/
# ! gTTS by Pierre Nicolas Durette https://pypi.org/project/gTTS/
# ! playsound by Szymon Mikler https://pypi.org/project/playsound3/
# ! googletrans by SuHun Han https://pypi.org/project/googletrans/

# ! The code below is written by me, Videsh Arivazhagan, the author of this project.

# TODO Make this a flask application
# TODO Replace this with routing
# TODO Break this program into submodules for better error trapping
# TODO Rewrite the entire repository.

import subprocess
import sys
subprocess.check_call([sys.executable, '-m', 'pip', 'install', './requirements.txt'])

import os
import time
import asyncio
import threading
import keyboard
import speech_recognition as sr
from gtts import gTTS
from playsound3 import playsound as ps
from googletrans import Translator
from colorama import Fore, Style

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
    """
    Prompt the user for a language and return its code
    prompt{str}: The prompt to display to the user
    return{string}: Returns the language code needed for the gTTS module
    """
    while True:
        language = input(Fore.CYAN + prompt + Style.RESET_ALL).strip().lower()
        if language in LANGUAGE_CODES:
            return language, LANGUAGE_CODES[language]
        print(Fore.RED + "Language not recognized. Please try again." + Style.RESET_ALL)

def monitor_exit():
    """
    Monitor keyboard input to exit on 'q' press
    """
    global EXIT_FLAG
    keyboard.wait('q')
    EXIT_FLAG = True
    print(Fore.YELLOW + "\nExit key detected. Quitting application..." + Style.RESET_ALL)

async def main():
    """
    Main function to run the Pythonese application.
    """
    global EXIT_FLAG

    try:
        os.system("cls")
    except Exception as e:
        os.system("clear")
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=0)

    print(Fore.GREEN + "=== Welcome to Pythonese Translator ===" + Style.RESET_ALL)
    time.sleep(2)
    input_language, input_lang_code = get_language_code("Enter the input language: ")
    output_language, output_lang_code = get_language_code("Enter the output language: ")
    print(Fore.RED + "Press 'q' to quit at any time." + Style.RESET_ALL)

    while not EXIT_FLAG:
        try:
            with mic as source:
                print(Fore.BLUE + "Adjusting for ambient noise. Please wait..." + Style.RESET_ALL)
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print(Fore.CYAN + f"Listening in {input_language}." + Style.RESET_ALL)
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=10)

            recognized_text = recognizer.recognize_google(audio, language=input_lang_code)
            print(Fore.GREEN + "You said: " + Style.RESET_ALL + f"{recognized_text}")

            translator = Translator()
            translated = await translator.translate(recognized_text,
                                                    src=input_lang_code,
                                                    dest=output_lang_code)
            translated_text = translated.text
            print(Fore.GREEN + "Translated text: " + Style.RESET_ALL + f"{translated_text}")

            tts = gTTS(text=translated_text, lang=output_lang_code)
            tts.save("translated.mp3")
            print(Fore.MAGENTA + "Playing translated speech..." + Style.RESET_ALL)
            ps("translated.mp3")

        except sr.UnknownValueError:
            print(Fore.RED + "Could not understand audio. Please try again." + Style.RESET_ALL)
        except sr.RequestError as e:
            print(Fore.RED + f"Request error: {e}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)

    print(Fore.YELLOW + "Exiting program. Goodbye!" + Style.RESET_ALL)

if __name__ == "__main__":
    exit_thread = threading.Thread(target=monitor_exit, daemon=True)
    exit_thread.start()
    asyncio.run(main())
