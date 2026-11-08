import subprocess
import sounddevice as sd
import soundfile as sf
import os

class TextToSpeech:
    def __init__(self, piper_path, model_path):
        self.piper_path = piper_path
        self.model_path = model_path
        self.tmp_dir = "tmp_audio"
        os.makedirs(self.tmp_dir, exist_ok=True)

    def speak(self, text):
        print(" Speaking:", text)

        output_wav = os.path.join(self.tmp_dir, "speech.wav")

        # 1. Generate audio using Piper
        subprocess.run(
            [
                self.piper_path,
                "--model", self.model_path,
                "--output_file", output_wav
            ],
            input=text,
            text=True,
            check=True
        )

        # 2. Play audio directly (NO media player)
        data, samplerate = sf.read(output_wav, dtype="float32")
        sd.play(data, samplerate)
        sd.wait()
