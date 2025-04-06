"""
The Main code for the Pythonese application
"""
# ! All External Modules or Python Package imports are not my work. Credit is as listed:

# ! traceback: https://pypi.org/project/traceback/ By: Python Software Foundation (PSF)
# ! os: https://docs.python.org/3/library/os.html By: Python Software Foundation (PSF)
# ! uuid: https://docs.python.org/3/library/uuid.html By: Python Software Foundation (PSF)
# ! flask: https://pypi.org/project/Flask/ By: Armin Ronacher and contributors
# ! speech_recognition: https://pypi.org/project/SpeechRecognition/ By: Anthony Lapenna
# ! google.generativeai: https://pypi.org/project/google-generativeai/ By: Google LLC
# ! gtts: https://pypi.org/project/gTTS/ By: Eduardo Silva (gTTS)
# ! pydub: https://pypi.org/project/pydub/ By: James A. Smith (pydub)

# ! The code below is written by me, Videsh Arivazhagan, the author of this project.

import traceback
import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
import speech_recognition as sr
import google.generativeai as genai
from gtts import gTTS
from pydub import AudioSegment

app = Flask(__name__)

GOOGLE_API_KEY = "AIzaSyCfb1AlLLYl9V3gEODD1JKwsuLTqQi0E3Q"
genai.configure(api_key=GOOGLE_API_KEY)

LANGUAGE_CODES = {
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

if not os.path.exists('static/audio'):
    os.makedirs('static/audio')

# Renders the index page
# Parameters: None
# Returns: Rendered HTML page
@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGE_CODES)

