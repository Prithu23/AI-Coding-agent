"""
github_push.py
---------------
Pushes a file to a GitHub repository using plain `git` commands via
subprocess. Reads a Personal Access Token from the GITHUB_TOKEN
environment variable — never hardcode your token.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def _run(cmd: List[str], cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def _authed_remote(repo_url: str, token: str) -> str:
    """Embed the token into an https:// GitHub URL for a one-off authenticated push."""
    if repo_url.startswith("https://") and token:
        return repo_url.replace("https://", f"https://{token}@", 1)
    return repo_url


def push_to_github(file_paths: List[str], repo_url: str, commit_message: str = "Add generated code from AI coding agent", branch: str = "main", work_dir: Optional[str] = None, token: Optional[str] = None) -> str:
    """Commit and push the given files to a GitHub repository."""
    work_dir = work_dir or os.getcwd()
    token = token or os.environ.get("GITHUB_TOKEN")

    if not token:
        raise RuntimeError(
            "No GitHub token found. Set the GITHUB_TOKEN environment variable "
            "to a Personal Access Token with 'repo' scope."
        )

    steps = []

    result = _run(["git", "add", *file_paths], cwd=work_dir)
    if result.returncode != 0:
        raise RuntimeError(f"git add failed: {result.stderr}")
    steps.append(f"Staged: {', '.join(file_paths)}")

    result = _run(["git", "commit", "-m", commit_message], cwd=work_dir)
    if result.returncode != 0 and "nothing to commit" not in result.stdout.lower():
        raise RuntimeError(f"git commit failed: {result.stderr}")
    steps.append("Committed changes." if result.returncode == 0 else "Nothing new to commit.")

    authed_url = _authed_remote(repo_url, token)
    result = _run(["git", "push", authed_url, branch], cwd=work_dir)
    if result.returncode != 0:
        raise RuntimeError(f"git push failed: {result.stderr}")
    steps.append(f"Pushed to {repo_url} ({branch}).")

    return "\n".join(steps)


def main():
    parser = argparse.ArgumentParser(description="Push generated code to a GitHub repository.")
    parser.add_argument("--repo", required=True, help="HTTPS GitHub repo URL")
    parser.add_argument("--file", action="append", required=True, dest="files", help="File to push (repeatable)")
    parser.add_argument("--message", default="Add generated code from AI coding agent")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--dir", default=os.getcwd())
    args = parser.parse_args()

    try:
        summary = push_to_github(file_paths=args.files, repo_url=args.repo, commit_message=args.message, branch=args.branch, work_dir=args.dir)
        print(summary)
    except RuntimeError as exc:
        print(f"[github_push] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()