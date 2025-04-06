"""
Flask implementation of the Pythonese translator application
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import speech_recognition as sr
import google.generativeai as genai
from gtts import gTTS
import uuid
import tempfile
from pydub import AudioSegment

app = Flask(__name__)

# Configure your Google Gemini API key
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

# Create uploads directory if it doesn't exist
if not os.path.exists('static/audio'):
    os.makedirs('static/audio')

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGE_CODES)

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file found'}), 400
    
    audio_file = request.files['audio']
    input_language = request.form.get('input_language')
    output_language = request.form.get('output_language')
    
    # Save the uploaded audio file temporarily
    temp_audio_path = f"static/audio/temp_{uuid.uuid4()}.webm"
    audio_file.save(temp_audio_path)
    
    try:
        # Convert WebM to WAV format for compatibility with speech_recognition
        wav_path = f"static/audio/temp_{uuid.uuid4()}.wav"
        audio = AudioSegment.from_file(temp_audio_path)
        audio.export(wav_path, format="wav")
        
        # Convert speech to text
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            recognized_text = recognizer.recognize_google(audio_data, language=LANGUAGE_CODES[input_language])
        
        # Generate audio for original text
        original_audio_filename = f"original_{uuid.uuid4()}.mp3"
        original_audio_path = f"static/audio/{original_audio_filename}"
        original_tts = gTTS(text=recognized_text, lang=LANGUAGE_CODES[input_language])
        original_tts.save(original_audio_path)
        
        # Clean up temp files
        os.remove(temp_audio_path)
        os.remove(wav_path)
        
        # Get translation
        translated_text = translate_text(recognized_text, input_language, output_language)
        
        # Generate audio for translated text
        translated_audio_filename = f"translated_{uuid.uuid4()}.mp3"
        translated_audio_path = f"static/audio/{translated_audio_filename}"
        translated_tts = gTTS(text=translated_text, lang=LANGUAGE_CODES[output_language])
        translated_tts.save(translated_audio_path)
        
        return jsonify({
            'recognized_text': recognized_text,
            'translated_text': translated_text,
            'original_audio_path': original_audio_path,
            'translated_audio_path': translated_audio_path
        })
    
    except Exception as e:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return jsonify({'error': str(e)}), 500

@app.route('/translate_text', methods=['POST'])
def handle_text_translation():
    data = request.json
    input_text = data.get('text', '')
    input_language = data.get('input_language', 'english')
    output_language = data.get('output_language', 'french')
    
    try:
        # Generate audio for original text
        original_audio_filename = f"original_{uuid.uuid4()}.mp3"
        original_audio_path = f"static/audio/{original_audio_filename}"
        original_tts = gTTS(text=input_text, lang=LANGUAGE_CODES[input_language])
        original_tts.save(original_audio_path)
        
        # Get translation
        translated_text = translate_text(input_text, input_language, output_language)
        
        # Generate audio for translated text
        translated_audio_filename = f"translated_{uuid.uuid4()}.mp3"
        translated_audio_path = f"static/audio/{translated_audio_filename}"
        translated_tts = gTTS(text=translated_text, lang=LANGUAGE_CODES[output_language])
        translated_tts.save(translated_audio_path)
        
        return jsonify({
            'translated_text': translated_text,
            'original_audio_path': original_audio_path,
            'translated_audio_path': translated_audio_path
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def translate_text(text, source_language, target_language):
    """Use Google Gemini API to translate text"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        prompt = f"Translate the following text from {source_language} to {target_language}: '{text}', and return only the translated text without any additional formatting or explanation."
        response = model.generate_content(prompt)
        # Clean up response to get just the translated text
        translated = response.text
        # Remove quotes if they're present
        if translated.startswith('"') and translated.endswith('"'):
            translated = translated[1:-1]
        if translated.startswith("'") and translated.endswith("'"):
            translated = translated[1:-1]
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        # Fallback to simple echo for testing if Gemini fails
        return f"TRANSLATION ERROR: {e}"

@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)

@app.route('/languages')
def get_languages():
    return jsonify(LANGUAGE_CODES)

if __name__ == '__main__':
    app.run(debug=True)