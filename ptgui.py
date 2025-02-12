"""
Credits:
- SpeechRecognition (https://pypi.org/project/SpeechRecognition/): Library for performing speech recognition
- googletrans (https://pypi.org/project/googletrans/): Free and Unlimited Google translate API
- gTTS (https://pypi.org/project/gTTS/): Google Text-to-Speech interface
- playsound3 (https://pypi.org/project/playsound3/): Pure Python, cross platform, single function module for playing sounds
- Flask (https://flask.palletsprojects.com/): Web framework for Python
"""

import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
from playsound3 import playsound
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

running = False
stats = {
    'translations': 0,
    'language_pairs': []
}

def get_speech_input():
    """
    Function to capture speech input from microphone
    Uses speech_recognition module to convert speech to text
    Returns the recognized text as string
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
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
        return {"error": "Language not supported"}

    translator = Translator()
    translation = translator.translate(text, dest=target_lang)

    stats['translations'] += 1
    stats['language_pairs'].append(f"'{translation.src}' to '{target_lang}'")

    tts = gTTS(text=translation.text, lang=target_lang)
    tts.save("static/translated_speech.mp3")

    return {
        "original": text,
        "translated": translation.text,
        "audio": "static/translated_speech.mp3"
    }

@app.route('/')
def home():
    return render_template('index.html', languages=gTTS.LANGUAGES)

@app.route('/start', methods=['POST'])
def start_translation():
    global running
    running = True
    target_lang = request.form.get('language')
    
    if running:
        speech_text = get_speech_input()
        if speech_text and speech_text not in ["Could not understand audio", "Could not request results"]:
            result = translate_and_speak(speech_text, target_lang)
            return jsonify(result)
    
    return jsonify({"error": "Translation failed"})

@app.route('/stop', methods=['POST'])
def stop_translation():
    global running
    running = False
    return jsonify({
        "translations": stats['translations'],
        "language_pairs": stats['language_pairs']
    })

if __name__ == "__main__":
    app.run(debug=True)

# Create templates/index.html with the following content:
"""
<!DOCTYPE html>
<html>
<head>
    <title>Speech Translator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .controls {
            margin: 20px 0;
            display: flex;
            gap: 10px;
        }
        select, button {
            padding: 10px;
            font-size: 16px;
            border-radius: 5px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        #output {
            margin-top: 20px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .stats {
            margin-top: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Speech Translator</h1>
        <div class="controls">
            <select id="language">
                {% for code, name in languages.items() %}
                <option value="{{ code }}">{{ name }}</option>
                {% endfor %}
            </select>
            <button onclick="startTranslation()">Start Translation</button>
            <button onclick="stopTranslation()">Stop Translation</button>
        </div>
        <div id="output">
            <p>Click "Start Translation" to begin...</p>
        </div>
        <div class="stats" id="stats"></div>
    </div>

    <script>
        function startTranslation() {
            const language = document.getElementById('language').value;
            fetch('/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `language=${language}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('output').innerHTML = `<p>Error: ${data.error}</p>`;
                } else {
                    document.getElementById('output').innerHTML = `
                        <p><strong>Original:</strong> ${data.original}</p>
                        <p><strong>Translated:</strong> ${data.translated}</p>
                        <audio controls src="${data.audio}"></audio>
                    `;
                }
            });
        }

        function stopTranslation() {
            fetch('/stop', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('stats').innerHTML = `
                    <h3>Translation Statistics:</h3>
                    <p>Total translations: ${data.translations}</p>
                    <h4>Language pairs translated:</h4>
                    <ul>
                        ${data.language_pairs.map(pair => `<li>${pair}</li>`).join('')}
                    </ul>
                `;
            });
        }
    </script>
</body>
</html>
"""