# Build — Biblioteca de Estudos (estudo-teologia)

Como gerar e manter o `index.html` do flipbook. Leia isso antes de mexer
na arquitetura — não precisa de mais contexto além do que está aqui e no
próprio código.

## O que é

`index.html` é um flipbook autocontido (StPageFlip inline, CSS/JS/imagens
em `data:` URI, ~11 MB) com uma "biblioteca 3D": tela inicial com
corredores (Teologia, No Secreto, Livros), cada corredor com capas de
livro clicáveis, cada livro um flipbook de verdade (página vira
arrastando ou clicando na borda).

Ele é **gerado**, nunca editado à mão. A fonte de verdade é
`build/build6.py` + um `RESUMAO-<LIVRO>.html` por matéria (conteúdo
bruto, não commitado — ver "Arquivos versionados" abaixo).

## Regra inegociável

**Nunca alterar o texto teológico/devocional de um livro já existente.**
Toda mudança na arquitetura (CSS, JS, layout) passa por
`verify_integrity.py` depois do rebuild — ele compara o texto visível de
cada livro no `index.html` gerado contra o `RESUMAO-<LIVRO>.html`
original e espera **exatamente 2 opcodes de diff por livro**, os dois
"delete" do lado do arquivo original (é o texto de capa/síntese que o
`.decompose()` de `.folio`/`.pagehead`/`.cover-page` exclui da
comparação — não é conteúdo perdido). Qualquer coisa diferente disso é
bug, não segue em frente.

## Pipeline pra adicionar um livro novo

1. **Escrever o RESUMAO**: `RESUMAO-<LIVRO>.html` com uma
   `<section class="slide" data-title="...">` por página de conteúdo.
   Primeira seção leva classe `cover`. Estilo de escrita segue
   `writing-style.md` da memória do projeto (sem travessão, sem
   antítese mecânica tipo "não é X, é Y", sem gerúndio composto, varia
   o tamanho das frases). Roda um grep rápido pra conferir antes de
   seguir: `—`, `não é.*é `, `estar \+ gerúndio`.
2. **Chunkar**: copia `chunk_template.py` pra `chunk_<id>.py`, ajusta
   `BOOK_ID`/`SRC_PATH`, roda. Ele gera `/tmp/pages_<id>.html` e
   `/tmp/toc_<id>.json`. **A contagem de páginas impressa precisa ser
   PAR** (regra de paridade da capa dura traseira da StPageFlip — capa
   só vira reta/plana quando o total é par). Se der ímpar, split uma
   seção grande em duas usando o padrão de continuação: a seção nova
   leva `<div class="pagehead">Título · continua</div>` como primeiro
   filho em vez do kicker/h2/hr normal.
3. **Registrar em `build6.py`**: acrescenta uma entrada em
   `THEOLOGY_BOOKS` (id, title, prof, theme, cover_a, cover_b,
   pages_file, toc_file) e as variáveis CSS `--<theme>`/`--<theme>-deep`
   no `:root` (escolhe uma cor de capa que não repita as já usadas).
4. **Rebuild**: `python3 build/build6.py` (a partir da raiz do repo
   clonado). Escreve `index.html` na raiz.
5. **Servir localmente pra testar**: o Playwright dos scripts abaixo
   espera `http://localhost:8801`. Sobe assim (precisa desse formato pra
   sobreviver entre chamadas de shell separadas):
   ```
   setsid nohup python3 -m http.server 8801 --directory . >/tmp/http8801.log 2>&1 & disown
   ```
   Confere com `curl -s -o /dev/null -w "%{http_code}" http://localhost:8801/index.html`
   antes de rodar os testes — esse servidor cai sozinho de vez em
   quando, só resubir se não voltar 200.
6. **Verificar**:
   - `python3 build/verify_integrity.py` — integridade de conteúdo
     (regra acima). Ajusta a lista `pairs` no topo do script pra incluir
     o livro novo.
   - `python3 build/regression_check.py` — Playwright abre cada livro,
     vira 5 páginas, checa que não disparou `pageerror`. Ajusta a lista
     de `(book_id, corridor)` no topo.
   - Capturas de tela (Playwright, `page.screenshot`) da estante, capa
     e miolo do livro novo — checagem visual manual.
