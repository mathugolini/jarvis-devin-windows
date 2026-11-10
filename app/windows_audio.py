"""Audio local para Windows; dependencias pesadas carregadas apenas ao usar voz."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import wave

MODEL_REPO = "Systran/faster-whisper-small"
MODEL_REVISION = "536b0662742c02347bc0e980a01041f333bce120"
MODEL_SIZE = 483546902
MODEL_SHA256 = "3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671"
MODEL_FILES = ("config.json", "model.bin", "tokenizer.json", "vocabulary.txt")


def model_ready(folder: Path) -> bool:
    try:
        marker = json.loads((folder / "jarvis-model.json").read_text(encoding="utf-8"))
        return (marker.get("revision") == MODEL_REVISION
                and all((folder / name).is_file() for name in MODEL_FILES)
                and (folder / "model.bin").stat().st_size == MODEL_SIZE)
    except (OSError, ValueError):
        return False


def prepare_model(folder: Path) -> None:
    if model_ready(folder):
        print("Modelo local pronto.")
        return
    try:
        from huggingface_hub import snapshot_download
    except ImportError as error:
        raise RuntimeError("Dependencias de voz ausentes. Execute Instalar.cmd.") from error
    folder.mkdir(parents=True, exist_ok=True)
    print("Baixando o modelo de portugues (aproximadamente 484 MB)...", flush=True)
    snapshot_download(repo_id=MODEL_REPO, revision=MODEL_REVISION,
                      allow_patterns=list(MODEL_FILES), local_dir=str(folder))
    if not all((folder / name).is_file() for name in MODEL_FILES):
        raise RuntimeError("Download incompleto. Execute baixar-modelo novamente.")
    digest = hashlib.sha256()
    with (folder / "model.bin").open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if (folder / "model.bin").stat().st_size != MODEL_SIZE or digest.hexdigest() != MODEL_SHA256:
        raise RuntimeError("Modelo recebido nao passou na verificacao de integridade.")
    marker = folder / "jarvis-model.json"
    marker.write_text(json.dumps({"repository": MODEL_REPO, "revision": MODEL_REVISION,
                                 "sha256": MODEL_SHA256}, indent=2), encoding="utf-8")
    print("Modelo baixado e verificado. A transcricao pode funcionar sem internet.")


def transcribe_audio(audio: Path, model: Path, language: str) -> str:
    if not audio.is_file():
        raise ValueError(f"Arquivo de audio nao encontrado: {audio}")
    if not model_ready(model):
        raise ValueError("Modelo ausente ou incompleto. Execute jarvis-devin baixar-modelo.")
    try:
        from faster_whisper import WhisperModel
    except ImportError as error:
        raise RuntimeError("Transcricao nao instalada. Execute Instalar.cmd.") from error
    engine = WhisperModel(str(model), device="cpu", compute_type="int8", local_files_only=True)
    segments, _ = engine.transcribe(str(audio), language=language, beam_size=5, vad_filter=True)
    text = " ".join(segment.text.strip() for segment in segments).strip()
    if not text:
        raise ValueError("Nao reconheci fala. Tente novamente ou use o modo texto.")
    return text


def wait_for_stop(seconds: float = 120) -> None:
    """Leitura de teclado no console Windows sem deixar threads bloqueadas em input()."""
    import msvcrt
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if msvcrt.kbhit():
            key = msvcrt.getwch()
            if key in ("\r", "\n"):
                return
            if key == "\x03":
                raise KeyboardInterrupt
        time.sleep(0.03)


def record_wav(target: Path, device: int | str | None = None) -> None:
    try:
        import sounddevice as sd
    except ImportError as error:
        raise RuntimeError("Captura de voz nao instalada. Execute Instalar.cmd.") from error
    if device in ("", "default"):
        device = None
    if isinstance(device, str) and device.isdecimal():
        device = int(device)
    chunks: list[bytes] = []
    warnings: list[str] = []

    def callback(data, frames, timing, status):
        if status and not warnings:
            warnings.append(str(status))
        chunks.append(bytes(data))

    try:
        info = sd.query_devices(device, "input")
        rate = int(info["default_samplerate"])
        with sd.RawInputStream(device=device, samplerate=rate, channels=1, dtype="int16", callback=callback):
            print("Gravando. Pressione Enter para encerrar (limite de 2 minutos).", flush=True)
            wait_for_stop()
    except (OSError, sd.PortAudioError) as error:
        raise RuntimeError("Microfone indisponivel. Confira o dispositivo de entrada e as permissoes "
                           "de microfone para aplicativos da area de trabalho no Windows. " + str(error)) from error
    if warnings:
        raise RuntimeError("A captura teve falhas e foi descartada: " + warnings[0] + ". Tente novamente.")
    data = b"".join(chunks)
    if len(data) < rate // 2:
        raise ValueError("Gravacao muito curta. Fale uma frase e tente novamente.")
    with wave.open(str(target), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(data)


def list_microphones() -> None:
    try:
        import sounddevice as sd
    except ImportError as error:
        raise RuntimeError("Execute Instalar.cmd para preparar o audio.") from error
    for index, device in enumerate(sd.query_devices()):
        if device["max_input_channels"] > 0:
            print(f"{index}: {device['name']}")
    print("Use o indice em 'microphone' no config.json, ou null para o padrao do Windows.")


def powershell_path() -> str:
    binary = shutil.which("powershell.exe")
    if binary:
        return binary
    path = Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    if path.is_file():
        return str(path)
    raise RuntimeError("Windows PowerShell nao encontrado.")


def speak_text(text: str, voice: str = "") -> None:
    if sys.platform != "win32":
        return
    script = Path(__file__).resolve().parent.parent / "scripts/speak.ps1"
    with tempfile.TemporaryDirectory(prefix="jarvis-resumo-") as folder:
        text_file = Path(folder) / "resumo.txt"
        text_file.write_text(text, encoding="utf-8")
        subprocess.run([powershell_path(), "-NoProfile", "-ExecutionPolicy", "RemoteSigned", "-File",
                        str(script), "-TextPath", str(text_file), "-Voice", voice],
                       check=True, timeout=120, capture_output=True)
