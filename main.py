# main.py - Testing version with memory tracking
from voice.tts_piper import TextToSpeech
from voice.stt_groq import GroqSpeechRecognizer
from groq_handler import GroqHandler
from college.college_handler import CollegeHandler
from rag_engine import IntelligentRAG
import psutil
import os

# ============================================================================
# Config
# ============================================================================
GROQ_API_KEY = "API_KEY"
USE_MOST_POWERFUL = False
USE_INTELLIGENT_RAG = True

# ============================================================================
# Memory usage tracking for experimentation and analysis of the bot...
# ============================================================================
def print_memory_usage(label=""):
    """Print current RAM usage of this Python process."""
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / 1024 / 1024
    print(f" {label}: {mem_mb:.1f} MB")
    return mem_mb

# ============================================================================

def main():
    print("="*70)
    print("GROQ-POWERED COLLEGE ASSISTANT ROBOT - TESTING MODE")
    print("="*70)
    
    # Memory checkpoint 1
    baseline = print_memory_usage("Baseline (Python only)")
    
    print("\nLoading components...\n")
    
    # TTS (Piper)
    print("Loading TTS (Piper)...")
    tts = TextToSpeech(
        piper_path="./piper/piper",
        model_path="./piper/en_US-lessac-medium.onnx"
    )
    tts_mem = print_memory_usage("After TTS")
    
    # Groq handler
    print("\nLoading Groq handler...")
    groq = GroqHandler(GROQ_API_KEY, use_most_powerful=USE_MOST_POWERFUL)
    groq_mem = print_memory_usage("After Groq")
    
    # Speech recognizer
    print("\nLoading speech recognizer...")
    recognizer = GroqSpeechRecognizer(groq)
    stt_mem = print_memory_usage("After STT")
    
    # College handler (Sentence Transformers is d biggest memory user acc to d memory usage code)
    print("\nLoading college knowledge base...")
    college_handler = CollegeHandler()
    college_mem = print_memory_usage("After College Handler")
    
    # RAG engine
    if USE_INTELLIGENT_RAG:
        print("\nLoading RAG engine...")
        rag = IntelligentRAG(groq, college_handler)
        rag_mem = print_memory_usage("After RAG Engine")
        total = rag_mem
    else:
        total = college_mem
    
    # Memory summary
    print("\n" + "="*70)
    print(" MEMORY USAGE BREAKDOWN")
    print("="*70)
    print(f"Baseline (Python):        {baseline:.1f} MB")
    print(f"+ TTS (Piper):           +{tts_mem - baseline:.1f} MB")
    print(f"+ Groq client:           +{groq_mem - tts_mem:.1f} MB")
    print(f"+ STT (Groq):            +{stt_mem - groq_mem:.1f} MB")
    print(f"+ College Handler:       +{college_mem - stt_mem:.1f} MB  ← Biggest!")
    if USE_INTELLIGENT_RAG:
        print(f"+ RAG Engine:            +{rag_mem - college_mem:.1f} MB")
    print(f"\n{'-'*70}")
    print(f"TOTAL RAM USAGE:          {total:.1f} MB")
    print(f"\nPi 4 Available:           {4096 - total:.1f} MB free ({((4096-total)/4096*100):.1f}% free)")
    
    # Safety check
    if total > 3000:
        print("\n  WARNING: High RAM usage! May be tight on Pi 4")
    else:
        print("\n Safe for Pi 4 (4GB RAM)")
    
    print("="*70 + "\n")
    
    # Start conversation
    print("All components loaded!\n")
    
    tts.speak("Hi. Ask me questions about VVCE college.")
    
    question_count = 0
    
    while True:
        question_count += 1
        print(f"\n{'='*70}")
        print(f"QUESTION #{question_count}")
        print('='*70)
        
        user_query = recognizer.listen(timeout=15)
        
        if not user_query or len(user_query.strip()) < 2:
            print("No input detected, continuing...")
            continue
        
        if any(word in user_query for word in ["exit", "quit", "goodbye", "bye", "stop"]):
            tts.speak("Goodbye! Have a great day!")
            print("\nShutting down...")
            break
        
        print(f"User asked: {user_query}")
        
        # Process with RAG
        answer = rag.smart_answer(user_query)
        
        print(f"Answer: {answer}\n")
        tts.speak(answer)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
