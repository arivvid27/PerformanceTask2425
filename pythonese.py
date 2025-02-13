"""
The Main Web-based GUI code for the Pythonese application using Flask
"""

from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from gtts import gTTS
from playsound3 import playsound as ps
from googletrans import Translator
import asyncio

app = Flask(__name__)

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

stop_flag = False


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def start_translation():
    """Start the translation process."""
    global stop_flag
    stop_flag = False

    input_language = request.json.get('input_language', '').strip().lower()
    output_language = request.json.get('output_language', '').strip().lower()

    if input_language not in language_codes or output_language not in language_codes:
        return jsonify({'error': 'Invalid language entered. Please try again.'}), 400

    input_lang_code = language_codes[input_language]
    output_lang_code = language_codes[output_language]

    asyncio.run(run_translation(input_lang_code, output_lang_code))
    return jsonify({'message': 'Translation process started.'})


@app.route('/stop', methods=['POST'])
def stop_translation():
    """Stop the translation process."""
    global stop_flag
    stop_flag = True
    return jsonify({'message': 'Stopping translation...'})


async def run_translation(input_lang_code, output_lang_code):
    """Run the translation process."""
    global stop_flag
    r = sr.Recognizer()
    mic = sr.Microphone(device_index=0)

    while not stop_flag:
        try:
            with mic as source:
                print("Adjusting for ambient noise. Please wait...")
                r.adjust_for_ambient_noise(source, duration=1)
                print(f"Listening in {input_lang_code}...")

                audio = r.listen(source, timeout=None, phrase_time_limit=10)
                if stop_flag:
                    print("Stopped by user.")
                    return

            # Recognize speech
            recognized_text = r.recognize_google(audio, language=input_lang_code)
            print(f"You said: {recognized_text}")

            # Translate text (sync call)
            translator = Translator()
            translated = translator.translate(recognized_text, src=input_lang_code, dest=output_lang_code)
            translated_text = translated.text
            print(f"Translated text: {translated_text}")

            # Convert to speech
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

    print("Translation loop ended.")


if __name__ == '__main__':
    app.run(debug=True)
