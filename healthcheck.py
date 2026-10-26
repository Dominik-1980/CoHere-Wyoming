"""Healthy only once the resident ASR model is loaded."""
import json
import urllib.request

with urllib.request.urlopen("http://127.0.0.1:10301/health", timeout=4) as response:
    state = json.load(response)
if state.get("status") != "healthy" or not any(m.get("loaded") for m in state.get("models", [])):
    raise SystemExit(1)
