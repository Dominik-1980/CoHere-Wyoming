"""Narrow, fail-closed adaptations of MIT-licensed agent-cli 0.112.0.

Changes by CoHere-Wyoming: local Cohere architecture detection; remote Python
disabled; accurate Wyoming model/language metadata; no transcript text logging.
Upstream copyright (c) 2025 Bas Nijholt. See licenses/agent-cli-MIT.txt.
"""

from importlib.util import find_spec
from pathlib import Path

LANGUAGES = '["ar", "de", "el", "en", "es", "fr", "it", "ja", "ko", "nl", "pl", "pt", "vi", "zh"]'
NOTICE = "# Modified by CoHere-Wyoming; upstream MIT license: /app/licenses/agent-cli-MIT.txt\n"


def replaced(text, pairs):
    for old, new in pairs:
        if text.count(old) != 1:
            raise RuntimeError(f"Upstream changed: expected exactly one {old!r}")
        text = text.replace(old, new)
    return NOTICE + text


def patch(root):
    backend = root / "server/whisper/backends/transformers.py"
    handler = root / "server/whisper/wyoming_handler.py"
    # Validate every anchor before modifying either upstream file.
    updates = {
        backend: replaced(backend.read_text(), [
            ('_state.is_cohere_asr = requires_remote_code(model_name)',
             '_state.is_cohere_asr = model_config.model_type == "cohere_asr"'),
            ('allow_remote_code = trust_remote_code or requires_remote_code(model_name)',
             'allow_remote_code = False  # Native Transformers architecture only'),
        ]),
        handler: replaced(handler.read_text(), [
            ('description=f"Whisper {status.name}"', 'description="Cohere Transcribe 03-2026 (CPU, unquantized)"'),
            ('name="OpenAI"', 'name="Cohere Labs"'),
            ('url="https://github.com/openai/whisper"', 'url="https://huggingface.co/CohereLabs/cohere-transcribe-03-2026"'),
            ('languages=WHISPER_LANGUAGE_CODES', f'languages={LANGUAGES}'),
            ('name="agent-cli-whisper"', 'name="cohere-transcribe"'),
            ('description="Agent CLI Whisper ASR Server with TTL-based model unloading"',
             'description="CoHere-Wyoming: Cohere Transcribe via Agent CLI"'),
            ('logger.info("Wyoming transcription: %s", result.text[:100] if result.text else "")',
             'logger.debug("Wyoming transcription completed (%d characters)", len(result.text or ""))'),
        ]),
    }
    for path, text in updates.items():
        path.write_text(text)


if __name__ == "__main__":
    spec = find_spec("agent_cli")
    patch(Path(spec.submodule_search_locations[0]))
    print("Agent CLI patched: native Cohere, Wyoming metadata, transcript logging disabled")
