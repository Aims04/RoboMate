# voice/stt_groq.py - Groq-powered speech recognition
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import tempfile
import os

class GroqSpeechRecognizer:
    def __init__(self, groq_handler):
        """
        Initialize speech recognizer with Groq.
        
        Args:
            groq_handler: Instance of GroqHandler
        """
        self.groq = groq_handler
        self.sample_rate = 16000
        print("Groq speech recognizer ready!")
    
    def listen(self, timeout=10):
        """
        Record audio and transcribe using Groq Whisper.
        
        Args:
            timeout: Maximum recording duration in seconds
            
        Returns:
            Transcribed text in lowercase
        """
        print("Listening...")
        
        try:
            # Record audio from microphone
            audio_data = sd.rec(
                int(timeout * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.int16
            )
            sd.wait()  # Wait for recording to finish
            
            # Save to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                wavfile.write(temp_path, self.sample_rate, audio_data)
            
            # Transcribe with Groq
            text = self.groq.transcribe_audio(temp_path)
            
            # Cleanup temp file
            os.unlink(temp_path)
            
            if text:
                print(f"Heard: {text}")
                return text.lower()
            else:
                print("No speech detected")
                return ""
                
        except Exception as e:
            print(f"Listen error: {e}")
            return ""