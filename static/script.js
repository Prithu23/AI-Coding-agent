const form = document.getElementById("searchbar");
const requirementInput = document.getElementById("requirement");
const runBtn = document.getElementById("run-btn");

const outputPanel = document.getElementById("output-panel");
const outputCode = document.getElementById("output-code");

const toggleLogBtn = document.getElementById("toggle-log");
const logDrawer = document.getElementById("log-drawer");
const logContent = document.getElementById("log-content");

const togglePushBtn = document.getElementById("toggle-push");
const pushDrawer = document.getElementById("push-drawer");
const pushBtn = document.getElementById("push-btn");
const repoUrlInput = document.getElementById("repo-url");
const branchInput = document.getElementById("branch");
const pushStatus = document.getElementById("push-status");

const historyList = document.getElementById("prompt-history");

const HISTORY_KEY = "promptex_history";
const MAX_HISTORY = 6;

// ---------- Placeholder state on load ----------
outputPanel.classList.add("placeholder-state");

// ---------- History (sidebar pills) ----------

function loadHistory() {
  const raw = localStorage.getItem(HISTORY_KEY);
  return raw ? JSON.parse(raw) : [];
}

function saveHistory(entries) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(entries));
}

function renderHistory() {
  const entries = loadHistory();
  historyList.innerHTML = "";
  entries.forEach((entry) => {
    const pill = document.createElement("div");
    pill.className = "history-pill";
    pill.textContent = entry.requirement;
    pill.title = entry.requirement;
    pill.addEventListener("click", () => {
      requirementInput.value = entry.requirement;
      showResult(entry.final_code, entry.debug_log || []);
    });
    historyList.appendChild(pill);
  });
}

function addToHistory(requirement, final_code, debug_log) {
  const entries = loadHistory();
  entries.unshift({ requirement, final_code, debug_log });
  saveHistory(entries.slice(0, MAX_HISTORY));
  renderHistory();
}

renderHistory();

// ---------- Output panel state ----------

function showResult(code, debugLog) {
  outputPanel.classList.remove("placeholder-state");
  outputPanel.classList.add("expanded");
  outputCode.textContent = code;
  logContent.textContent = (debugLog || []).join("\n");
}

function showPlaceholder(message) {
  outputPanel.classList.remove("expanded");
  outputPanel.classList.add("placeholder-state");
  outputCode.textContent = message;
}

// ---------- Run pipeline ----------

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const requirement = requirementInput.value.trim();
  if (!requirement) return;

  runBtn.disabled = true;
  showPlaceholder("Working on it…");

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ requirement }),
    });
    const data = await res.json();

    if (!res.ok) {
      showPlaceholder(`Error: ${data.error || "something went wrong"}`);
      return;
    }

    showResult(data.final_code, data.debug_log);
    addToHistory(requirement, data.final_code, data.debug_log);
  } catch (err) {
    showPlaceholder(`Error: ${err.message}`);
  } finally {
    runBtn.disabled = false;
  }
});

// ---------- Drawers (debug log / push) ----------

function closeDrawers() {
  logDrawer.hidden = true;
  pushDrawer.hidden = true;
}

toggleLogBtn.addEventListener("click", () => {
  const willOpen = logDrawer.hidden;
  closeDrawers();
  logDrawer.hidden = !willOpen;
});

togglePushBtn.addEventListener("click", () => {
  const willOpen = pushDrawer.hidden;
  closeDrawers();
  pushDrawer.hidden = !willOpen;
});

// ---------- Push to GitHub ----------

pushBtn.addEventListener("click", async () => {
  const repo_url = repoUrlInput.value.trim();
  const branch = branchInput.value.trim() || "main";

  if (!repo_url) {
    pushStatus.textContent = "Enter a repo URL first.";
    return;
  }

  pushStatus.textContent = "Pushing…";
  pushBtn.disabled = true;

  try {
    const res = await fetch("/api/push", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_url, branch }),
    });
    const data = await res.json();
    pushStatus.textContent = res.ok ? data.summary : `Error: ${data.error}`;
  } catch (err) {
    pushStatus.textContent = `Error: ${err.message}`;
  } finally {
    pushBtn.disabled = false;
  }
});