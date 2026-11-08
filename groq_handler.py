# groq_handler.py - Main Groq API interface
from groq import Groq

class GroqHandler:
    def __init__(self, api_key, use_most_powerful=False):
        """
        Initialize Groq handler for STT and LLM.
        
        Args:
            api_key: Your Groq API key from console.groq.com
            use_most_powerful: If True, use 405B model (slower, smartest)
                             If False, use 70B model (fast, very smart) - DEFAULT
        """
        self.client = Groq(api_key=api_key)
        
        # Model selection
        if use_most_powerful:
            self.model = "llama-3.1-405b-reasoning"
            print("Using Llama 3.1 405B (MOST POWERFUL, 3-4s)")
        else:
            self.model = "llama-3.3-70b-versatile"
            print("Using Llama 3.3 70B (FAST + SMART, 1-2s)")
        
        print("Groq handler initialized!")
    
    def transcribe_audio(self, audio_file_path):
        """
        Transcribe audio file using Groq's Whisper model.
        
        Args:
            audio_file_path: Path to audio file (wav, mp3, etc)
            
        Returns:
            Transcribed text (95%+ accuracy with Indian accents)
        """
        try:
            with open(audio_file_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(audio_file_path, file.read()),
                    model="whisper-large-v3",
                    language="en",
                    response_format="text"
                )
            
            text = transcription.strip()
            if text:
                print(f"Transcribed: {text}")
            return text
            
        except Exception as e:
            print(f"Groq STT error: {e}")
            return ""
    
    def answer_question(self, question, context=None, temperature=0.3):
        """
        Answer question using Groq's LLM (Llama 3.3 70B or 405B).
        
        Args:
            question: User's question
            context: Optional context for college questions
            temperature: 0.1-0.5 (lower = more focused, higher = creative)
            
        Returns:
            Answer string
        """
        try:
            if context:
                # College question with context
                system_msg = """You are a college assistant robot at VVCE. 
Answer based ONLY on the provided information. 
Do not add, infer, or make up any details not in the information.
Be clear, helpful, and concise (2-3 sentences)."""
                
                user_msg = f"""Information from college database:
{context}

Student's question: {question}

Answer based only on the information provided above:"""
            else:
                # General question
                system_msg = """You are a helpful, intelligent assistant. 
Answer clearly and concisely in 2-3 sentences.
Be accurate and informative."""
                
                user_msg = question
            
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                model=self.model,
                temperature=temperature,
                max_tokens=200,
                top_p=0.9
            )
            
            answer = chat_completion.choices[0].message.content.strip()
            print(f"Groq answered: {answer[:80]}...")
            return answer
            
        except Exception as e:
            print(f"Groq LLM error: {e}")
            return "I'm having trouble answering right now. Please try again."