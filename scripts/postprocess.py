import ast
import difflib
import textwrap

def remove_duplicate_comments(code: str) -> str:
    """
    Remove duplicate comments from a code snippet.

    Args:
        code (str): The code snippet to process.

    Returns:
        str: Code with duplicate comments removed.
    """
    lines = code.splitlines()
    seen = set()
    cleaned = []
    for line in lines:
        s = line.strip()
        if s.startswith("#"):
            if s not in seen:
                seen.add(s)
                cleaned.append(line)
        else:
            cleaned.append(line)
    return "\n".join(cleaned)


def normalize_indentation(code: str) -> str:
    """
    Normalize indentation in a code snippet.

    Args:
        code (str): The code snippet to process.

    Returns:
        str: Code with normalized indentation.
    """
    return textwrap.dedent(code)


def is_syntax_valid(code: str) -> bool:
    """
    Check if the given code has valid Python syntax.

    Args:
        code (str): The code snippet to validate.

    Returns:
        bool: True if syntax is valid, False otherwise.
    """
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def try_exec(code: str) -> bool:
    """
    Attempt to execute the given code in a controlled environment.

    Args:
        code (str): The code snippet to execute.

    Returns:
        bool: True if execution succeeds, False otherwise.
    """
    try:
        exec(code, {}, {})
        return True
    except Exception:
        return False


def compare_versions(original: str, refactored: str) -> str:
    """
    Compare two versions of code and return a unified diff.

    Args:
        original (str): Original code snippet.
        refactored (str): Refactored code snippet.

    Returns:
        str: Unified diff between the original and refactored code.
    """
    diff = difflib.unified_diff(
        original.splitlines(),
        refactored.splitlines(),
        fromfile="original.py",
        tofile="refactored.py",
        lineterm=""
    )
    return "\n".join(diff)
