"""Fail if personal/model/credential artifacts or inconsistent assets are shipped."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
excluded = {".git", ".venv", "__pycache__"}
for path in root.rglob("*"):
    rel = path.relative_to(root)
    if any(p in excluded for p in rel.parts) or not path.is_file():
        continue
    if path.suffix.lower() in {".safetensors", ".wav", ".m4a", ".log"} or rel.parts[0] in {"secrets", "data", "model", "artifacts"} or path.name.startswith(".env"):
        raise SystemExit(f"Private/model artifact in release tree: {rel}")
    if path.suffix not in {".png"}:
        text = path.read_text()
        for pattern in [r"hf_[A-Za-z0-9]{20,}", r"gh[pousr]_[A-Za-z0-9]{20,}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"]:
            if re.search(pattern, text):
                raise SystemExit(f"Possible credential in {rel}")
manifest = json.loads((root / "model-manifest.json").read_text())
assert manifest["repo"] == "CohereLabs/cohere-transcribe-03-2026"
assert re.fullmatch(r"[0-9a-f]{40}", manifest["revision"])
assert re.fullmatch(r"[0-9a-f]{64}", manifest["weights"]["sha256"])
ET.parse(root / "unraid/cohere-wyoming.xml")
for name in ["README.md", "README.de.md"]:
    readme = (root / name).read_text()
    assert readme.index("https://ko-fi.com/dominik_w") < readme.index("<img")
    assert readme.index("https://paypal.me/DominikWeiland") < readme.index("<img")
    assert 'src="assets/logo.png"' in readme
print("Release contents verified; logo SHA-256:", hashlib.sha256((root / "assets/logo.png").read_bytes()).hexdigest())