# Handles audio upload, processes it, and returns translation
# Parameters: Audio file (file), input_language (string), output_language (string)
# Returns: JSON response with recognized text, translated text, and audio paths
@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    temp_audio_path = None
    wav_path = None
    
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file found'}), 400
        
        audio_file = request.files['audio']
        input_language = request.form.get('input_language', 'english')
        output_language = request.form.get('output_language', 'french')
        
        if input_language not in LANGUAGE_CODES:
            return jsonify({'error': f'Invalid input language: {input_language}'}), 400
        if output_language not in LANGUAGE_CODES:
            return jsonify({'error': f'Invalid output language: {output_language}'}), 400
        
        temp_audio_path = f"static/audio/temp_{uuid.uuid4()}.webm"
        audio_file.save(temp_audio_path)
        
        wav_path = f"static/audio/temp_{uuid.uuid4()}.wav"
        
        try:
            audio = AudioSegment.from_file(temp_audio_path)
            audio.export(wav_path, format="wav")
        except Exception as e:
            return jsonify({'error': f'Audio conversion error: {str(e)}'}), 400
        
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                recognized_text = recognizer.recognize_google(audio_data, language=LANGUAGE_CODES[input_language])
        except sr.UnknownValueError:
            return jsonify({'error': 'Could not understand audio. Please speak clearly and try again.'}), 400
        except sr.RequestError as e:
            return jsonify({'error': f'Speech recognition service error: {str(e)}'}), 503
        except Exception as e:
            return jsonify({'error': f'Speech recognition error: {str(e)}'}), 500
        
        try:
            original_audio_filename = f"original_{uuid.uuid4()}.mp3"
            original_audio_path = f"static/audio/{original_audio_filename}"
            original_tts = gTTS(text=recognized_text, lang=LANGUAGE_CODES[input_language])
            original_tts.save(original_audio_path)
        except Exception as e:
            return jsonify({'error': f'Error generating original audio: {str(e)}'}), 500
        
        try:
            translated_text = translate_text(recognized_text, input_language, output_language)
            if not translated_text or translated_text.startswith("TRANSLATION ERROR"):
                return jsonify({'error': translated_text if translated_text else 'Empty translation result'}), 500
        except Exception as e:
            return jsonify({'error': f'Translation error: {str(e)}'}), 500
        
        try:
            translated_audio_filename = f"translated_{uuid.uuid4()}.mp3"
            translated_audio_path = f"static/audio/{translated_audio_filename}"
            translated_tts = gTTS(text=translated_text, lang=LANGUAGE_CODES[output_language])
            translated_tts.save(translated_audio_path)
        except Exception as e:
            return jsonify({'error': f'Error generating translated audio: {str(e)}'}), 500
        
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)
        
        return jsonify({
            'recognized_text': recognized_text,
            'translated_text': translated_text,
            'original_audio_path': original_audio_path,
            'translated_audio_path': translated_audio_path
        })
    
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        print(traceback.format_exc())
        
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)
        
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Handles text translation and generates audio
# Parameters: JSON with text (string), input_language (string), output_language (string)
# Returns: JSON response with translated text and audio paths
@app.route('/translate_text', methods=['POST'])
def handle_text_translation():
    try:
        if not request.is_json:
            return jsonify({'error': 'Expected JSON data'}), 400
        
        data = request.json
        input_text = data.get('text', '')
        input_language = data.get('input_language', 'english')
        output_language = data.get('output_language', 'french')
        
        if not input_text:
            return jsonify({'error': 'No text provided for translation'}), 400
        
        if input_language not in LANGUAGE_CODES:
            return jsonify({'error': f'Invalid input language: {input_language}'}), 400
        if output_language not in LANGUAGE_CODES:
            return jsonify({'error': f'Invalid output language: {output_language}'}), 400
        
        try:
            original_audio_filename = f"original_{uuid.uuid4()}.mp3"
            original_audio_path = f"static/audio/{original_audio_filename}"
            original_tts = gTTS(text=input_text, lang=LANGUAGE_CODES[input_language])
            original_tts.save(original_audio_path)
        except Exception as e:
            return jsonify({'error': f'Error generating original audio: {str(e)}'}), 500
        
        try:
            translated_text = translate_text(input_text, input_language, output_language)
            if not translated_text or translated_text.startswith("TRANSLATION ERROR"):
                return jsonify({'error': translated_text if translated_text else 'Empty translation result'}), 500
        except Exception as e:
            return jsonify({'error': f'Translation error: {str(e)}'}), 500
        
        try:
            translated_audio_filename = f"translated_{uuid.uuid4()}.mp3"
            translated_audio_path = f"static/audio/{translated_audio_filename}"
            translated_tts = gTTS(text=translated_text, lang=LANGUAGE_CODES[output_language])
            translated_tts.save(translated_audio_path)
        except Exception as e:
            return jsonify({'error': f'Error generating translated audio: {str(e)}'}), 500
        
        return jsonify({
            'translated_text': translated_text,
            'original_audio_path': original_audio_path,
            'translated_audio_path': translated_audio_path
        })
        
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Translates text using Google Gemini API
# Parameters: text (string), source_language (string), target_language (string)
# Returns: Translated text (string)
def translate_text(text, source_language, target_language):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        prompt = f"Translate the following text from {source_language} to {target_language}: '{text}', and return only the translated text without any additional formatting or explanation."
        response = model.generate_content(prompt)
        translated = response.text
        if translated.startswith('"') and translated.endswith('"'):
            translated = translated[1:-1]
        if translated.startswith("'") and translated.endswith("'"):
            translated = translated[1:-1]
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return f"TRANSLATION ERROR: {e}"

# Serves audio files from the static directory
# Parameters: filename (string)
# Returns: Audio file
@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)

# Returns the list of supported languages
# Parameters: None
# Returns: JSON response with language codes
@app.route('/languages')
def get_languages():
    return jsonify(LANGUAGE_CODES)

# Handles 404 errors
# Parameters: e (error object)
# Returns: JSON or rendered HTML page
@app.errorhandler(404)
def page_not_found(e):
    if request.headers.get('Accept') == 'application/json':
        return jsonify({'error': 'Resource not found'}), 404
    return render_template('404.html'), 404

# Handles 500 errors
# Parameters: e (error object)
# Returns: JSON or rendered HTML page
@app.errorhandler(500)
def server_error(e):
    if request.headers.get('Accept') == 'application/json':
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
