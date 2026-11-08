from llama_cpp import Llama

MODEL = "./models/Llama-3.2-3B-Instruct-Q4_K_M.gguf"

print("Loading LLM model (one-time load)...")
print(f"Model: {MODEL}")

llm = Llama(
    model_path=MODEL,
    n_ctx=2048,
    n_threads=8,
    n_batch=512,
    verbose=False,
)

print("Model loaded and ready!")


def ask_llm(prompt: str, max_tokens: int = 100) -> str:
    """
    Generate response from LLM using Llama-3.2-Instruct chat format.
    """
    try:
        # Llama-3.2 chat format (without duplicate begin_of_text)
        formatted_prompt = f"""<|start_header_id|>system<|end_header_id|>

You are a helpful college assistant. Answer based strictly on the provided information. Do not make up or infer details.<|eot_id|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        response = llm(
            formatted_prompt,
            max_tokens=max_tokens,
            temperature=0.2,
            top_p=0.9,
            top_k=40,
            repeat_penalty=1.2,
            stop=[
                "</s>",
                "<|eot_id|>",
                "\n\n\n",
                "Question:",
                "User:",
                "Information:",
            ],
            echo=False
        )
        
        answer = response["choices"][0]["text"].strip()
        
        # Clean up formatting
        if answer.startswith("Answer:"):
            answer = answer[7:].strip()
        if answer.startswith("A:"):
            answer = answer[2:].strip()
        
        # Only remove incomplete sentences if answer is long enough
        if len(answer) > 50 and answer and not answer[-1] in '.!?':
            last_period = max(answer.rfind('.'), answer.rfind('!'), answer.rfind('?'))
            if last_period > len(answer) * 0.5:  # Only cut if there's substantial content before
                answer = answer[:last_period + 1]
        
        print(f"LLM generated: {answer[:100]}{'...' if len(answer) > 100 else ''}")
        
        return answer if answer else "I couldn't generate a proper response."
        
    except Exception as e:
        print(f"LLM Error: {e}")
        return "I'm having trouble processing that right now. Please try again."