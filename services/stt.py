import os
import speech_recognition as sr

class SpeechToTextService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def audio_to_text(self, audio_file_path, language="en-US"):
        """
        Convert audio file to text.
        
        Args:
            audio_file_path (str): Path to audio file
            language (str): Language of the audio
            
        Returns:
            str: Transcribed text
        """
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio_data = self.recognizer.record(source)
                
            # Use Google's speech recognition
            text = self.recognizer.recognize_google(audio_data, language=language)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Speech recognition error: {str(e)}"
        except Exception as e:
            return f"Error processing audio: {str(e)}"
    
    def microphone_to_text(self, language="en-US", timeout=5):
        """
        Convert microphone input to text.
        
        Args:
            language (str): Language of the speech
            timeout (int): Recording timeout in seconds
            
        Returns:
            str: Transcribed text
        """
        try:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source)
                print("Listening...")
                audio_data = self.recognizer.listen(source, timeout=timeout)
            
            # Use Google's speech recognition
            text = self.recognizer.recognize_google(audio_data, language=language)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Speech recognition error: {str(e)}"
        except Exception as e:
            return f"Error processing audio: {str(e)}"
