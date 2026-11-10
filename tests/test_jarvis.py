import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

SPEC = importlib.util.spec_from_file_location("jarvis", Path(__file__).resolve().parents[1] / "app/jarvis.py")
jarvis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(jarvis)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="jarvis-tests-")
        self.root = Path(self.temp.name)
        self.app = jarvis.Jarvis(self.root / "state")
        self.app.init()
        self.project_a = self.root / "projeto A"
        self.project_b = self.root / "projeto B"
        self.project_a.mkdir()
        self.project_b.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def test_project_memory_does_not_cross_projects(self):
        self.app.remember("MEMORIA_PROJETO_A", "project", self.project_a)
        self.app.remember("MEMORIA_GLOBAL", "global", self.project_a)
        prompt = self.app.prompt("pesquisar", True, self.project_b)
        self.assertIn("MEMORIA_GLOBAL", prompt)
        self.assertNotIn("MEMORIA_PROJETO_A", prompt)

    def test_reinstallation_preserves_user_profile_and_config(self):
        self.app.profile_path.write_text("Meu perfil real", encoding="utf-8")
        config = self.app.init()
        config["microphone"] = "7"
        self.app.save_config(config)
        self.assertEqual(self.app.init()["microphone"], "7")
        self.assertEqual(self.app.profile_path.read_text(), "Meu perfil real")

    def test_forget_removes_only_requested_memory(self):
        first = self.app.remember("A", "global", self.project_a)
        second = self.app.remember("B", "global", self.project_a)
        self.assertTrue(self.app.forget(first))
        self.assertEqual([entry["id"] for entry in self.app.memories()], [second])
        self.assertFalse(self.app.forget("unknown"))

    def test_private_files_and_bounded_memory(self):
        for index in range(50):
            self.app.remember(f"memória {index} " + "x" * 700, "global", self.project_a)
        prompt = self.app.prompt("pedido", False, self.project_a)
        memory_block = prompt.split("<memorias_locais>\n")[1].split("\n</memorias_locais>")[0]
        self.assertLessEqual(len(memory_block), 18000)
        self.assertLessEqual(len(json.loads(memory_block)), 40)
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(self.app.memory_path.stat().st_mode), 0o600)

    def make_fake_devin(self, exit_code=0, sleep=0):
        folder = self.root / "bin"
        folder.mkdir(exist_ok=True)
        executable = folder / "devin_fake.py"
        executable.write_text("#!/usr/bin/env python3\nimport json,pathlib,sys,time\n"
            "if '--help' in sys.argv:\n print('--prompt-file --print --permission-mode'); sys.exit(0)\n"
            "p=pathlib.Path(sys.argv[sys.argv.index('--prompt-file')+1])\n"
            f"pathlib.Path({str(self.root / 'received.json')!r}).write_text(json.dumps({{'args':sys.argv[1:],'prompt':p.read_text(),'cwd':str(pathlib.Path.cwd()),'file':str(p)}}))\n"
            f"time.sleep({sleep})\nprint('RESUMO_PARA_VOZ: Teste concluído.\\nFIM_RESUMO\\nResposta simulada, sem chamada a modelos.')\n"
            f"sys.exit({exit_code})\n", encoding="utf-8")
        executable.chmod(0o700)
        return [sys.executable, str(executable)]

    def test_real_process_bridge_keeps_shell_characters_literal(self):
        folder = self.make_fake_devin()
        marker = self.root / "NAO_DEVE_EXISTIR"
        request = f"pesquise $(touch {marker}) `touch {marker}`; echo teste"
        with patch.object(jarvis, "devin_command", return_value=folder), contextlib.redirect_stdout(io.StringIO()):
            code = self.app.run_devin(request, True, workspace_override=str(self.project_a), silent=True)
        self.assertEqual(code, 0)
        self.assertFalse(marker.exists())
        received = json.loads((self.root / "received.json").read_text())
        self.assertIn(request, received["prompt"])
        self.assertEqual(received["cwd"], str(self.project_a.resolve()))
        self.assertIn("--print", received["args"])
        self.assertEqual(received["args"][1], "normal")
        self.assertFalse(Path(received["file"]).exists())
        self.assertTrue(list((self.app.home / "relatorios").glob("*/resposta.txt")))

    def test_failed_devin_is_not_reported_as_success(self):
        folder = self.make_fake_devin(exit_code=7)
        with patch.object(jarvis, "devin_command", return_value=folder), patch.object(self.app, "speak") as speak, contextlib.redirect_stdout(io.StringIO()):
            code = self.app.run_devin("teste", workspace_override=str(self.project_a))
        self.assertEqual(code, 7)
        speak.assert_not_called()
        saved = next((self.app.home / "relatorios").glob("*/consulta.json"))
        self.assertEqual(json.loads(saved.read_text())["exit_code"], 7)

    def test_timeout_terminates_process_without_success_report(self):
        folder = self.make_fake_devin(sleep=10)
        config = self.app.init()
        config["timeout_seconds"] = 1
        self.app.save_config(config)
        with patch.object(jarvis, "devin_command", return_value=folder), contextlib.redirect_stdout(io.StringIO()):
            code = self.app.run_devin("teste", workspace_override=str(self.project_a), silent=True)
        self.assertEqual(code, 130)
        self.assertFalse((self.app.home / "relatorios").exists())

    def test_dry_run_makes_no_devin_call(self):
        with patch.object(jarvis, "devin_command", side_effect=AssertionError("Não deveria executar")), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(self.app.run_devin("teste", True, dry_run=True), 0)

    def test_spoken_summary_does_not_read_arbitrary_logs(self):
        self.assertIn("terminal", jarvis.spoken_summary("Erro: token ou log desconhecido"))
        self.assertEqual(jarvis.spoken_summary("RESUMO_PARA_VOZ: Pronto.\nFIM_RESUMO\n```codigo```"), "Pronto.")

    @unittest.skipUnless(sys.platform == "win32", "Instalador especifico para Windows")
    def test_installer_and_reinstallation_in_isolated_directory(self):
        package = Path(__file__).resolve().parents[1]
        environment = dict(os.environ, PYTHONUTF8="1")
        installed_state = self.root / "installed state"
        installed_app = self.root / "installed app"
        command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "RemoteSigned", "-File",
            str(package / "scripts/install.ps1"), "-OnlyFiles", "-SkipDesktop", "-SkipPath",
            "-InstallRoot", str(installed_app), "-DataRoot", str(installed_state), "-PythonExe", sys.executable]
        subprocess.run(command, env=environment, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        profile = installed_state / "perfil.md"
        profile.write_text("Perfil preservado", encoding="utf-8")
        subprocess.run(command, env=environment, check=True, capture_output=True, text=True, timeout=60)
        self.assertEqual(profile.read_text(), "Perfil preservado")
        launcher = installed_app / "bin/jarvis-devin.cmd"
        result = subprocess.run([str(launcher), "pesquisar", "teste", "--simular"],
            env=environment, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
        self.assertIn("Perfil preservado", result.stdout)
        self.assertIn("PESQUISA PERSONALIZADA", result.stdout)


if __name__ == "__main__":
    unittest.main()
