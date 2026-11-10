# Jarvis para Devin CLI no Windows

Interface pessoal para **Windows 10/11 x64 (Intel/AMD)**: fale um pedido, acrescente seu perfil e memórias, e use o **Devin CLI** para pesquisar ou trabalhar em um projeto.

Versão **0.2.0**. A transcrição roda localmente na CPU com faster-whisper; a leitura usa a voz do Windows. O texto e o contexto são enviados ao Devin.

## Baixar e instalar

1. Abra [Releases](https://github.com/mathugolini/jarvis-devin-windows/releases/latest) e baixe **jarvis-devin-windows.zip**.
2. No Windows, abra as propriedades do ZIP. Se aparecer **Desbloquear**, marque e aplique antes de extrair.
3. Descompacte e abra **COMECE-AQUI.html** para o guia.
4. Execute **Instalar.cmd**. Aguarde a mensagem **Arquivos preparados**.

O instalador usa a pasta do usuário, prepara Python 3.12/3.13, dependências e o Devin CLI se necessário. Baixa aproximadamente 484 MB para o modelo, além dos programas. Usa winget se precisar instalar Python; se ele não estiver disponível, o guia oferece o caminho manual.

Faça o login do Devin quando solicitado. Autorize o microfone no Windows ao usar voz pela primeira vez.

## Usar no PowerShell

Após instalar, abra um **novo PowerShell**:

```powershell
jarvis-devin
```

No menu: **7** escolhe o projeto, **9** abre o Devin para login, **4** abre o perfil, **1** recebe um pedido falado e **3** inicia uma pesquisa personalizada. Saia da sessão do Devin com `/exit`.

Comandos diretos:

```powershell
# Falar
jarvis-devin voz

# Pesquisar por voz
jarvis-devin voz --pesquisa

# Pesquisar por texto
jarvis-devin pesquisar "Pesquise novidades relevantes para meu trabalho e cite as fontes"

# Trabalhar na interface interativa do Devin
jarvis-devin pedir "Analise este projeto e me ajude com a proxima tarefa" --interativo

# Selecionar a pasta atual como projeto
jarvis-devin projeto (Get-Location).Path
```

No modo voz: Enter inicia, outro Enter encerra; confira a transcrição e confirme o envio. Cada gravação tem limite de dois minutos.

Também pode usar **Abrir.cmd** ou o atalho na Área de Trabalho. Se o comando curto ainda não aparecer, o guia mostra o caminho completo.

## Documentação

- [Guia Windows e comandos](GUIA-WINDOWS.md).
- [Validação e limites](VALIDACAO.md).
- [Fontes oficiais e escolhas técnicas](FONTES.md).
- [Exemplos de pedidos](exemplos/PEDIDOS.md).

## Dados, conta e escopo

Programa: `%LOCALAPPDATA%\JarvisDevin`. Perfil, memórias e relatórios: `%LOCALAPPDATA%\JarvisDevinData`. Esses dados ficam fora do repositório e do ZIP. O pacote não inclui credenciais, uma assinatura do Devin ou dados do seu trabalho. O uso do Devin segue seu plano.

Os turnos de voz são individuais. Memórias são explícitas; não há captura contínua da tela, palavra de ativação, acesso automático a e-mails nem pesquisas agendadas. Cada consulta simples inicia uma sessão nova e reutiliza perfil e memórias; para vários passos na mesma conversa, use `--interativo`.

No notebook de trabalho, as permissões e regras da organização continuam valendo. O instalador não altera políticas permanentes de execução do PowerShell.

## Testes

O [workflow Windows](https://github.com/mathugolini/jarvis-devin-windows/actions/workflows/windows.yml) verifica as dependências, o PowerShell, a cópia e reinstalação dos arquivos, os comandos e os adaptadores de áudio em Python 3.12 e 3.13.

```powershell
python -m unittest discover -s tests -v
```

Os testes usam um Devin simulado e áudio simulado. O login no Devin, o microfone físico e a reprodução de voz ainda precisam ser confirmados no notebook real. [Detalhes](VALIDACAO.md).

## Código e licença

Para instalar a partir do código:

```powershell
git clone https://github.com/mathugolini/jarvis-devin-windows.git
cd jarvis-devin-windows
.\Instalar.cmd
```

[MIT](LICENSE). Dependências e serviços externos mantêm suas licenças e termos. Este é um projeto independente, não um produto oficial da Cognition.
