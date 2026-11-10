# Fontes da adaptação Windows

Consultadas em 10/11/2026.

- [Devin CLI — instalação oficial no Windows](https://docs.devin.ai/cli): confirma o instalador PowerShell e o uso no Windows Terminal/PowerShell.
- [Devin CLI — comandos](https://docs.devin.ai/cli/reference/commands): --prompt-file, --print e sessão interativa.
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper): transcrição local com CTranslate2, execução em CPU/int8 e PyAV para decodificação de áudio.
- [sounddevice — instalação](https://python-sounddevice.readthedocs.io/en/latest/installation.html): a distribuição pip inclui PortAudio para Windows.
- [sounddevice — RawInputStream](https://python-sounddevice.readthedocs.io/en/latest/api/raw-streams.html): captura com buffers PCM.
- [Microsoft — SpeechSynthesizer](https://learn.microsoft.com/en-us/dotnet/api/system.speech.synthesis.speechsynthesizer): síntese com as vozes instaladas no Windows.
- [Microsoft — políticas de execução do PowerShell](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies): escopo da sessão, RemoteSigned e precedência de políticas da organização.
- [Python para Windows](https://www.python.org/downloads/windows/).
- [Microsoft — Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist): dependência possível de bibliotecas nativas no Windows.
- [Modelo faster-whisper-small](https://huggingface.co/Systran/faster-whisper-small/tree/536b0662742c02347bc0e980a01041f333bce120): revisão fixa usada pelo programa.

O arquivo principal do modelo é verificado pelo SHA-256 3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671. Ele e as dependências são baixados na instalação; não fazem parte do ZIP do projeto.

Para estudar a arquitetura de assistentes pessoais:

- [Building AI Voice Agents for Production — DeepLearning.AI e LiveKit](https://www.deeplearning.ai/courses/building-ai-voice-agents-for-production).
- [Long-Term Agentic Memory With LangGraph](https://www.deeplearning.ai/courses/long-term-agentic-memory-with-langgraph).
- [Dodaios, anteriormente Personal Jarvis](https://github.com/Dodaios/Dodaios).
