"""Tests on real Windows/Git Bash; microphone, model and Devin stay simulated."""
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest


@unittest.skipUnless(sys.platform == "win32", "Requires Git for Windows")
class GitBashTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="jarvis-bash-")
        cls.root = Path(cls.temp.name)
        cls.package = Path(__file__).resolve().parents[1]
        git = shutil.which("git.exe")
        if not git:
            raise RuntimeError("Git for Windows must be present in Windows CI")
        git_root = Path(git).resolve().parents[1]
        cls.bash = git_root / "bin/bash.exe"
        if not cls.bash.is_file():
            raise RuntimeError(f"Git Bash missing: {cls.bash}")
        cls.local = cls.root / "local app data"
        cls.installed = cls.local / "JarvisDevin"
        cls.state = cls.root / "dados com espaços"
        cls.project = cls.root / "projeto com espaços"
        cls.project.mkdir()
        cls.environment = dict(os.environ, PYTHONUTF8="1", LOCALAPPDATA=str(cls.local),
                               JARVIS_TEST_BIN=str(cls.installed / "bin"))
        cls.environment["PATH"] = (str(git_root / "usr/bin") + os.pathsep
                                    + str(git_root / "mingw64/bin") + os.pathsep + os.environ["PATH"])
        cls.environment["TERM"] = "xterm-256color"
        # Exercise the user's Bash installer entry point; never change PATH/login.
        command = [str(cls.bash), "--noprofile", "--norc", str(cls.package / "Instalar.sh"),
                   "-OnlyFiles", "-SkipDesktop", "-SkipPath", "-InstallRoot", str(cls.installed),
                   "-DataRoot", str(cls.state), "-PythonExe", sys.executable]
        result = subprocess.run(command, env=cls.environment, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=60)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_bash(self, body, **extra):
        script = self.root / "request.sh"
        script.write_text('set -euo pipefail\nexport PATH="$(cygpath -u "$JARVIS_TEST_BIN"):$PATH"\n'
                          + body + "\n", encoding="utf-8")
        result = subprocess.run([str(self.bash), "--noprofile", "--norc", str(script)],
                                env=dict(self.environment, **extra), cwd=self.project,
                                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_literal_request_and_posix_project_path(self):
        request = '/api/test https://example.org/a:b "aspas" $(touch NUNCA_CRIAR) & % ! çã'
        output = self.run_bash('jarvis-devin projeto "$PWD"\n'
                               'jarvis-devin pesquisar "$JARVIS_TEST_REQUEST" --simular --sem-voz',
                               JARVIS_TEST_REQUEST=request)
        self.assertIn(request, output)
        config = json.loads((self.state / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(Path(config["workspace"]).resolve(), self.project.resolve())
        self.assertFalse((self.project / "NUNCA_CRIAR").exists())

    def test_project_option_and_open_script(self):
        output = self.run_bash('jarvis-devin pesquisar "teste opcao" --projeto "$PWD" --simular\n'
                               'bash "$JARVIS_TEST_OPEN" pesquisar "teste abrir" --projeto="$PWD" --simular',
                               JARVIS_TEST_OPEN=str(self.package / "Abrir.sh"))
        self.assertIn("teste opcao", output)
        self.assertIn("teste abrir", output)
        self.assertIn(str(self.project.resolve()), output)

    def test_conversion_override_does_not_leak_to_children(self):
        audio_module = self.installed / "app/windows_audio.py"
        original = audio_module.read_text(encoding="utf-8")
        snapshot = self.root / "child-environment.json"
        child = ("import json,os,pathlib; pathlib.Path(os.environ['JARVIS_TEST_SNAPSHOT']).write_text("
                 "json.dumps({k:os.environ.get(k) for k in "
                 "['MSYS2_ARG_CONV_EXCL','JARVIS_MSYS_CONV_PRESENT','JARVIS_MSYS_CONV_ORIGINAL']}))")
        audio_module.write_text(original + "\nimport atexit\n"
                                + f"atexit.register(lambda: subprocess.run([sys.executable, '-c', {child!r}], check=True))\n",
                                encoding="utf-8")
        try:
            for setting in (None, "/preserve-user-setting/"):
                self.environment.pop("MSYS2_ARG_CONV_EXCL", None)
                if setting is not None:
                    self.environment["MSYS2_ARG_CONV_EXCL"] = setting
                self.run_bash('jarvis-devin pesquisar teste --simular', JARVIS_TEST_SNAPSHOT=str(snapshot))
                values = json.loads(snapshot.read_text(encoding="utf-8"))
                self.assertEqual(values, {"MSYS2_ARG_CONV_EXCL": setting,
                                         "JARVIS_MSYS_CONV_PRESENT": None, "JARVIS_MSYS_CONV_ORIGINAL": None})
        finally:
            self.environment.pop("MSYS2_ARG_CONV_EXCL", None)
            audio_module.write_text(original, encoding="utf-8")

    def test_interactive_voice_enter_through_winpty(self):
        from winpty import PtyProcess
        audio_module = self.installed / "app/windows_audio.py"
        original = audio_module.read_text(encoding="utf-8")
        # Replace only capture/model in a disposable installation. Keep the real
        # msvcrt reader, launcher, winpty, app prompts and transcript confirmation.
        audio_module.write_text(original + '''
def model_ready(folder):
    return True

def record_wav(target, device=None):
    print("TEST_RECORDING_READY", flush=True)
    started = time.monotonic()
    wait_for_stop(seconds=12)
    if time.monotonic() - started > 10:
        raise RuntimeError("Enter did not reach the Windows console")
    with wave.open(str(target), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(16000)
        stream.writeframes(b"\\0\\0" * 1600)
    print("TEST_RECORDING_STOPPED", flush=True)

def transcribe_audio(audio, model, language):
    return "PEDIDO_FALADO_TESTE"
''', encoding="utf-8")
        script = self.root / "interactive.sh"
        script.write_text('set -euo pipefail\nexport PATH="$(cygpath -u "$JARVIS_TEST_BIN"):$PATH"\n'
                          'command -v winpty\n'
                          '[[ -t 0 && -t 1 ]] || exit 72\n'
                          'jarvis-devin voz --pesquisa --simular --sem-voz\n'
                          'echo TEST_INTERACTIVE_FINISHED\n', encoding="utf-8")
        process = None
        reader = None
        chunks = queue.Queue()
        received = ""
        def read_output():
            try:
                while True:
                    chunks.put(process.read(4096))
            except (EOFError, OSError):
                pass

        def expect(token):
            nonlocal received
            deadline = time.monotonic() + 30
            while token not in received and time.monotonic() < deadline:
                try:
                    received += chunks.get(timeout=0.25)
                except queue.Empty:
                    pass
            self.assertIn(token, received, received)

        try:
            process = PtyProcess.spawn([str(self.bash), "--noprofile", "--norc", str(script)],
                                       cwd=str(self.project), env=self.environment, dimensions=(35, 160))
            reader = threading.Thread(target=read_output, daemon=True)
            reader.start()
            expect("Pressione Enter")
            process.write("\r")
            expect("TEST_RECORDING_READY")
            process.write("\r")
            expect("TEST_RECORDING_STOPPED")
            expect("cancelar")
            process.write("\r")
            expect("PESQUISA PERSONALIZADA")
            expect("TEST_INTERACTIVE_FINISHED")
            self.assertIn("PEDIDO_FALADO_TESTE", received)
        finally:
            audio_module.write_text(original, encoding="utf-8")
            if process is not None:
                # pywinpty's isalive() mutates closed; explicitly close sockets.
                process.closed = False
                process.close(force=True)
            if reader is not None:
                reader.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
