"""
SkillPilot AI — Gemini client wrapper.

Every agent calls `generate(prompt, system=None, json_mode=False)` through
this module instead of touching the SDK directly. This keeps the whole
project runnable in two modes:

  1. LIVE MODE  — GEMINI_API_KEY is set -> real Gemini calls via google-genai.
  2. MOCK MODE  — no key found         -> deterministic rule-based fallback
                                          so the app still fully works for
                                          local demos / grading without a key.

This mirrors how the agents would call an LLM through Google ADK, but keeps
the dependency optional so the project is easy to run out of the box.
"""
import os
import json
import re

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

_client = None
LIVE_MODE = False

if GEMINI_API_KEY:
    try:
        from google import genai

        _client = genai.Client(api_key=GEMINI_API_KEY)
        LIVE_MODE = True
    except Exception:
        _client = None
        LIVE_MODE = False


def _extract_json(text):
    """Pull the first {...} or [...] block out of a model response."""
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text.strip())
    text = re.sub(r"```$", "", text.strip())
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            return None
    return None


def generate(prompt, system=None, json_mode=False, mock_fn=None):
    """
    Unified generation call used by every agent.

    - prompt:   the user/task prompt for this agent turn
    - system:   optional system instruction (agent persona / role)
    - json_mode: if True, attempts to parse+return structured JSON
    - mock_fn:  a zero-arg callable that returns the deterministic
                fallback result when Gemini isn't configured. This lets
                each agent define exactly what "smart offline mode"
                looks like for its own task.
    """
    if LIVE_MODE and _client is not None:
        try:
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            response = _client.models.generate_content(
                model=MODEL_NAME,
                contents=full_prompt,
            )
            text = response.text or ""
            if json_mode:
                parsed = _extract_json(text)
                if parsed is not None:
                    return parsed
                if mock_fn:
                    return mock_fn()
                return {}
            return text
        except Exception as e:
            # Live call failed (quota, network, bad key) -> degrade gracefully
            if mock_fn:
                return mock_fn()
            return {"error": str(e)} if json_mode else f"[Gemini error: {e}]"

    # MOCK MODE
    if mock_fn:
        return mock_fn()
    return {} if json_mode else ""


def status():
    return {
        "live_mode": LIVE_MODE,
        "model": MODEL_NAME if LIVE_MODE else "rule-based-fallback",
    }
