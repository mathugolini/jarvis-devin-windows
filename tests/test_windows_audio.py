import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import windows_audio as audio


class AudioTests(unittest.TestCase):
    def test_model_download_is_pinned_and_verified(self):
        def snapshot(**kwargs):
            self.assertEqual(kwargs["revision"], audio.MODEL_REVISION)
            folder = Path(kwargs["local_dir"])
            for name in audio.MODEL_FILES:
                (folder / name).write_bytes(b"abc")
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder) / "model"
            with patch.dict(sys.modules, {"huggingface_hub": types.SimpleNamespace(snapshot_download=snapshot)}), \
                    patch.object(audio, "MODEL_SIZE", 3), patch.object(audio, "MODEL_SHA256", hashlib.sha256(b"abc").hexdigest()), \
                    contextlib.redirect_stdout(io.StringIO()):
                audio.prepare_model(model)
                self.assertTrue(audio.model_ready(model))
                (model / "tokenizer.json").unlink()
                self.assertFalse(audio.model_ready(model))

    def test_corrupted_model_is_not_marked_ready(self):
        def snapshot(**kwargs):
            for name in audio.MODEL_FILES:
                (Path(kwargs["local_dir"]) / name).write_bytes(b"bad")
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder) / "model"
            with patch.dict(sys.modules, {"huggingface_hub": types.SimpleNamespace(snapshot_download=snapshot)}), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(RuntimeError):
                    audio.prepare_model(model)
            self.assertFalse((model / "jarvis-model.json").exists())

    def test_audio_capture_produces_valid_mono_wav(self):
        class Stream:
            def __init__(self, **kwargs):
                self.callback = kwargs["callback"]
            def __enter__(self):
                self.callback(b"\x01\x00" * 8000, 8000, None, None)
                return self
            def __exit__(self, *args):
                pass
        fake = types.SimpleNamespace(RawInputStream=Stream, query_devices=lambda *args: {"default_samplerate": 16000}, PortAudioError=OSError)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "voice.wav"
            with patch.dict(sys.modules, {"sounddevice": fake}), patch.object(audio, "wait_for_stop"), contextlib.redirect_stdout(io.StringIO()):
                audio.record_wav(target)
            with wave.open(str(target), "rb") as result:
                self.assertEqual(result.getnchannels(), 1)
                self.assertEqual(result.getsampwidth(), 2)
                self.assertEqual(result.getframerate(), 16000)
                self.assertEqual(result.getnframes(), 8000)

    def test_transcription_is_local_cpu_and_consumes_segments(self):
        calls = {}
        class Engine:
            def __init__(self, *args, **kwargs):
                calls.update(kwargs)
            def transcribe(self, *args, **kwargs):
                return iter([types.SimpleNamespace(text=" Pesquise Java. ")]), None
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "voice.wav"
            target.write_bytes(b"test")
            with patch.dict(sys.modules, {"faster_whisper": types.SimpleNamespace(WhisperModel=Engine)}), patch.object(audio, "model_ready", return_value=True):
                self.assertEqual(audio.transcribe_audio(target, Path(folder), "pt"), "Pesquise Java.")
        self.assertEqual(calls["device"], "cpu")
        self.assertEqual(calls["compute_type"], "int8")
        self.assertTrue(calls["local_files_only"])

    def test_voice_text_is_passed_as_file_not_powershell_code(self):
        with patch.object(audio.sys, "platform", "win32"), patch.object(audio, "powershell_path", return_value="powershell.exe"), \
                patch.object(audio.subprocess, "run") as run:
            audio.speak_text("Texto com $(comando) e caracteres especiais.")
        arguments = run.call_args.args[0]
        self.assertIn("-TextPath", arguments)
        self.assertNotIn("-Command", arguments)
        self.assertFalse(any("$(comando)" in arg for arg in arguments))


if __name__ == "__main__":
    unittest.main()
