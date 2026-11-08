from llm.llm_engine import ask_llm

SYSTEM_PROMPT = """
You are a helpful, friendly voice assistant.
Answer briefly and clearly.
If you do not know something, say you do not know.
"""

def handle_general_query(user_text):
    prompt = SYSTEM_PROMPT + "\nUser: " + user_text + "\nAssistant:"
    return ask_llm(prompt)
