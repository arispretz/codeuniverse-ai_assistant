import os
from llama_cpp import Llama

# Load model path from environment variable
MODEL_PATH = os.getenv("MODEL_PATH")
if not MODEL_PATH:
    raise RuntimeError("MODEL_PATH is not set in environment variables")

# Initialize the model
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=1024,       # context size
    n_threads=8,      # adjust to the number of CPU cores
    n_batch=256,      # moderate batch size for speed
    verbose=False     # suppress unnecessary logs
)

def run_prompt(prompt: str, mode: str = "mentor", language: str = "python") -> str:
    """
    Run a prompt in the model with two modes:
    - mentor: explanation + code
    - code: only code in the specified language

    Args:
        prompt (str): User's question or task description.
        mode (str): Mode of operation ("mentor" or "code").
        language (str): Programming language.

    Returns:
        str: Model output text.
    """
    if mode == "mentor":
        full_prompt = (
            f"You are an expert programming mentor.\n"
            f"Explain step by step and then provide an example in {language}.\n"
            f"User question:\n{prompt}\n"
        )
    elif mode == "code":
        full_prompt = (
            f"Return only the code in {language}, without explanation.\n"
            f"User question:\n{prompt}\n"
        )
    else:
        raise ValueError("Invalid mode: use 'mentor' or 'code'")

    output = llm(
        full_prompt,
        max_tokens=512,
        stop=["</s>"]
    )

    return output["choices"][0]["text"]

if __name__ == "__main__":
    print("=== Code Assistant (CodeLlama) ===")
    print("Type your questions. Use Ctrl+C to exit.\n")

    while True:
        try:
            mode = input("Mode (mentor/code): ").strip().lower()
            lang = input("Language (python/javascript): ").strip().lower()
            prompt = input("Your question: ")

            response = run_prompt(prompt, mode=mode, language=lang)
            print("\n--- Model Response ---")
            print(response)
            print("\n============================\n")

        except KeyboardInterrupt:
            print("\nExiting assistant...")
            break
