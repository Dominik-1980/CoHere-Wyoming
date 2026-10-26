import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from prepare_model import prepare, verify_model, REQUIRED


class ModelPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.weight = b"test fixture, not a real model"
        for name in REQUIRED:
            (self.folder / name).write_text('{}')
        (self.folder / "config.json").write_text('{"model_type": "cohere_asr"}')
        (self.folder / "model.safetensors").write_bytes(self.weight)
        self.manifest = {
            "repo": "CohereLabs/example", "revision": "a" * 40,
            "model_type": "cohere_asr",
            "weights": {"file": "model.safetensors", "bytes": len(self.weight),
                        "sha256": hashlib.sha256(self.weight).hexdigest()},
        }

    def test_offline_valid_model_never_downloads_or_writes_marker(self):
        download = Mock(side_effect=AssertionError("network forbidden"))
        prepare(self.folder, self.manifest, download=False, downloader=download)
        download.assert_not_called()
        self.assertFalse((self.folder / "cohere-wyoming-source.json").exists())

    def test_hash_mismatch_is_rejected_even_with_expected_size(self):
        (self.folder / "model.safetensors").write_bytes(b"x" * len(self.weight))
        with self.assertRaisesRegex(RuntimeError, "SHA-256"):
            verify_model(self.folder, self.manifest)

    def test_incomplete_download_is_rejected_without_success_marker(self):
        (self.folder / "model.safetensors").write_bytes(b"partial")
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            prepare(self.folder, self.manifest, downloader=Mock())
        self.assertFalse((self.folder / "cohere-wyoming-source.json").exists())

    def test_wrong_architecture_is_rejected(self):
        (self.folder / "config.json").write_text('{"model_type":"whisper"}')
        with self.assertRaisesRegex(RuntimeError, "cohere_asr"):
            verify_model(self.folder, self.manifest)

    def test_quantized_checkpoint_is_rejected(self):
        (self.folder / "config.json").write_text('{"model_type":"cohere_asr","quantization_config":{"bits":4}}')
        with self.assertRaisesRegex(RuntimeError, "unquantized"):
            verify_model(self.folder, self.manifest)

    def test_missing_tokenizer_is_rejected(self):
        (self.folder / "tokenizer.json").unlink()
        with self.assertRaisesRegex(RuntimeError, "Missing model file"):
            verify_model(self.folder, self.manifest)

    def test_download_pinned_source_then_cached_start_without_network(self):
        download = Mock()
        prepare(self.folder, self.manifest, downloader=download)
        args = download.call_args.kwargs
        self.assertEqual(args["repo_id"], self.manifest["repo"])
        self.assertEqual(args["revision"], self.manifest["revision"])
        self.assertNotIn("*.py", args["allow_patterns"])
        download.reset_mock()
        prepare(self.folder, self.manifest, downloader=download)
        download.assert_not_called()

    def test_corrupt_marker_does_not_silently_skip_download(self):
        (self.folder / "cohere-wyoming-source.json").write_text("invalid JSON")
        download = Mock()
        prepare(self.folder, self.manifest, downloader=download)
        download.assert_called_once()
