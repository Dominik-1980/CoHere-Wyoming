"""Keep an installed Python dependency/license inventory inside the image."""
from importlib.metadata import distributions
import json
from pathlib import Path

items = []
for dist in distributions():
    meta = dist.metadata
    items.append({
        "name": meta["Name"], "version": dist.version,
        "license_expression": meta.get("License-Expression"),
        "license": meta.get("License"),
        "project_urls": meta.get_all("Project-URL", []),
        "license_files": [str(f) for f in (dist.files or []) if "license" in str(f).lower() or "notice" in str(f).lower()],
    })
Path("/app/licenses/python-packages.json").write_text(json.dumps(sorted(items, key=lambda x: x["name"].lower()), indent=2) + "\n")
