# Validação da versão Windows 0.2.0

O projeto possui testes automatizados para Windows x64 em Python 3.12 e 3.13. O resultado de cada execução pode ser consultado em [Actions](https://github.com/mathugolini/jarvis-devin-windows/actions/workflows/windows.yml).

## O que os testes verificam

- Sintaxe dos scripts no Windows PowerShell 5.1.
- Instalação e importação das dependências nativas de áudio no Windows.
- Cópia e reinstalação dos arquivos em pasta isolada, incluindo caminhos com espaços.
- Preservação do perfil e configuração.
- Inicialização do comando jarvis-devin.cmd e simulação de pesquisa.
- Perfil, memórias globais, isolamento por projeto e exclusão por identificador.
- Encaminhamento de um pedido para um processo que simula o Devin, com texto passado por arquivo.
- Tratamento literal de caracteres de shell no pedido, falhas e interrupção por tempo limite.
- Download fixado por revisão e verificação do modelo, usando arquivos pequenos simulados.
- Geração de WAV mono PCM de 16 bits, usando captura simulada.
- Configuração da transcrição local em CPU/int8, sem downloads implícitos durante uma consulta.
- Encaminhamento do resumo para o PowerShell por arquivo, sem inseri-lo em código de comandos.
- Construção do ZIP com manifesto de integridade.

O teste do instalador usa os parâmetros OnlyFiles, SkipDesktop e SkipPath com pastas temporárias. Assim, verifica os arquivos e o comando sem modificar o PATH, a Área de Trabalho ou instalar uma conta do Devin durante o teste.

## O que ainda exige o notebook real

O microfone físico, os drivers, a voz instalada e a conta autenticada do Devin não são simulados como se fossem resultados reais. Precisam ser confirmados no computador de uso. Os testes automatizados não medem reconhecimento da sua voz, latência, consumo ou produtividade.

A instalação completa pode depender da conexão, do winget/Python disponível e das permissões da empresa. O código foi separado da versão macOS: captura, transcrição, síntese de voz, caminhos, encerramento de processos e instalador foram adaptados para Windows.

## Repetir

```powershell
python -m unittest discover -s tests -v
python scripts/build_zip.py
```

Para testar apenas a instalação de arquivos em uma pasta controlada:

```powershell
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File .\scripts\install.ps1 -OnlyFiles -SkipDesktop -SkipPath -InstallRoot "$env:TEMP\JarvisTesteApp" -DataRoot "$env:TEMP\JarvisTesteDados" -PythonExe "CAMINHO_DO_PYTHON_EXE"
```

O exemplo exige substituir CAMINHO_DO_PYTHON_EXE pelo caminho real de um Python 3.12 ou 3.13 x64. Para uso diário, prefira Instalar.cmd.
