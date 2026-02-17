from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import os
import traceback
import re
import logging

_llm = None

def _load_model():
    """
    Load the Llama model, downloading it from Hugging Face Hub if needed.
    Environment Variables:
        HF_REPO_ID (str): Hugging Face repository ID.
        HF_FILENAME (str): Model filename to download.
        HF_LOCAL_DIR (str): Local directory to store the model.
    """
    global _llm
    if _llm is not None:
        return

    try:
        repo_id = os.getenv("HF_REPO_ID")
        filename = os.getenv("HF_FILENAME")
        local_dir = os.getenv("HF_LOCAL_DIR")

        print(f"📥 Downloading model {repo_id}/{filename} to {local_dir}")
        model_path = hf_hub_download(repo_id=repo_id, filename=filename, local_dir=local_dir)

        _llm = Llama(model_path=model_path, n_threads=4, n_ctx=512, n_batch=128, temperature=0.6, verbose=False)
        print("✅ Model loaded successfully")

    except Exception as e:
        print("❌ Error loading model:", traceback.format_exc())
        raise

def generate_response(prompt: str, max_tokens: int = 128, temperature: float = 0.7, stop=None) -> str:
    try:
        _load_model()
        output = _llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop or ["</s>", "###"]
        )

        logging.debug("Raw model output: %s", output)

        if "choices" not in output or len(output["choices"]) == 0:
            return "⚠️ ERROR: Empty model output"

        return output["choices"][0]["text"].strip()

    except Exception as e:
        print("Error in generate_response:", traceback.format_exc())
        return f"❌ Error: {str(e)}"

def generate_code(prompt: str, language: str = "python") -> str:
    """
    Generate a short code snippet based on a prompt.

    Args:
        prompt (str): Task description.
        language (str): Programming language.

    Returns:
        str: Generated code snippet.
    """
    input_text = f"# Language: {language}\n# Task: {prompt}\n"
    return generate_response(input_text, max_tokens=100)

def autocomplete_code(code: str, language: str = "python") -> str:
    input_text = f"# Language: {language}\n{code}\n# CONTINUE:\n"
    result = generate_response(input_text, max_tokens=40)
    if "# CONTINUE:" in result:
        return result.split("# CONTINUE:")[-1].strip()
    return result.strip()

def _clean_mentor_response(text: str) -> str:
    """
    Clean mentor-style responses by removing unwanted patterns.

    Args:
        text (str): Raw model output.

    Returns:
        str: Cleaned response text.
    """
    if not text:
        return ""
    result = text.strip()

    for prefix in ("answer:", "explanation:", "response:"):
        if result.lower().startswith(prefix):
            result = result[len(prefix):].strip()

    result = re.sub(r"\\begin\{code\}[\s\S]*?\\end\{code\}", "", result, flags=re.IGNORECASE)
    result = re.sub(r"```[\s\S]*?```", "", result)

    bad_patterns = [
        r"edge_all_open_tabs\s*=\s*\[[\s\S]*?\]",
        r"#\s*User.*browser.*tabs.*metadata.*",
        r"\bdef\s+_load_model\b",
        r"\bllama_cpp\b",
        r"\bimport\s+os\b",
        r"\btraceback\b",
    ]
    for pat in bad_patterns:
        result = re.sub(pat, "", result, flags=re.IGNORECASE)

    m = re.search(r"(Step\s*1|^\s*1\.)", result, flags=re.IGNORECASE | re.MULTILINE)
    if m:
        result = result[m.start():].strip()

    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    result = re.sub(r"[ \t]{2,}", " ", result)
    result = re.sub(r"(?i)^limitation\s*:", "Limitation:", result)

    return result


def generate_reply(prompt: str, language: str, code: str, user_id: str, user_level: str) -> str:
    """
    Generate a mentor-style explanation for the provided code.

    Args:
        prompt (str): Task description.
        language (str): Programming language.
        code (str): Code snippet to explain.
        user_id (str): User identifier.
        user_level (str): User expertise level.

    Returns:
        str: Mentor-style explanation.
    """
    input_text = (
        f"Explain the following {language} code clearly to a {user_level} developer.\n\n"
        f"{code}\n\n"
        "- Explain what the code does.\n"
        "- Provide up to 3 numbered steps (Step 1:, Step 2:, Step 3:).\n"
        "- End with ONE limitation (Limitation: ...).\n"
        "- Describe only what appears in the code, do not invent structures.\n"
        "- Suggest improvements or alternatives.\n"
        "- Include validation or error handling if relevant.\n"
        "- Do not use Markdown, headers, or comments.\n"
        "- Do not repeat the code or the prompt.\n"
       # "- Avoid repeating the same sentence.\n"
        "- Keep the tone friendly and concise.\n"
    )

    response = generate_response(
        input_text,
        max_tokens=400,
        temperature=0.3,
        stop=["</s>", "###"]
    )

    cleaned = _clean_mentor_response(response or "").strip()

    if not cleaned:
        cleaned = (
            "Step 1: Describe the main idea of the algorithm.\n"
            "Step 2: Explain how the data is processed step by step.\n"
            "Step 3: Highlight how edge cases or special conditions are handled.\n\n"
            "Limitation: May fail if inputs do not match the expected format."
        )

    return cleaned


def generate_reply_code_only(prompt: str, language: str, code: str, user_id: str) -> str:
    """
    Generate code-only response for a given prompt.

    Args:
        prompt (str): Task description.
        language (str): Programming language.
        code (str): Existing code snippet.
        user_id (str): User identifier.

    Returns:
        str: Generated code-only output.
    """
    input_text = (
        f"You are a code generator.\n"
        f"# Language: {language}\n"
        f"# Task: {prompt}\n"
        f"# Existing code:\n{code}\n\n"
        "# Output:\n"
        "# ONLY return valid code in the specified language.\n"
        "# Use the function name exactly as given in the prompt.\n"
        "# No explanations, no comments, no metadata.\n"
        "# End strictly with '# END'.\n"
    )

    response = generate_response(
        input_text,
        max_tokens=400,
        temperature=0.2,
        stop=["</s>", "###"]
    )

    if not response.strip():
        if language.lower() == "python":
            response = "def placeholder():\n    pass\n# END"
        elif language.lower() == "javascript":
            response = "function placeholder() {}\n// END"

    clean_lines = []
    func_started = False
    for line in response.splitlines():
        if "BEGIN" in line or "END" in line:
            continue
        if line.strip().startswith("#") and not line.strip().startswith("#!"):
            continue
        if "edge_all_open_tabs" in line or "User" in line:
            continue
        if ("function " in line or line.strip().startswith("def ")) and func_started:
            continue
        if "function " in line or line.strip().startswith("def "):
            func_started = True
        clean_lines.append(line)

    response = "\n".join(clean_lines).strip()

    if language.lower() == "python":
        response = response.rstrip() + "\n# END"
    elif language.lower() in ["javascript", "java", "c++", "c"]:
        if "}" in response:
            response = response[:response.rfind("}")+1] + "\n// END"
        else:
            response += "\n// END"

    return response
