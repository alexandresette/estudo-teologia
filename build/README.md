# Build — Biblioteca de Estudos (estudo-teologia)

Como gerar e manter o site. Leia isso antes de mexer na arquitetura, e
confira `git log --oneline -20` pra ver o que mudou desde a última vez.

## O que é

Site estático com uma "biblioteca 3D": tela inicial com corredores
(Teologia, No Secreto, Resumo de Livros), cada corredor com capas de
livro clicáveis, cada livro um flipbook de verdade (StPageFlip, página
vira arrastando ou clicando na borda).

**Desde setembro/2026 o site é multi-página de verdade.** Cada corredor
e cada livro é um arquivo HTML físico, com URL própria:

- `index.html` — hall de entrada (escolha de corredor)
- `corredor/teologia.html`, `corredor/secreto.html`, `corredor/livros.html`
- `livro/<id>/index.html` — um por livro (URL fica `livro/<id>/`)
- `assets/` — CSS, JS (`site.js`), StPageFlip (`pageflip.js`), imagens e
  vídeo do portão, todos como arquivos reais (nada em base64 embutido)

Antes disso era um `index.html` monolítico de ~49 MB com tudo embutido
em base64 e roteamento por hash. Isso foi abandonado porque o usuário
queria páginas de verdade (URL própria, sobrevive a Ctrl+Shift+R sem
voltar pra tela inicial) em vez de uma SPA fingindo ser site. O monólito
antigo não morreu: virou a **fonte de build**, guardado em
`build/source_monolith.html`. Ele nunca é servido nem editado à mão —
só existe pra os scripts abaixo extraírem conteúdo dele.

## Pipeline de build (gerar o site a partir da fonte)

Dois scripts, nessa ordem, sempre a partir da raiz do repo:

```
python3 build/extract_multipage.py   # lê build/source_monolith.html, escreve
                                      # assets/, corredor/, livro/<id>/_content.html
                                      # e livro/<id>/img/*.jpg (decodifica os base64,
                                      # dedup por hash) + _meta.json intermediário
python3 build/generate_pages.py      # lê _meta.json + _content.html, escreve as
                                      # páginas finais (index.html, corredor/*.html,
                                      # livro/<id>/index.html) e copia build/site.js
                                      # pra assets/site.js
```

Rodar os dois de novo é sempre um rebuild completo e seguro (não precisa
de passo manual depois). Os arquivos intermediários (`_meta.json`,
`livro/<id>/_content.html`) não vão pro commit — já estão no
`.gitignore`? **Confirmar isso**; se não estiverem, adicionar, porque
são lixo de build, não conteúdo.

`build/site.js` é **autoral** (não é gerado a partir do monólito) — é o
motor compartilhado de flip/notas/portão/som que toda página de livro
carrega via `<script src="assets/site.js">`. Editar sempre em
`build/site.js`, nunca direto em `assets/site.js` (isso é sobrescrito a
cada `generate_pages.py`).

## Regra inegociável

**Nunca alterar o texto teológico/devocional de um livro já existente**
sem pedido explícito. Isso vale tanto pra conteúdo dentro de
`build/source_monolith.html` quanto, depois do rebuild, pro
`livro/<id>/index.html` gerado. Qualquer mudança estrutural (CSS, JS,
layout, arquitetura) não deve mexer no texto visível de nenhum livro —
confirma visualmente antes de comitar.

Os scripts antigos de verificação automática disso
(`build/verify_integrity.py`, `build/regression_check.py`) são do
**pipeline antigo de arquivo único** e não funcionam mais como estão
(apontam pro `index.html` monolítico e pro clique via `data-corridor`,
que não existe mais na navegação por `<a href>` real). Não rodar sem
adaptar primeiro. O jeito atual de testar é manual, via Playwright,
apontando pra cada `livro/<id>/`:

1. Sobe um servidor local na raiz do repo:
   ```
   (nohup python3 -m http.server 8899 > /tmp/http8899.log 2>&1 &) ; sleep 1
   ```
2. **Importante**: o portão de entrada aparece em toda página (inclusive
   nas de livro) e bloqueia clique/tecla até ser destravado. Antes de
   testar qualquer página de livro direto, desbloqueia via
   `sessionStorage.setItem('estudoGateUnlocked','1')` depois de visitar
   `index.html` uma vez (ou simula o fluxo completo: entra na senha,
   depois navega).
