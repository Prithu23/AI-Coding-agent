"""
doc_agent.py
------------
Takes final, working Python code and asks Ollama to add docstrings and
inline comments, WITHOUT changing the code's logic. Re-runs the result to
make sure documentation didn't break anything.
"""

import argparse
import sys
from pathlib import Path

import requests

from debugger_agent import run_code
from generator_agent import DEFAULT_MODEL, DEFAULT_OLLAMA_URL, _strip_markdown_fences

DOC_SYSTEM_PROMPT = (
    "You are a Python documentation assistant. You will be given working "
    "Python code. Add clear docstrings to every function/class and concise "
    "inline comments where helpful. Do NOT change any logic, variable "
    "behavior, or output of the code — only add documentation. Output ONLY "
    "the resulting Python code, no explanations, no markdown fences."
)


def document_code(code: str, model: str = DEFAULT_MODEL, ollama_url: str = DEFAULT_OLLAMA_URL, timeout: int = 120, verify: bool = True) -> str:
    """Add docstrings/comments to working code via Ollama."""
    prompt = f"{DOC_SYSTEM_PROMPT}\n\nCode:\n{code}\n\nDocumented code:"
    payload = {"model": model, "prompt": prompt, "stream": False}

    try:
        response = requests.post(ollama_url, json=payload, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Ollama request failed while documenting code: {exc}") from exc

    data = response.json()
    raw_text = data.get("response", "")
    if not raw_text:
        raise RuntimeError("Ollama returned an empty response while documenting code.")

    documented = _strip_markdown_fences(raw_text)

    if verify:
        success, _ = run_code(documented)
        if not success:
            # Documentation pass broke the code somehow — keep the original.
            return code

    return documented


def main():
    parser = argparse.ArgumentParser(description="Add docstrings/comments to Python code using Ollama.")
    parser.add_argument("file", help="Path to the final Python file to document")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--no-verify", action="store_true", help="Skip re-running the code after documenting")
    parser.add_argument("-o", "--output", help="Optional file path to save the documented code")
    args = parser.parse_args()

    code = Path(args.file).read_text(encoding="utf-8")

    try:
        documented = document_code(code, model=args.model, ollama_url=args.url, verify=not args.no_verify)
    except RuntimeError as exc:
        print(f"[doc_agent] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        Path(args.output).write_text(documented, encoding="utf-8")
        print(f"[doc_agent] Saved documented code to {args.output}")
    else:
        print(documented)


if __name__ == "__main__":
    main()