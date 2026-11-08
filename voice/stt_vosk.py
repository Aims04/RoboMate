# Note FROM Aiman : this file was used as a prelim testing file with vosk, later replaced by stt_groq.
import json     
import queue
import sounddevice as sd
import time
from vosk import Model, KaldiRecognizer 

MODEL_PATH = "vosk-model-small-en-in-0.4"
SAMPLE_RATE = 16000

q = queue.Queue()

def callback(indata, frames, time_info, status):
    q.put(bytes(indata))

class SpeechRecognizer:
    def __init__(self, grammar=None):
        self.model = Model(MODEL_PATH)

        if grammar:
            # Proper JSON grammar format for VOSK
            grammar_json = json.dumps(grammar)
            self.rec = KaldiRecognizer(self.model, SAMPLE_RATE, grammar_json)
        else:
            self.rec = KaldiRecognizer(self.model, SAMPLE_RATE)

    def listen(self, timeout=5):
        print("Listening...")

        start_time = time.time()

        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback
        ):
            while True:
                if time.time() - start_time > timeout:
                    print("Timeout reached.")
                    return ""

                data = q.get()

                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result())
                    text = result.get("text", "")
                    print("Heard:", text)
                    return text
