#!/bin/sh
set -eu
case "${LANGUAGE:-de}" in
  ar|de|el|en|es|fr|it|ja|ko|nl|pl|pt|vi|zh) ;;
  *) echo 'Unsupported LANGUAGE; see model-manifest.json' >&2; exit 1 ;;
esac
python /app/prepare_model.py
export HF_HUB_OFFLINE=1
exec agent-cli server asr --backend transformers --model "${MODEL_DIR:-/data/model}" \
  --default-language "${LANGUAGE:-de}" --device cpu --ttl 0 --preload \
  --host 0.0.0.0 --port 10301 --wyoming-port 10300 \
  --cache-dir /data/hf/hub --max-new-tokens 512
