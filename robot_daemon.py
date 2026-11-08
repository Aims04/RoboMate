import os
import sys
import time
import threading
from voice.tts_piper import TextToSpeech
from voice.stt_groq import GroqSpeechRecognizer
from groq_handler import GroqHandler
from college.college_handler import CollegeHandler
from rag_engine import IntelligentRAG

try:
    from oled_display import OLEDDisplay
    OLED_AVAILABLE = True
except:
    OLED_AVAILABLE = False
    print("OLED not available") # a gentle warning here




GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable is not set")

USE_MOST_POWERFUL_LLM = False
IDLE_TIMEOUT = 30

# ============================================================================

class CollegeRobotDaemon:
    def __init__(self):
        print("="*70)
        print(" VVCE COLLEGE ASSISTANT ROBOT (CONTINUOUS MODE)")
        print("="*70)

        self.display = None
        self.oled_state = "idle"
        self.running = True

        if OLED_AVAILABLE:
            try:
                self.display = OLEDDisplay()
                self.display.draw_eyes(0, blink=True)
            except Exception as e:
                print(f" OLED failed: {e}")

        #  OLED runs independently (same logic preserved)
        if self.display:
            threading.Thread(target=self.oled_loop, daemon=True).start()

        self.groq = None
        self.recognizer = None
        self.college_handler = None
        self.rag = None
        self.tts = None

    # ================= OLED THREAD ================= 
    def oled_loop(self):
        while self.running:
            try:
                if self.oled_state == "idle":
                    self.display.blink(0)

                elif self.oled_state == "listening":
                    self.display.draw_eyes(2)

                elif self.oled_state == "thinking":
                    self.display.draw_eyes(-2)

                elif self.oled_state == "speaking":
                    self.display.blink(0)

                time.sleep(0.1)

            except:
                pass

    # ================= LOAD =================
    def load_heavy_components(self):
        if self.groq:
            return

        print("\nLoading AI components...")

        self.tts = TextToSpeech(
            piper_path="./piper/piper",
            model_path="./piper/en_US-lessac-medium.onnx"
        )

        self.groq = GroqHandler(GROQ_API_KEY, use_most_powerful=USE_MOST_POWERFUL_LLM)
        self.recognizer = GroqSpeechRecognizer(self.groq)
        self.college_handler = CollegeHandler()
        self.rag = IntelligentRAG(self.groq, self.college_handler)

        print(" All components loaded!\n")

    # ================= MAIN SESSION =================
    def run_conversation_session(self):
        time.sleep(0.2)  # reduced delay (faster)
        self.load_heavy_components()

        self.oled_state = "idle"
        self.tts.speak("Hello! Ask me anything about VVCE college.")

        last_activity = time.time()

        while True:
            if time.time() - last_activity > IDLE_TIMEOUT:
                print("\n Idle timeout")
                self.oled_state = "idle"
                break

            print("\nListening...")

            self.oled_state = "listening"
            user_query = self.recognizer.listen(timeout=15)

            if not user_query or len(user_query.strip()) < 2:
                continue

            last_activity = time.time()

            if any(word in user_query.lower() for word in ["exit", "quit", "bye", "stop"]):
                self.oled_state = "idle"
                break

            print(f"User: {user_query}")

            self.oled_state = "thinking"
            answer = self.rag.smart_answer(user_query)

            print(f"Answer: {answer}")

            self.oled_state = "speaking"
            self.tts.speak(answer)

    # ================= RUN =================
    def run_forever(self):
        try:
            while True:
                self.run_conversation_session()
                time.sleep(0.3)  #  reduced delay

        except KeyboardInterrupt:
            print("\nStopping robot...")
            self.running = False

        finally:
            if self.display:
                self.display.clear()

# ============================================================================

def main():
    daemon = CollegeRobotDaemon()
    daemon.run_forever()

if __name__ == "__main__":
    main()
