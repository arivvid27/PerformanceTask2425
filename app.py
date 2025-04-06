import os
from flask import Flask, render_template, request, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import tempfile

from config import Config
from services import translation_service, stt_service, tts_service
from utils.helpers import save_uploaded_file

# Initialize Flask app and database
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Models
class TranslationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)
    translated_text = db.Column(db.Text, nullable=False)
    source_language = db.Column(db.String(10))
    target_language = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html', languages=Config.SUPPORTED_LANGUAGES)

@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.json or {}
    text = data.get('text', '')
    source_lang = data.get('source_lang')
    target_lang = data.get('target_lang', 'en')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    if not source_lang:
        source_lang = translation_service.detect_language(text)
    
    translated_text = translation_service.translate_text(
        text=text,
        source_lang=source_lang,
        target_lang=target_lang
    )
    
    # Save to history
    if translated_text and not translated_text.startswith('Translation error'):
        history = TranslationHistory(
            original_text=text,
            translated_text=translated_text,
            source_language=source_lang,
            target_language=target_lang
        )
        db.session.add(history)
        db.session.commit()
    
    return jsonify({
        'translated_text': translated_text,
        'source_lang': source_lang,
        'target_lang': target_lang
    })

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.json or {}
    text = data.get('text', '')
    language = data.get('language', 'en')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Convert text to speech
    audio_file = tts_service.text_to_speech(text, language)
    
    if not audio_file:
        return jsonify({'error': 'Failed to generate speech'}), 500
    
    session['audio_file'] = audio_file
    
    return jsonify({
        'success': True,
        'audio_url': '/api/get-audio'
    })

@app.route('/api/get-audio')
def get_audio():
    audio_file = session.get('audio_file')
    
    if not audio_file or not os.path.exists(audio_file):
        return jsonify({'error': 'Audio file not found'}), 404
    
    return send_file(audio_file, mimetype='audio/mp3')

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    # Check if file is in request
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    language = request.form.get('language', 'en-US')
    
    if audio_file.filename == '':
        return jsonify({'error': 'No audio file selected'}), 400
    
    # Save the uploaded file
    filepath = save_uploaded_file(audio_file, app.config['UPLOAD_FOLDER'])
    
    # Convert speech to text
    text = stt_service.audio_to_text(filepath, language)
    
    # Clean up the file
    try:
        os.remove(filepath)
    except:
        pass
    
    return jsonify({
        'text': text,
        'language': language
    })

@app.route('/api/speech-translate', methods=['POST'])
def speech_translate():
    # Check if file is in request
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    source_lang = request.form.get('source_lang', 'en-US')
    target_lang = request.form.get('target_lang', 'en')
    
    if audio_file.filename == '':
        return jsonify({'error': 'No audio file selected'}), 400
    
    # Save the uploaded file
    filepath = save_uploaded_file(audio_file, app.config['UPLOAD_FOLDER'])
    
    # Convert speech to text
    text = stt_service.audio_to_text(filepath, source_lang)
    
    # Clean up the file
    try:
        os.remove(filepath)
    except:
        pass
    
    if text.startswith("Error") or text.startswith("Could not"):
        return jsonify({'error': text}), 400
    
    # Translate the text
    translated_text = translation_service.translate_text(
        text=text,
        source_lang=source_lang[:2],  # Use first 2 chars of language code
        target_lang=target_lang
    )
    
    return jsonify({
        'original_text': text,
        'translated_text': translated_text,
        'source_lang': source_lang,
        'target_lang': target_lang
    })

@app.route('/history')
def history():
    translations = TranslationHistory.query.order_by(TranslationHistory.timestamp.desc()).limit(20).all()
    return render_template('history.html', translations=translations, languages=Config.SUPPORTED_LANGUAGES)

@app.route('/profile')
def profile():
    return render_template('profile.html', languages=Config.SUPPORTED_LANGUAGES)

if __name__ == '__main__':
    app.run(debug=True)