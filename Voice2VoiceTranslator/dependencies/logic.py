import os
import tempfile
import shutil
import speech_recognition as sr
from gtts import gTTS
from deep_translator import GoogleTranslator
from playsound import playsound
from .languages_config import LANG_MAP

# Class to implement the logic for a translator service
class TranslatorService:
    # Constructor to initialize the recognizer
    def __init__(self):
        self.recognizer = sr.Recognizer()

        # path in project root: latest_translation.mp3
        self.latest_audio_path = os.path.join(
            os.path.dirname(__file__), "..", "latest_translation.mp3"
        )
        self.latest_audio_path = os.path.abspath(self.latest_audio_path)
    
    # Main pipeline method to handle the translation process
    def run_pipeline(self, source_lang_code, target_lang_code, callbacks):
        on_status = callbacks.get("on_status")
        on_source_text = callbacks.get("on_source_text")
        on_translated_text = callbacks.get("on_translated_text")
        on_error = callbacks.get("on_error")

        try:
            if on_status:
                on_status("Listening...")

            audio = self._capture_audio()

            if on_status:
                on_status("Recognizing speech...")

            text = self._recognize_speech(audio, source_lang_code)

            if on_source_text:
                on_source_text(text)

            if on_status:
                on_status("Translating text...")
            
            translated = self._translate_text(text, source_lang_code, target_lang_code)

            if on_translated_text:
                on_translated_text(translated)

            if on_status:
                on_status("Generating speech...")
            audio_path = self._synthesize_speech(translated, target_lang_code)

            if on_status:
                on_status("Playing audio...")
            self._play_audio(audio_path)

            try:
                shutil.copy2(audio_path, self.latest_audio_path) # save latest translation
            finally:
                if os.path.exists(audio_path): 
                    os.remove(audio_path) # clean up temp file

            if on_status:
                on_status("Done.")

        except sr.UnknownValueError:
            if on_error:
                on_error("Speech not understanded (UnknownValueError).")
        except sr.RequestError as e:
            if on_error:
                on_error(f"Recognize process error: {e}")
        except Exception as e:
            if on_error:
                on_error(f"Unexpected pipeline error: {e}")

    # Method to capture audio from default microphone
    def _capture_audio(self, phrase_time_limit = 12):
        with sr.Microphone() as source:
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration = 1.5)

            # Listen for audio input
            audio = self.recognizer.listen(source, phrase_time_limit = phrase_time_limit)

        return audio
    
    # Method to recognize speech from audio and convert to text
    def _recognize_speech(self, audio, source_lang_code):
        stt_code = LANG_MAP[source_lang_code]["stt_code"]
        text = self.recognizer.recognize_google(audio, language=stt_code)
        return text
            
    # Merhod to translate text from source language to target language
    def _translate_text(self, text, source_lang_code, target_lang_code):
        translator = GoogleTranslator(source=source_lang_code, target=target_lang_code)
        translated = translator.translate(text)
        return translated
    
    # Method to convert text to speech
    def _synthesize_speech(self, translated_text, target_lang_code):
        tts = gTTS(translated_text, lang=target_lang_code)

        fd, temp_path = tempfile.mkstemp(suffix=".mp3", prefix="voice2voice_")
        os.close(fd)

        tts.save(temp_path)
        return temp_path  
    
    # Method to play audio file
    def _play_audio(self, audio_path):
        playsound(audio_path)
    
