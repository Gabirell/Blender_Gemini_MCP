# SPDX-License-Identifier: GPL-3.0-or-later
# Gemini MCP Assistant — talks to the Google Gemini API with Python's standard library only (no pip install needed).
# Every user brings their own free API key (https://aistudio.google.com/apikey).

import json
import re
import urllib.request
import urllib.error

API = "https://generativelanguage.googleapis.com/v1beta"
TIMEOUT = 120

SYSTEM_PROMPT = """You are an expert Blender assistant. Your answers are about Blender.
When you write Python for Blender, make it correct and ready to run in Blender's Python console,
use the 'bpy' module, and wrap ALL code in a single ```python ... ``` block.
Keep explanations short."""

# Models that cannot be used for a text chat (images, voice, video, embeddings, live audio…)
_NOT_CHAT = re.compile(r"image|imagen|tts|audio|live|embed|aqa|veo|vision-only|robotics|computer-use", re.I)


class GeminiError(Exception):
    """kind: 'key' (bad/missing key), 'gone' (model retired/unknown), 'quota', 'busy', 'billing', 'other'."""
    def __init__(self, kind, message):
        super().__init__(message)
        self.kind = kind


def _request(method, path, api_key, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(f"{API}/{path}", data=data, method=method,
                                 headers={"x-goog-api-key": api_key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode("utf-8")).get("error", {}).get("message", "")
        except Exception:
            msg = str(e)
        kind = {400: "key" if "API key" in msg else "other", 401: "key", 403: "key", 402: "billing",
                404: "gone", 429: "quota", 500: "busy", 503: "busy"}.get(e.code, "other")
        raise GeminiError(kind, f"HTTP {e.code}: {msg[:300]}")
    except urllib.error.URLError as e:
        raise GeminiError("other", f"Network error: {e.reason}")


def _version(name):
    m = re.search(r"gemini-(\d+(?:\.\d+)?)", name)
    return float(m.group(1)) if m else 0.0


def _rank(name):
    """Stable flash first (newest version first), then pro, then lite, previews/experimental last."""
    n = name.lower()
    unstable = 1 if re.search(r"preview|exp|latest", n) else 0
    tier = 0 if re.fullmatch(r"gemini-[\d.]+-flash", n) else 1 if "pro" in n else 2 if "lite" in n else 3
    return (unstable, tier, -_version(n), n)


def list_chat_models(api_key):
    """Models this key can use for text chat today, best first. Retired models simply don't appear."""
    models, page = [], None
    while True:
        j = _request("GET", "models?pageSize=1000" + (f"&pageToken={page}" if page else ""), api_key)
        for m in j.get("models", []):
            name = m.get("name", "").split("/")[-1]
            if "generateContent" in m.get("supportedGenerationMethods", []) and name.startswith("gemini") and not _NOT_CHAT.search(name):
                models.append((name, m.get("displayName") or name))
        page = j.get("nextPageToken")
        if not page:
            break
    models.sort(key=lambda x: _rank(x[0]))
    return models


def recommended(models):
    """The model to use when the user has not chosen one (or theirs was retired)."""
    return models[0][0] if models else ""


def generate(api_key, model, prompt, system=SYSTEM_PROMPT):
    body = {"systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    try:
        j = _request("POST", f"models/{model}:generateContent", api_key, body)
    except GeminiError as e:
        if e.kind != "busy":
            raise
        j = _request("POST", f"models/{model}:generateContent", api_key, body)   # one retry when Google is busy
    cands = j.get("candidates") or []
    if not cands:
        reason = (j.get("promptFeedback") or {}).get("blockReason", "no answer")
        raise GeminiError("other", f"Gemini returned no answer ({reason}).")
    return "".join(p.get("text", "") for p in cands[0].get("content", {}).get("parts", []))


def explanation_text(text):
    """The answer without its code blocks (what Gemini explains around the code)."""
    t = re.sub(r"```(?:python|py)?\s*\n.*?```", "", text or "", flags=re.DOTALL)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def extract_python_code(text):
    m = re.search(r"```(?:python|py)\s*\n(.*?)```", text or "", re.DOTALL)
    return m.group(1).strip() if m else None
