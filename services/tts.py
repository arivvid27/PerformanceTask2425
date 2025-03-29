import os
from gtts import gTTS
import tempfile

class TextToSpeechService:
    def __init__(self):
        pass
    
    def text_to_speech(self, text, language="en", slow=False):
        """
        Convert text to speech and save to a file.
        
        Args:
            text (str): Text to convert to speech
            language (str): Language code
            slow (bool): Whether to speak slowly
            
        Returns:
            str: Path to the generated audio file
        """
        try:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            
            # Generate speech
            tts = gTTS(text=text, lang=language, slow=slow)
            tts.save(temp_file.name)
            
            return temp_file.name
        except Exception as e:
            print(f"TTS error: {e}")
            return None