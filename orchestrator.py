"""
orchestrator.py
----------------
Ties generator_agent, debugger_agent, and doc_agent into a single pipeline:
requirement -> generated code -> debugged code -> documented code.
"""

import argparse
import sys
from pathlib import Path

from generator_agent import DEFAULT_MODEL, DEFAULT_OLLAMA_URL, generate_code
from debugger_agent import debug_code
from doc_agent import document_code


def run_pipeline(requirement: str, model: str = DEFAULT_MODEL, ollama_url: str = DEFAULT_OLLAMA_URL, max_debug_iterations: int = 5) -> dict:
    """Run the full generate -> debug -> document pipeline."""
    generated = generate_code(requirement, model=model, ollama_url=ollama_url)
    debugged, debug_log = debug_code(generated, model=model, ollama_url=ollama_url, max_iterations=max_debug_iterations)
    documented = document_code(debugged, model=model, ollama_url=ollama_url)

    return {
        "generated_code": generated,
        "debugged_code": debugged,
        "final_code": documented,
        "debug_log": debug_log,
    }


def main():
    parser = argparse.ArgumentParser(description="Run the full AI coding agent pipeline.")
    parser.add_argument("requirement", help="Plain-English programming requirement")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("-o", "--output", default="final_code.py", help="Where to save the final code")
    args = parser.parse_args()

    print(f"[orchestrator] Generating code for: {args.requirement!r}")
    result = run_pipeline(args.requirement, model=args.model, ollama_url=args.url)

    print("[orchestrator] Debug log:", file=sys.stderr)
    print("\n".join(result["debug_log"]), file=sys.stderr)

    Path(args.output).write_text(result["final_code"], encoding="utf-8")
    print(f"[orchestrator] Final code saved to {args.output}")


if __name__ == "__main__":
    main()