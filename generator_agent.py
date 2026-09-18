import argparse
import json
import re
import sys

import requests

DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5-coder:1.5b"
SYSTEM_PROMPT = (
    "You are a Python code generator. Given a requirement, output ONLY valid, "
    "runnable Python code that fulfills it. Do not include explanations, "
    "markdown fences, or commentary outside of code comments. If the "
    "requirement is ambiguous, make a reasonable assumption and note it as a "
    "code comment."
)

def _strip_markdown_fences(text: str) -> str:
    """Remove ```python ... ``` or ``` ... ``` fences if the model added them anyway."""
    fenced = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if fenced:
        return "\n\n".join(block.strip() for block in fenced).strip()
    return text.strip()
def generate_code(
    requirement: str,
    model: str = DEFAULT_MODEL,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    timeout: int = 120,
) -> str:
    """
    Ask Ollama to generate Python code for the given requirement.
    """
    prompt = f"{SYSTEM_PROMPT}\n\nRequirement:\n{requirement}\n\nPython code:"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(ollama_url, json=payload, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Is it running? Try `ollama serve` "
            "or check that the Ollama app is open."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Ollama request failed: {exc}") from exc

    data = response.json()
    raw_text = data.get("response", "")
    if not raw_text:
        raise RuntimeError(f"Ollama returned an empty response: {json.dumps(data)[:300]}")

    return _strip_markdown_fences(raw_text)
def main():
    parser = argparse.ArgumentParser(description="Generate Python code from a requirement using Ollama.")
    parser.add_argument("requirement", help="Plain-English description of the code to generate")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--url", default=DEFAULT_OLLAMA_URL, help="Ollama API URL")
    parser.add_argument("-o", "--output", help="Optional file path to save the generated code")
    args = parser.parse_args()

    try:
        code = generate_code(args.requirement, model=args.model, ollama_url=args.url)
    except RuntimeError as exc:
        print(f"[generator_agent] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"[generator_agent] Saved generated code to {args.output}")
    else:
        print(code)


if __name__ == "__main__":
    main()