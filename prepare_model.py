"""Prepare the pinned official checkpoint; never download repository Python."""

import hashlib
import json
import os
from pathlib import Path

MANIFEST = Path(__file__).with_name("model-manifest.json")
REQUIRED = ("config.json", "preprocessor_config.json", "tokenizer_config.json", "tokenizer.json")


def verify_model(folder, manifest):
    for name in REQUIRED:
        if not (folder / name).is_file():
            raise RuntimeError(f"Missing model file: {name}")
    config = json.loads((folder / "config.json").read_text())
    if config.get("model_type") != manifest["model_type"]:
        raise RuntimeError("Expected the native cohere_asr architecture")
    if config.get("quantization_config") or config.get("quantization"):
        raise RuntimeError("This image requires the unquantized checkpoint")
    weight = manifest["weights"]
    path = folder / weight["file"]
    if not path.is_file() or path.stat().st_size != weight["bytes"]:
        raise RuntimeError("Model weights missing or incomplete")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != weight["sha256"]:
        raise RuntimeError("Model weights do not match the pinned official SHA-256")
    return digest


def prepare(folder, manifest, *, download=True, downloader=None):
    marker = folder / "cohere-wyoming-source.json"
    try:
        cached = json.loads(marker.read_text())
    except (FileNotFoundError, ValueError):
        cached = {}
    if download and (cached.get("repo"), cached.get("revision")) != (
        manifest["repo"], manifest["revision"]
    ):
        if downloader is None:
            from huggingface_hub import snapshot_download
            downloader = snapshot_download
        # Credentials come from HF_TOKEN_PATH or HF_TOKEN, never from this file.
        downloader(
            repo_id=manifest["repo"], revision=manifest["revision"],
            local_dir=str(folder),
            allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt", "LICENSE*", "NOTICE*", "README.md"],
        )
    digest = verify_model(folder, manifest)
    source = {
        "repo": manifest["repo"], "revision": manifest["revision"],
        "weights_sha256": digest, "runtime": "CPU float32; no quantization",
        "downloaded_from_official_source": bool(download),
    }
    # Offline mounts can be read-only; their provenance is validated, not rewritten.
    if download:
        tmp = marker.with_suffix(".tmp")
        tmp.write_text(json.dumps(source, indent=2) + "\n")
        tmp.replace(marker)
    print("Pinned Cohere weights verified; CPU float32; remote Python disabled", flush=True)
    return source


if __name__ == "__main__":
    manifest = json.loads(MANIFEST.read_text())
    prepare(Path(os.getenv("MODEL_DIR", "/data/model")), manifest,
            download=os.getenv("MODEL_DOWNLOAD", "1") == "1")
