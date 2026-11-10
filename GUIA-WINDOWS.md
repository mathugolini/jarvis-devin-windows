# Jarvis no Windows: do ZIP ao primeiro pedido

Versão 0.3.0 · Windows 10/11 x64 · 10/11/2026

**Vai usar o Git Bash?** Siga [GUIA-GIT-BASH.md](GUIA-GIT-BASH.md). Você pode instalar com **bash Instalar.sh** e usar **jarvis-devin voz** diretamente nele. As instruções de PowerShell abaixo continuam disponíveis.

## 1. Baixar e extrair

Baixe jarvis-devin-windows.zip na página de versões do repositório. Antes de extrair, clique com o botão direito no ZIP → Propriedades. Se houver a opção **Desbloquear**, marque e aplique. Isso libera esse arquivo baixado, sem mudar uma política permanente do computador.

Extraia o ZIP em uma pasta local, por exemplo Downloads. Abra **COMECE-AQUI.html** para ler este guia no navegador.

## 2. Instalar

Dê dois cliques em **Instalar.cmd**. Ele abre o Windows PowerShell e prepara o programa na sua conta de usuário.

O instalador reutiliza um Python 3.12 ou 3.13 de 64 bits, se encontrar. Se faltar, tenta instalar Python 3.13 por winget. Depois prepara um ambiente separado, o áudio, o modelo de transcrição e o Devin CLI oficial, se necessário. O instalador do Devin pode pedir seu login.

O modelo precisa de aproximadamente **484 MB**. Python e dependências exigem downloads adicionais. Aguarde a mensagem **Arquivos preparados**. Se aparecer um erro, confira a explicação antes de seguir.

As pastas padrão são:

- Programa: **%LOCALAPPDATA%\JarvisDevin**.
- Perfil, memórias e relatórios: **%LOCALAPPDATA%\JarvisDevinData**.

Depois de instalar, feche e abra um **novo PowerShell** para o comando curto ser reconhecido. Também pode usar **Abrir.cmd** ou o atalho **Jarvis Devin** na Área de Trabalho.

## 3. Abrir o menu

No novo PowerShell, execute:

```powershell
jarvis-devin
```

Se ainda não encontrar o comando, este caminho completo funciona com a instalação padrão:

```powershell
& "$env:LOCALAPPDATA\JarvisDevin\bin\jarvis-devin.cmd"
```

O menu oferece:

1. Falar com o Devin.
2. Escrever um pedido.
3. Pesquisar com seu contexto, por voz ou texto.
4. Abrir o perfil.
5. Registrar uma memória.
6. Ver ou esquecer memórias.
7. Escolher o projeto.
8. Executar diagnóstico.
9. Abrir o Devin interativo.
0. Sair.

## 4. Escolher o projeto

Use a opção **7** e cole o caminho da pasta de trabalho, por exemplo C:\Projetos\MeuProjeto.

Se o PowerShell já estiver na pasta correta, pode usar:

```powershell
jarvis-devin projeto (Get-Location).Path
```

O projeto fica salvo para os próximos pedidos. Se não escolher, o programa usa uma pasta própria de trabalho. Antes de atuar em outro projeto, troque a pasta selecionada.

## 5. Confirmar o acesso ao Devin

Execute:

```powershell
jarvis-devin pedir "Responda apenas pronto" --interativo
```

Faça o login no Devin e confirme a confiança na pasta se ele solicitar. Quando terminar, digite:

```text
/exit
```

O Jarvis usa seu acesso ao Devin. Ele não fornece uma assinatura nem substitui as permissões da sua conta ou empresa.

## 6. Preencher seu perfil

```powershell
jarvis-devin perfil
```

O Bloco de Notas abre o perfil. Preencha função, objetivos, ferramentas, público e critérios de decisão. Salve. O texto será incluído nos próximos pedidos enviados ao Devin; coloque apenas o contexto que deseja disponibilizar.

Para salvar uma preferência válida para todos os projetos:

```powershell
jarvis-devin lembrar "Prefiro respostas em portugues com exemplos praticos e fontes" --global
```

Para salvar uma informação apenas no projeto atual:

```powershell
jarvis-devin lembrar "Este projeto usa Java 21 e Maven"
```

Adapte os exemplos ao seu trabalho antes de registrar. As memórias não são aprendidas automaticamente nesta versão.

## 7. Falar um pedido

```powershell
jarvis-devin voz
```

1. Pressione Enter para começar a gravar.
2. Fale, por exemplo: “Leia a documentação deste projeto e explique sua estrutura”.
3. Pressione Enter para parar.
4. Confira a transcrição no terminal.
5. Enter envia; uma correção digitada substitui o texto; cancelar descarta.
6. Aguarde a resposta. Um resumo poderá ser lido pela voz instalada no Windows.

Cada gravação dura até dois minutos. O microfone escuta apenas no período de gravação iniciado por você.

## 8. Fazer uma pesquisa por voz

```powershell
jarvis-devin voz --pesquisa
```

