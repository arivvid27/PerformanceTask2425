"""
The Main GUI code for the Pythonese application
"""
# ! All External Modules or Python Package imports are not my work. Credit is as listed:
# ! asyncio by Guido van Rossum https://docs.python.org/3/library/asyncio.html
# ! tkinter by Guido van Rossum https://docs.python.org/3/library/tkinter.html
# ! SpeechRecognition by Anthony Zhang https://pypi.org/project/SpeechRecognition/
# ! gTTS by Pierre Nicolas Durette https://pypi.org/project/gTTS/
# ! playsound by Szymon Mikler https://pypi.org/project/playsound3/
# ! googletrans by SuHun Han https://pypi.org/project/googletrans/

# ! The code below is written by me, Videsh Arivazhagan, the author of this project.

import asyncio
import tkinter as tk
from tkinter import messagebox, scrolledtext
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

class StopListener:
    """Utility class to check for stop flag to stop recording."""
    def __init__(self):
        self.stop_flag = False

    def stop(self):
        """Set the stop flag to True."""
        self.stop_flag = True

    def reset(self):
        """Reset the stop flag to False."""
        self.stop_flag = False

class PythoneseApp:
    """Main Pythonese application class."""
    def __init__(self, root):
        self.root = root
        self.root.title("Pythonese Application")

        self.input_language_var = tk.StringVar()
        self.output_language_var = tk.StringVar()

        tk.Label(root, text="Input Language:").grid(row=0, column=0, padx=10, pady=10)
        self.input_language_entry = tk.Entry(root, textvariable=self.input_language_var)
        self.input_language_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(root, text="Output Language:").grid(row=1, column=0, padx=10, pady=10)
        self.output_language_entry = tk.Entry(root, textvariable=self.output_language_var)
        self.output_language_entry.grid(row=1, column=1, padx=10, pady=10)

        self.start_button = tk.Button(root, text="Start", command=self.start_translation)
        self.start_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_translation)
        self.stop_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, width=50)
        self.log_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.stop_listener = StopListener()

    def log(self, message):
        """Log messages to the Tkinter window."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def start_translation(self):
        """Start the translation process."""
        input_language = self.input_language_var.get().strip().lower()
        output_language = self.output_language_var.get().strip().lower()

        if input_language not in language_codes or output_language not in language_codes:
            messagebox.showerror("Error", "Invalid language entered. Please try again.")
            return

        self.stop_listener.reset()
        input_lang_code = language_codes[input_language]
        output_lang_code = language_codes[output_language]
        asyncio.run(self.run_translation(input_lang_code, output_lang_code))

    def stop_translation(self):
        """Stop the translation process."""
        self.stop_listener.stop()
        self.log("Stopping translation...")

    async def run_translation(self, input_lang_code, output_lang_code):
        """Run the translation process."""
        r = sr.Recognizer()
        mic = sr.Microphone(device_index=0)

        while not self.stop_listener.stop_flag:
            try:
                with mic as source:
                    self.log("Adjusting for ambient noise. Please wait...")
                    r.adjust_for_ambient_noise(source, duration=1)
                    self.log(f"Listening in {input_lang_code}...")

                    audio = r.listen(source, timeout=None, phrase_time_limit=10)
                    if self.stop_listener.stop_flag:
                        self.log("Stopped by user.")
                        return

                recognized_text = r.recognize_google(audio, language=input_lang_code)
                self.log(f"You said: {recognized_text}")

                translator = Translator()
                translated = await translator.translate(recognized_text, src=input_lang_code, dest=output_lang_code)
                translated_text = translated.text
                self.log(f"Translated text: {translated_text}")

                tts = gTTS(text=translated_text, lang=output_lang_code)
                tts.save("translated.mp3")
                self.log("Playing translated speech...")
                ps("translated.mp3")

            except sr.UnknownValueError:
                self.log("Could not understand audio. Please try again.")
            except sr.RequestError as e:
                self.log(f"Request error: {e}")
            except Exception as e:
                self.log(f"An error occurred: {e}")

        self.log("Translation loop ended.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PythoneseApp(root)
    root.mainloop()
