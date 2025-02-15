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
import keyboard
import speech_recognition as sr
from gtts import gTTS
from playsound3 import playsound as ps
from googletrans import Translator

language_codes = {
    'afrikaans': 'af',
    'albanian': 'sq',
    'amharic': 'am',
    'arabic': 'ar',
    'armenian': 'hy',
    'azerbaijani': 'az',
    'bengali': 'bn',
    'chinese': 'zh-CN',
    'croatian': 'hr',
    'czech': 'cs',
    'danish': 'da',
    'dutch': 'nl',
    'english': 'en',
    'french': 'fr',
    'german': 'de',
    'hindi': 'hi',
    'italian': 'it',
    'japanese': 'ja',
    'korean': 'ko',
    'portuguese': 'pt',
    'russian': 'ru',
    'spanish': 'es',
    'swahili': 'sw',
    'tamil': 'ta',
    'telugu': 'te',
    'thai': 'th',
    'turkish': 'tr',
    'vietnamese': 'vi',
    'zulu': 'zu'
}

def get_language_code(prompt):
    """Prompt user for a language and return its code."""
    while True:
        language = input(prompt).strip().lower()
        if language in language_codes:
            return language, language_codes[language]
        print("Language not recognized. Please try again.")


async def main():
    """Main function to run the Pythonese application."""
    r = sr.Recognizer()
    mic = sr.Microphone(device_index=0)

    input_language, input_lang_code = get_language_code("Enter the input language: ")
    output_lang_code = get_language_code("Enter the output language: ")

    while not keyboard.is_pressed('q'):
        try:
            with mic as source:
                print("Adjusting for ambient noise. Please wait...")
                r.adjust_for_ambient_noise(source, duration=1)
                print(f"Listening in {input_language}. Press 'q' to quit.")
                audio = r.listen(source, timeout=None, phrase_time_limit=10)

            recognized_text = r.recognize_google(audio, language=input_lang_code)
            print(f"You said: {recognized_text}")

            translator = Translator()
            translated = await translator.translate(recognized_text,
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
        except ValueError as e:
            print(f"A value error occurred: {e}")

    print("\nThank you for using Pythonese! Goodbye!")


asyncio.run(main())
