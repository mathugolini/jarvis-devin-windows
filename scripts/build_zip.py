"""Gera um ZIP de distribuicao com lista explicita de arquivos, sem dados locais."""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "README.md", "GUIA-WINDOWS.md", "GUIA-GIT-BASH.md", "COMECE-AQUI.html", "VALIDACAO.md", "FONTES.md", "LICENSE",
    "requirements.txt", "Instalar.cmd", "Abrir.cmd", "app/jarvis.py", "app/windows_audio.py",
    "Instalar.sh", "Abrir.sh", "scripts/jarvis-devin.sh",
    "scripts/install.ps1", "scripts/speak.ps1", "scripts/build_zip.py",
    "tests/test_jarvis.py", "tests/test_windows_audio.py", "tests/test_git_bash.py", "exemplos/PEDIDOS.md",
)


def build() -> Path:
    target = ROOT / "dist/jarvis-devin-windows.zip"
    target.parent.mkdir(exist_ok=True)
    prefix = "jarvis-devin-windows/"
    manifest = []
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name in FILES:
            content = (ROOT / name).read_bytes()
            if name.endswith(".cmd"):
                content = content.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            package.writestr(prefix + name, content)
            manifest.append(hashlib.sha256(content).hexdigest() + "  " + name)
        package.writestr(prefix + "MANIFEST.sha256", "\n".join(manifest) + "\n")
    with zipfile.ZipFile(target) as package:
        assert package.testzip() is None
        for line in manifest:
            digest, name = line.split("  ", 1)
            assert hashlib.sha256(package.read(prefix + name)).hexdigest() == digest
    print(f"ZIP verificado: {target} ({target.stat().st_size} bytes)")
    return target


if __name__ == "__main__":
    build()