3. Testa por livro: abre `livro/<id>/`, confere `#counter`, aperta
   `ArrowRight` (espera >650ms, que é o `flippingTime` do StPageFlip,
   antes de checar o contador — testar cedo demais parece bug e não é),
   testa um item do índice que não seja o primeiro nem o segundo
   (os primeiros caem no mesmo "spread" de 2 páginas e dão falso
   negativo de "não mudou"), testa salvar nota se o livro tiver TOC.

## Pipeline pra adicionar um livro novo

Hoje isso significa editar `build/source_monolith.html` (acrescentar
uma entrada em `BOOKS`/`DEVOS`/`LIVROS` e o `<div id="book-NOVO">`
correspondente, igual sempre foi) e rodar os dois scripts de novo. Fica
pra decidir, numa próxima sessão, se vale a pena trocar esse fluxo por
algo que não exija editar o monólito à mão — hoje funciona, mas é o elo
mais manual do processo.

## Engenharia do leitor (StPageFlip) — coisas não óbvias

(Isso não mudou com a migração pra multi-página, é tudo em `site.js`.)

- `showPageCorners:false` no construtor da `PageFlip`: sem isso, só
  passar o mouse perto da borda já "gruda" a ponta da página pra
  arrastar. Com `false`, só gruda em clique-e-segure; clique simples
  continua virando a página inteira.
- **Seleção de texto**: a StPageFlip cancela a seleção nativa do
  navegador em qualquer `mousedown` sobre a página. O fix é um listener
  de `mousedown`/`touchstart` em fase de captura no `.reader-stage` que
  dá `stopPropagation()` quando o alvo é texto de verdade (ver
  `isFlipZoneTarget()`/`guardTextSelection()` em `site.js`).
- **`goBookStart()`**: usa `turnToPage(0)` duas vezes (a segunda 700ms
  depois) em vez de `flip(0)` animado, porque uma virada em andamento
  pode sobrescrever o salto se só chamar uma vez.
- **`pf.flip(N)` arredonda pra baixo até o índice ímpar do "spread"**:
  pedir pra ir pra página 2 ou 3 pousa no mesmo lugar (página 1, no
  spread 1-2). Não é bug, é como a lib mostra duas páginas por vez.
- Primeiríssimo `flipNext()` logo depois de abrir qualquer livro é
  engolido pela lib enquanto a capa dura termina de assentar. Segundo
  clique em diante funciona normal. Não vale a pena perseguir.
- `#reader` é posicionado como overlay cheio de tela quando tem a
  classe `.show`; `.flipbtn`/`.reader-hint` precisam ser **irmãos** de
  `#reader` no DOM (CSS usa `#reader.show ~ .flipbtn`), nunca filhos —
  colocar dentro quebra a visibilidade dos botões.

## Efeitos sonoros e portão de entrada

- Efeitos de UI são sintetizados na hora via Web Audio (sem arquivo de
  áudio). Botão de mudo persiste em `localStorage` (por origem, vale
  pra todas as páginas).
- O portão (`#gate`, vídeo de fundo + senha) decide se esconde via
  `sessionStorage.estudoGateUnlocked` — também por origem, então
  desbloquear uma vez vale pra qualquer página do site na mesma aba.

## Workflow de git (contas)

Duas contas no `gh`: `alexandresette` (pessoal, dona deste repo) e
`alexandresettesf` (trabalho). Sempre conferir antes de operar:
```
gh api user --jq .login
```
Se não for `alexandresette`, trocar com `gh auth switch --user alexandresette`.
O sandbox na nuvem não tem credencial de git push (a VM é isolada de
propósito) — commit pode ser feito por lá, mas o `git push` final é
sempre no terminal real do Mac do usuário.

## Arquivos versionados no repo

`index.html`, `corredor/*.html`, `livro/<id>/index.html` + `img/*`,
`assets/*`, `build/*.py`, `build/site.js`, `build/source_monolith.html`,
este README. Os `RESUMO-*.html`/`RESUMAO-*.html` soltos na raiz são
material de trabalho antigo, de antes da consolidação no monólito — por
histórico, não por regra.
