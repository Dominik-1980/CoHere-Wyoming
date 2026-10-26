import asyncio
from importlib.util import find_spec
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from patch_backend import patch, replaced


class PatchSafetyTests(unittest.TestCase):
    def test_changed_upstream_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "Upstream changed"):
            replaced("unexpected new source", [("missing anchor", "replacement")])

    def test_duplicate_anchor_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "exactly one"):
            replaced("anchor anchor", [("anchor", "replacement")])

    def test_failed_patch_does_not_write_either_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            backend = root / "server/whisper/backends/transformers.py"
            handler = root / "server/whisper/wyoming_handler.py"
            backend.parent.mkdir(parents=True)
            original = ('_state.is_cohere_asr = requires_remote_code(model_name)\n'
                        'allow_remote_code = trust_remote_code or requires_remote_code(model_name)')
            backend.write_text(original)
            handler.write_text("unexpected handler source")
            with self.assertRaises(RuntimeError):
                patch(root)
            self.assertEqual(backend.read_text(), original)
            self.assertEqual(handler.read_text(), "unexpected handler source")


@unittest.skipUnless(find_spec("agent_cli"), "Runs against installed image runtime in CI")
class InstalledRuntimeTests(unittest.TestCase):
    def test_native_transformers_import_works_as_container_user(self):
        from transformers import AutoConfig, AutoModelForSpeechSeq2Seq, AutoProcessor
        self.assertEqual(AutoConfig.for_model("cohere_asr").model_type, "cohere_asr")
        self.assertIsNotNone(AutoModelForSpeechSeq2Seq)
        self.assertIsNotNone(AutoProcessor)

    def test_wyoming_describe_reports_cohere_and_model_languages(self):
        from agent_cli.server.whisper.wyoming_handler import WyomingWhisperHandler
        from wyoming.info import Info
        import json

        handler = object.__new__(WyomingWhisperHandler)
        handler._registry = SimpleNamespace(list_status=lambda: [SimpleNamespace(name="/data/model")])
        events = []

        async def capture(event):
            events.append(event)
        handler.write_event = capture
        asyncio.run(handler._handle_describe())
        info = Info.from_event(events[0])
        self.assertEqual(info.asr[0].name, "cohere-transcribe")
        model = info.asr[0].models[0]
        self.assertEqual(model.attribution.name, "Cohere Labs")
        manifest = json.loads(Path("model-manifest.json").read_text())
        self.assertEqual(model.languages, manifest["languages"])

    def test_installed_backend_disables_remote_code_and_detects_architecture(self):
        from importlib.util import find_spec
        path = Path(find_spec("agent_cli").submodule_search_locations[0]) / "server/whisper/backends/transformers.py"
        source = path.read_text()
        self.assertIn("allow_remote_code = False", source)
        self.assertIn('_state.is_cohere_asr = model_config.model_type == "cohere_asr"', source)