Exemplo: “Pesquise as mudanças recentes nas tecnologias que uso. Considere meu perfil e explique o impacto no meu trabalho. Cite fontes oficiais”.

O pedido usa o perfil e as memórias do projeto. A pesquisa depende das ferramentas e do acesso da sua conta do Devin. Se uma ferramenta estiver bloqueada, confira o aviso e resolva a permissão na sessão interativa.

## 9. Pesquisar por texto

```powershell
jarvis-devin pesquisar "Compare ferramentas de documentacao para este projeto, considerando meu perfil e citando fontes oficiais"
```

Para receber somente texto:

```powershell
jarvis-devin pesquisar "Pesquise novidades relevantes para meu trabalho" --sem-voz
```

## 10. Trabalhar na interface do Devin

```powershell
jarvis-devin pedir "Analise este projeto e me ajude a implementar a proxima tarefa" --interativo
```

Para falar o pedido inicial e abrir essa interface:

```powershell
jarvis-devin voz --interativo
```

Continue a conversa na interface do Devin e responda às permissões necessárias. Digite **/exit** ao terminar. Nesta versão, o pedido inicial pode ser falado; os turnos seguintes nessa sessão seguem a interface do Devin.

As consultas simples são sessões novas. Perfil e memórias explícitas são reutilizados. Para vários passos na mesma conversa, prefira a sessão interativa.

## 11. Diagnóstico e registros

```powershell
jarvis-devin diagnostico
jarvis-devin memorias
```

Para conferir o contexto que seria enviado sem chamar o Devin:

```powershell
jarvis-devin pesquisar "Teste de contexto" --simular
```

Para abrir os relatórios no Explorador de Arquivos:

```powershell
explorer "$env:LOCALAPPDATA\JarvisDevinData\relatorios"
```

Essa pasta aparece depois de uma consulta simples retornar. Sessões interativas seguem os registros do próprio Devin.

## Problemas comuns

**O Windows bloqueou o script:** confira se o ZIP foi desbloqueado nas propriedades antes de extrair. Se uma política da empresa exigir scripts assinados ou impedir instalações, a liberação precisa seguir o procedimento da empresa. O pacote não altera essas políticas.

**Python ou winget não encontrado:** instale Python 3.13 ou 3.12 de 64 bits pelo site oficial python.org e execute Instalar.cmd novamente. Outra versão, como Python 3.14, não é usada por este instalador.

**Falha ao carregar dependências nativas:** confira a mensagem do instalador. Se citar Visual C++ Runtime ou uma DLL relacionada, instale o Microsoft Visual C++ Redistributable x64 pelo endereço oficial indicado em FONTES.md, conforme a permissão do seu computador. Depois execute o instalador novamente.

**Devin não encontrado ou login pendente:** execute Instalar.cmd novamente ou siga a instalação oficial em FONTES.md. Abra a opção 9 para completar login e permissões no projeto escolhido.

**Microfone não funciona:** em Configurações do Windows → Privacidade e segurança → Microfone, confira o acesso ao microfone e a permissão para aplicativos da área de trabalho. No Windows 10, o caminho pode aparecer como Privacidade → Microfone. Confira também o dispositivo de entrada nas configurações de Som.

**Escolher outro microfone:** execute **jarvis-devin microfones**. Abra **%LOCALAPPDATA%\JarvisDevinData\config.json** e troque o campo microphone pelo índice desejado, por exemplo 2. O valor null usa o padrão do Windows.

**Não ouvi a resposta:** o programa usa uma voz de síntese instalada no Windows e tenta escolher uma em português brasileiro. Se não houver, usa a voz padrão. A resposta completa permanece no terminal. Confira volume e dispositivo de saída; o campo speak na configuração deve estar true.

**Modelo ausente ou download incompleto:** execute **jarvis-devin baixar-modelo**. O download usa uma versão fixa do modelo e verifica o arquivo principal antes de marcá-lo como pronto.

**Interromper uma consulta simples:** Ctrl+C. Para sair de uma sessão interativa do Devin: **/exit**.

## Atualizar ou remover

Para atualizar, execute o novo Instalar.cmd. Perfil, configuração e memórias existentes são preservados.

Para remover, apague a pasta **%LOCALAPPDATA%\JarvisDevin** e o atalho na Área de Trabalho. Para apagar também perfil, memórias e relatórios, remova **%LOCALAPPDATA%\JarvisDevinData**. A entrada da pasta bin pode ser removida do PATH do usuário nas configurações de variáveis de ambiente. Python e Devin permanecem instalados porque podem ser usados por outras ferramentas.

## Escopo desta versão

Windows 10/11 x64, voz por turnos, transcrição local na CPU, perfil, memórias explícitas e integração com o Devin. ARM64, conversa contínua, palavra de ativação, agenda, e-mail e pesquisas agendadas ainda não foram implementados ou validados.

O código e o ZIP são públicos. Seus dados locais são guardados fora dessa pasta e não são enviados ao GitHub pelo programa. O pedido e o contexto selecionado são enviados ao Devin conforme seu uso. O pacote não tem mensalidade própria; o Devin segue seu plano.
