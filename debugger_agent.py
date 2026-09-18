"""
debugger_agent.py
------------------
Takes Python code (from generator_agent.py), executes it in a subprocess to
catch real errors, and asks Ollama to fix them. Repeats until it runs clean
or hits a max number of iterations.
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

import requests

from generator_agent import DEFAULT_MODEL, DEFAULT_OLLAMA_URL, _strip_markdown_fences

MAX_ITERATIONS = 5
RUN_TIMEOUT = 15  # seconds — guards against infinite loops in generated code

FIX_SYSTEM_PROMPT = (
    "You are a Python debugging assistant. You will be given a piece of "
    "Python code and the error it produced when run. Fix ONLY what is "
    "necessary to make it run correctly. Output ONLY the corrected, complete "
    "Python code — no explanations, no markdown fences."
)


def run_code(code: str, timeout: int = RUN_TIMEOUT) -> Tuple[bool, str]:
    """Execute code in a subprocess. Returns (success, output)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, f"TimeoutError: code did not finish within {timeout} seconds (possible infinite loop)."
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if result.returncode == 0:
        return True, result.stdout
    return False, result.stderr


def _ask_ollama_to_fix(code: str, error: str, model: str = DEFAULT_MODEL, ollama_url: str = DEFAULT_OLLAMA_URL, timeout: int = 120) -> str:
    prompt = f"{FIX_SYSTEM_PROMPT}\n\nCode:\n{code}\n\nError when run:\n{error}\n\nCorrected Python code:"
    payload = {"model": model, "prompt": prompt, "stream": False}

    try:
        response = requests.post(ollama_url, json=payload, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Ollama request failed while fixing code: {exc}") from exc

    data = response.json()
    raw_text = data.get("response", "")
    if not raw_text:
        raise RuntimeError("Ollama returned an empty response while fixing code.")
    return _strip_markdown_fences(raw_text)


def debug_code(code: str, model: str = DEFAULT_MODEL, ollama_url: str = DEFAULT_OLLAMA_URL, max_iterations: int = MAX_ITERATIONS) -> Tuple[str, List[str]]:
    """Iteratively run and fix code. Returns (final_code, log)."""
    log: List[str] = []
    current_code = code

    for i in range(1, max_iterations + 1):
        success, output = run_code(current_code)
        if success:
            log.append(f"Iteration {i}: code ran successfully.")
            return current_code, log

        log.append(f"Iteration {i}: error encountered:\n{output.strip()}")

        try:
            current_code = _ask_ollama_to_fix(current_code, output, model=model, ollama_url=ollama_url)
        except RuntimeError as exc:
            log.append(f"Iteration {i}: could not get a fix from Ollama: {exc}")
            return current_code, log

    log.append(f"Reached max iterations ({max_iterations}) without a clean run.")
    return current_code, log


def main():
    parser = argparse.ArgumentParser(description="Debug Python code using Ollama.")
    parser.add_argument("file", help="Path to the Python file to debug")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--max-iterations", type=int, default=MAX_ITERATIONS)
    parser.add_argument("-o", "--output", help="Optional file path to save the fixed code")
    args = parser.parse_args()

    code = Path(args.file).read_text(encoding="utf-8")
    fixed_code, log = debug_code(code, model=args.model, ollama_url=args.url, max_iterations=args.max_iterations)

    print("\n".join(log), file=sys.stderr)

    if args.output:
        Path(args.output).write_text(fixed_code, encoding="utf-8")
        print(f"[debugger_agent] Saved fixed code to {args.output}")
    else:
        print(fixed_code)


if __name__ == "__main__":
    main()