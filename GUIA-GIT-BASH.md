# Jarvis direto no Git Bash

Versão 0.3.0 · Windows 10/11 x64 · Git for Windows

Você instala e usa pelo **Git Bash**. O comando é **jarvis-devin**, inclusive para voz, pesquisa com seu perfil e abertura do Devin interativo. Não é necessário entrar em uma sessão do PowerShell para usar o Jarvis.

## 1. Instalar ou atualizar

Baixe **jarvis-devin-windows.zip** em [Releases](https://github.com/mathugolini/jarvis-devin-windows/releases/latest). Nas propriedades do ZIP, marque **Desbloquear**, se aparecer, antes de extrair. Abra o Git Bash na pasta extraída que contém Instalar.sh:

```bash
bash Instalar.sh
```

O instalador prepara Python, dependências, modelo de voz e Devin. Pode pedir seu login. Espere **Arquivos preparados**; o modelo ocupa aproximadamente 484 MB. O script usa o instalador Windows internamente, sem você trocar de terminal. As regras de instalação da sua empresa continuam valendo.

Se já tinha a versão 0.2.0, execute o instalador do **novo ZIP**. Ele acrescenta o comando do Bash e preserva perfil e memórias.

## 2. Ativar o comando nesta aba

Após a instalação padrão, execute no Git Bash:

```bash
export PATH="$(cygpath -u "$LOCALAPPDATA")/JarvisDevin/bin:$PATH"
jarvis-devin
```

O instalador também adiciona a pasta ao PATH do usuário do Windows. Novos terminais que herdarem esse PATH já terão o comando. O export acima resolve na aba atual, sem editar seu .bashrc. Alternativamente, use **bash Abrir.sh** na pasta extraída.

## 3. Selecionar o projeto e falar

Abra o Git Bash na pasta do projeto e execute:

```bash
jarvis-devin projeto "$PWD"
jarvis-devin voz
```

Enter começa a gravação; outro Enter para. Confira a transcrição e pressione Enter para enviar. Digite uma correção para substituir o texto ou **cancelar** para descartar. O limite é de dois minutos por gravação.

## 4. Pesquisa e trabalho diário

```bash
# Abra seu perfil no Bloco de Notas e salve suas preferências.
jarvis-devin perfil

# Salve uma preferência para todos os projetos.
jarvis-devin lembrar 'Prefiro respostas em portugues com exemplos e fontes' --global

# Pesquise por voz usando seu perfil e suas memórias.
jarvis-devin voz --pesquisa

# Pesquise por texto.
jarvis-devin pesquisar 'Pesquise novidades relevantes para o meu trabalho e cite as fontes'

# Fale o pedido inicial e continue na interface do Devin.
jarvis-devin voz --interativo

# Confira o ambiente.
jarvis-devin diagnostico

# Veja o contexto sem chamar o Devin.
jarvis-devin pesquisar 'Teste de contexto' --simular
```

Para uma consulta em outra pasta sem mudar o projeto salvo:

```bash
jarvis-devin pedir 'Explique este projeto' --projeto '/c/Projetos/Meu Projeto' --interativo
```

Use aspas em caminhos com espaços. Pedidos de texto entre aspas simples são literais no Bash, inclusive quando contêm $ ou crases. As opções de caminho aceitam a notação do Git Bash; o launcher converte esses caminhos para o Windows. No menu, ao digitar manualmente uma pasta na opção 7, use o caminho Windows, por exemplo **C:\Projetos\Meu Projeto**.

Para sair da interface do Devin, digite **/exit**. O login, as ferramentas e o uso do Devin dependem da sua conta. O perfil e as memórias são reutilizados; as consultas simples abrem sessões novas. O modo interativo permite continuar a mesma conversa.

## Como o terminal e a voz funcionam

O Git Bash costuma usar mintty, que precisa de uma ponte para programas que leem o console nativo do Windows. O launcher usa automaticamente o **winpty** incluído no Git for Windows em sessões interativas. Você continua no Git Bash e usa o mesmo comando. A captura usa o microfone do Windows; a transcrição é local; o texto reconhecido e o contexto são enviados ao Devin após sua confirmação.

Se aparecer um erro sobre winpty, confira **command -v winpty** e atualize/repare o Git for Windows pelo site oficial. Também é possível abrir o Git Bash dentro do Windows Terminal. WSL, GitHub Codespaces e Bash Linux não são os ambientes deste pacote.

## Se algo não abrir

- **command not found:** repita o export da etapa 2 ou execute **bash Abrir.sh**.
- **Modelo incompleto:** execute **jarvis-devin baixar-modelo**.
- **Devin sem login:** use **jarvis-devin pedir 'Responda pronto' --interativo** e conclua o acesso.
- **Microfone ou áudio:** veja as configurações e soluções no [guia Windows](GUIA-WINDOWS.md).

Programa: **%LOCALAPPDATA%\JarvisDevin**. Perfil, memórias e relatórios: **%LOCALAPPDATA%\JarvisDevinData**. Esses arquivos locais ficam fora do repositório público.

Os testes de Windows cobrem a instalação via Bash, caminhos com espaços, pedidos literais e o Enter da gravação através do winpty, com áudio e transcrição simulados. Microfone físico, qualidade do reconhecimento e login real precisam ser conferidos no seu notebook. Consulte [Validação](VALIDACAO.md).
