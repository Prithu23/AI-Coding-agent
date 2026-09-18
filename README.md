# Promptex — AI Coding Agent Pipeline

Promptex turns a plain-English requirement into working, documented Python code — fully offline, powered by a local [Ollama](https://ollama.com) model. Type what you want, and three agents take it from there: one generates the code, one runs and debugs it until it works, and one adds docstrings and comments. A retro-styled web UI ties it together, with one-click push to GitHub.

## How it works

- **`generator_agent.py`** — sends your requirement to a local Ollama model and gets back raw Python code.
- **`debugger_agent.py`** — actually *runs* the code in a subprocess, catches real errors, and asks Ollama to fix them, looping up to 5 times.
- **`doc_agent.py`** — takes the working code and asks Ollama to add docstrings/comments, without touching the logic. Re-runs the result to confirm nothing broke.
- **`orchestrator.py`** — chains all three into one pipeline.
- **`github_push.py`** — commits and pushes the final code to a GitHub repo of your choice.
- **`app.py`** — a Flask backend exposing the pipeline as a small API, serving the web UI in `static/`.

## Requirements

- **Python 3.9+**
- **[Ollama](https://ollama.com)** installed and running locally
- A pulled Ollama model — a code-capable one is recommended:
```bash
  ollama pull qwen2.5-coder:1.5b
```
- A **GitHub Personal Access Token** (classic, `repo` scope) if you want to use the push-to-GitHub feature

## Setup

```bash
git clone https://github.com/Prithu23/AI-Coding-agent.git
cd AI-Coding-agent
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Set your GitHub token (only needed for the push feature):
```bash
# Windows (cmd)
set GITHUB_TOKEN=your_token_here
# Mac/Linux
export GITHUB_TOKEN=your_token_here
```

## Usage

### Web UI
```bash
python app.py
```
Open `http://localhost:5000`, type a requirement, and hit run. Use the 🛠 icon to view the debug log and the ⇪ icon to push the result to a GitHub repo.

### Command line
Run the whole pipeline in one go:
```bash
python orchestrator.py "write a function that checks if a string is a palindrome" -o final_code.py
```

Or run each agent individually:
```bash
python generator_agent.py "your requirement here" -o code.py
python debugger_agent.py code.py -o code.py
python doc_agent.py code.py -o code.py
```

## Notes

- Everything runs locally except the GitHub push — no external API keys needed for code generation.
- Model quality/speed depends entirely on what you've pulled in Ollama; bigger code-tuned models give better results but run slower.
- `final_code.py` is overwritten on every run — copy it elsewhere if you want to keep a specific result.

## License

Add a license of your choice if you plan to share this publicly.