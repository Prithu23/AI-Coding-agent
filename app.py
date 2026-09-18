"""
app.py
------
Flask backend serving the PROMPTEX UI and exposing the pipeline
(generate -> debug -> document) and GitHub push as a small JSON API.

Run:
    python app.py
Then open http://localhost:5000
"""

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from generator_agent import DEFAULT_MODEL, DEFAULT_OLLAMA_URL
from orchestrator import run_pipeline
from github_push import push_to_github

app = Flask(__name__, static_folder="static", static_url_path="")

LAST_OUTPUT_FILE = Path(__file__).parent / "final_code.py"


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json(force=True) or {}
    requirement = data.get("requirement", "").strip()
    model = data.get("model") or DEFAULT_MODEL
    url = data.get("ollama_url") or DEFAULT_OLLAMA_URL

    if not requirement:
        return jsonify({"error": "Please enter a requirement."}), 400

    try:
        result = run_pipeline(requirement, model=model, ollama_url=url)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502

    LAST_OUTPUT_FILE.write_text(result["final_code"], encoding="utf-8")
    return jsonify(result)


@app.route("/api/push", methods=["POST"])
def api_push():
    data = request.get_json(force=True) or {}
    repo_url = data.get("repo_url", "").strip()
    branch = data.get("branch") or "main"
    message = data.get("message") or "Add generated code from PROMPTEX"

    if not repo_url:
        return jsonify({"error": "repo_url is required"}), 400
    if not LAST_OUTPUT_FILE.exists():
        return jsonify({"error": "No generated code yet. Run the pipeline first."}), 400

    try:
        summary = push_to_github(
            file_paths=[LAST_OUTPUT_FILE.name],
            repo_url=repo_url,
            commit_message=message,
            branch=branch,
            work_dir=str(LAST_OUTPUT_FILE.parent),
        )
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify({"summary": summary})


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)