7. **Entregar**: o `index.html` final vai pro repo do Mac do usuário via
   a ponte de dispositivo (`SendUserFile` + `device_commit_files`),
   confirmando md5 dos dois lados. **O sandbox na nuvem não tem
   credencial de git push** (a VM da ponte é isolada de propósito) — o
   commit dá pra fazer por lá, mas o `git push` final é sempre no
   terminal real do usuário no Mac (`gh api user --jq .login` pra
   conferir a conta ativa, troca pra `alexandresette` se precisar).

## Arquivos versionados no repo

Só `index.html`, `README.md` e (por histórico, não é regra) dois
`RESUMAO-*.html` antigos estão no git. Os `RESUMAO-<LIVRO>.html` de cada
matéria são material de trabalho/autoria, não entram no commit — o
entregável é só o `index.html` gerado. Scripts de build ficam em
`build/`.

## Engenharia do leitor (StPageFlip) — coisas não óbvias

- `showPageCorners:false` no construtor da `PageFlip`: sem isso, só
  passar o mouse perto da borda já "gruda" a ponta da página pra
  arrastar. Com `false`, só gruda em clique-e-segure; um clique simples
  continua virando a página inteira (comportamento da própria lib,
  intocado).
- **Seleção de texto**: a StPageFlip faz `preventDefault()` em qualquer
  `mousedown` sobre a página por padrão (é assim que ela gruda no
  dedo/mouse), o que cancela a seleção nativa do navegador. O fix é um
  listener de `mousedown`/`touchstart` em fase de **captura** no
  `.reader-stage` (a lib registra o dela na fase de bolha, então o
  nosso roda primeiro) que dá `stopPropagation()` quando o alvo do
  clique é texto de verdade (não margem, não `.folio`/`.pagehead`, não
  `<img>` — ver `isFlipZoneTarget()`/`guardTextSelection()` em
  `build6.py`). Efeito colateral esperado: clicar em cima de um
  parágrafo não vira mais a página com um clique simples (só clicar na
  margem/borda vira) — é o comportamento correto de qualquer leitor
  tipo Issuu/Flipsnack.
- **`goBookStart()`** (botão "Início"): usa `turnToPage(0)` (salto
  instantâneo) em vez de `flip(0)` (animado) porque o animado tem um bug
  de pouso ao aproximar da página 0 vindo de longe. E chama
  `turnToPage(0)` **duas vezes**, a segunda 700ms depois: se o clique
  pegou uma virada de página ainda em andamento, essa virada termina
  DEPOIS do nosso salto e sobrescreve o índice sozinha — a segunda
  chamada é a trava de segurança.
- **Quirk pré-existente, não é bug**: o primeiríssimo `flipNext()` logo
  depois de abrir qualquer livro (devocional ou texto) é
  confiavelmente engolido pela lib enquanto a capa dura termina de
  assentar. Segundo clique em diante funciona normal. Não vale a pena
  perseguir isso.

## Efeitos sonoros e música de fundo

- Efeitos de UI (hover, clique, virar página, abrir/fechar livro,
  trocar de corredor) são **sintetizados na hora via Web Audio**
  (osciladores + ruído filtrado), sem nenhum arquivo de áudio — mantém
  o `index.html` autocontido. Botão de mudo persiste em
  `localStorage`.
- Música de fundo é **outra categoria**: são faixas de verdade, e
  embutir em base64 infla o arquivo em dezenas de MB por música. Por
  isso NÃO fica embutida — cada faixa é um `.mp3` solto numa pasta
  `audio/` ao lado do `index.html`, referenciada por caminho relativo
  no array `MUSIC_TRACKS` (topo do bloco de música em `build6.py`).
  **Cuidado com direito autoral**: nunca adiciona uma faixa sem
  confirmação de que é royalty-free/CC0 ou que o usuário tem os
  direitos — checa a tag ID3 (artista/título) antes, um rip de
  YouTube geralmente denuncia isso no próprio metadata (tag `TOPE`,
  título com nome de canal "Official", etc.).

## Testes

`test_ux_features.py` (não incluído aqui, é reconstruível rápido se
precisar) cobre: botão de som visível + toggle + persistência, seleção
de texto por arraste numa página de texto (pega um `<p>` dentro de um
`.stf__item` com `display!=none`, já que a StPageFlip mantém TODAS as
páginas no DOM e só a spread atual está visível), clique em margem
ainda vira página, `homeBtn` volta pra página 1, devocional (imagem)
ainda vira com clique.
