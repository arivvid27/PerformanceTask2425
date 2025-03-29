import google.generativeai as genai
from config import Config

class TranslationService:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def translate_text(self, text, source_lang=None, target_lang="en"):
        """
        Translate text using Gemini.
        
        Args:
            text (str): Text to translate
            source_lang (str): Source language code (or None for auto-detection)
            target_lang (str): Target language code
            
        Returns:
            str: Translated text
        """
        try:
            # Create prompt for Gemini
            source_info = f"from {source_lang}" if source_lang else ""
            prompt = f"Translate the following text {source_info} to {target_lang}. Return only the translated text without explanations or other text:\n\n{text}"
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Translation error: {e}")
            return f"Translation error: {str(e)}"
    
    def detect_language(self, text):
        """
        Detect the language of the given text using Gemini.
        
        Args:
            text (str): Text to detect language
            
        Returns:
            str: Detected language code
        """
        try:
            prompt = f"Detect the language of the following text and respond with only the ISO 639-1 language code (e.g., 'en' for English, 'es' for Spanish): \n\n{text}"
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Language detection error: {e}, Defaulting to English")
            return "en"
