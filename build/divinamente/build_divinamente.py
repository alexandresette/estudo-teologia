#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera, a partir de CHAPTERS (chapters.py), os três artefatos do livro
"Divinamente" no mesmo formato que o resto da Biblioteca de Estudos usa:

  1. RESUMO-DIVINAMENTE.html  -- fonte autoral, deck standalone (mesmo
     esqueleto de RESUMAO-EXEGESE-AT.html), para ler/revisar fora do site.
     As imagens ficam por caminho relativo (nao embutidas), pra continuar
     legivel e leve.
  2. pages_divinamente.html   -- os <div class="page">...</div> prontos
     pra entrar no flipbook, com as imagens ja embutidas em base64.
  3. toc_divinamente.json     -- [{"folio": N, "title": "..."}] pro indice.

Rodar com este script (nao com o chunk_template.py perdido) sempre que
o conteudo de chapters.py mudar.
"""
import base64
import html as htmlmod
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from chapters import CHAPTERS

IMG_DIR = os.path.join(HERE, "images_jpg")
COVER_JPG = os.path.join(HERE, "cover.jpg")

# Todas as 20 ilustracoes sao paisagem 1408x768 (razao ~1.833) espremidas por
# object-fit:cover no quadro retrato da pagina (razao ~0.719): o corte final
# mostra so ~39% da largura original, centrado por padrao. Nas imagens abaixo
# o objeto de importancia (mao, figura, vulto) cai fora dessa janela central
# e precisa de um viés horizontal; valor = object-position-x em % (50 =
# centro/padrao, que e o que a maioria das imagens ja usa sem entrada aqui).
# Levantado por inspecao manual (grade de referencia a cada 10%) comparando
# a posicao real do sujeito com a janela de corte central.
ART_FOCUS_X = {
    3: 75,   # bom samaritano: acao central-direita
    5: 80,   # luz/jardim rompendo a ruina: abertura fica a direita
    8: 90,   # mao fechando o portao no meio da fumaca: mao bem a direita
    9: 85,   # figura junto a onda: figura a direita, sacrifica a onda
    12: 75,  # monge no banco: corpo cai a direita do vitral
    14: 25,  # mao entre as grades: mao e grade ficam a esquerda
    17: 90,  # figura ajoelhada no pomar: corpo cai bem a direita
    19: 65,  # mao erguida entre raizes: a mao que estende fica a direita
}
# RESUMO-DIVINAMENTE.html is the human-facing authored source and lives at
# the repo root next to the other RESUMAO-*.html decks; the flipbook
# fragments this script also produces (pages/toc) stay beside chapters.py
# so build6.py can read them with a plain relative-to-this-file path,
# with no dependency on ephemeral /tmp build artifacts.
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
OUT_DIR = HERE

ABERTURA = {
    "kicker": "Sobre este livro",
    "title": "Uma mente em obras",
    "paras": [
        "Todo mundo carrega um pensamento que não escolheu ter. Um medo que "
        "volta sempre na mesma hora da noite, uma voz interna que já decidiu "
        "o veredito antes de qualquer prova, um cansaço que não tem relação "
        "nenhuma com quanto se dormiu. Divinamente nasce dessa constatação "
        "simples: a mente humana está ferida, e boa parte do que se escreve "
        "sobre saúde mental trata o sintoma sem tocar na raiz.",
        "Dr. Jonatas Leonio parte de um lugar incomum para tratar o assunto: "
        "a mente de Cristo como modelo real de funcionamento, não como frase "
        "de efeito de púlpito. A tese atravessa os vinte capítulos inteira: "
        "existe uma mentalidade específica, descrita em Filipenses 2 pela "
        "palavra grega phroneo, e essa mentalidade pode ser aprendida, "
        "praticada e, aos poucos, herdada.",
        "Este resumo condensa esse percurso capítulo a capítulo, sempre com "
        "uma pintura ao lado de cada ideia central. A imagem não ilustra o "
        "versículo, ilustra o raciocínio: convida a olhar antes de ler, e a "
        "sentir antes de concordar.",
    ],
    "meta": "Dr. Jonatas Leonio · Aprendendo a pensar e sentir como Cristo",
    "hint": "Use as setas do teclado, os botões abaixo, ou o índice no canto.",
}

SINTESE = {
    "kicker": "Síntese",
    "title": "O que fica depois da leitura",
    "paras": [
        "Vinte capítulos depois, a pergunta que abriu o livro muda de figura. "
        "Não é mais só por que dói, é o que fazer com a dor enquanto ela "
        "ainda está aqui. Esse é o deslocamento real que Divinamente propõe: "
        "sair do diagnóstico e entrar no tratamento, sem pular a parte "
        "difícil do meio.",
        "A mente adoece, a mente de Cristo cura, a mente se renova, se "
        "guarda e cria hábitos que sustentam essa cura no dia a dia. Cada "
        "bloco do livro corresponde a uma dessas etapas, e nenhuma "
        "substitui a outra: remédio sem oração vira paliativo, e oração sem "
        "remédio, quando o corpo precisa dele, vira negação disfarçada de "
        "fé.",
        "Fica um convite direto: guardar o coração não é tarefa de um dia, é "
        "rotina que se cultiva. Água, luz, descanso, oração, comunhão, os "
        "hábitos do jardim do Éden continuam sendo, dois mil anos depois de "
        "Cristo, o desenho mais saudável que existe para uma mente inteira.",
    ],
    "verse_ref": "Romanos 12:2",
    "verse_text": "Não vos conformeis com este século, mas transformai-vos pela "
                  "renovação da vossa mente.",
    "verse_note": "Onde tudo começou, e onde tudo continua",
}


def esc(s):
    return htmlmod.escape(s, quote=True)


def paras_html(paras, lead=True):
    out = []
    for i, p in enumerate(paras):
        cls = ' class="lead"' if (i == 0 and lead) else ""
        out.append("<p%s>%s</p>" % (cls, esc(p).replace("\n\n", "</p><p>")))
    return "\n".join(out)


def framework_html(fw):
    if not fw:
        return ""
    cards = "".join(
        '<div class="card"><span class="tag">%s</span><p>%s</p></div>' % (esc(label), esc(desc))
        for label, desc in fw["items"]
    )
    label_bar = (
        '<p style="margin:16px 0 6px;font-weight:700;color:var(--navy);'
        'font-family:\'Helvetica Neue\',Arial,sans-serif;font-size:12.5px;'
        'letter-spacing:.03em">%s</p>' % esc(fw["title"])
    )
    return label_bar + '<div class="grid g2">' + cards + "</div>"


def verse_html(ref, text):
    return '<div class="verse">“%s”<span class="ref">%s</span></div>' % (esc(text), esc(ref))


# ---------- 1) RESUMO-DIVINAMENTE.html (standalone deck, images by path) ----------

HEAD_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Resumão · Divinamente</title>
<style>
  :root{
    --ink:#1a1c2e;
    --paper:#f5f0e6;
    --paper2:#efe8d8;
    --navy:#1f2b4d;
    --navy2:#27376a;
    --gold:#c8973f;
    --gold-soft:#e4c178;
    --rust:#a8482f;
    --teal:#2f6f6a;
    --muted:#6b6657;
    --line:rgba(31,43,77,.14);
    --shadow:0 18px 50px rgba(20,24,46,.18);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{height:100%}
  body{
    font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
    background:
      radial-gradient(1200px 700px at 80% -10%, #243463 0%, rgba(36,52,99,0) 55%),
      radial-gradient(900px 600px at -5% 110%, #2c1f3f 0%, rgba(44,31,63,0) 55%),
      #15182b;
    color:var(--ink);
    min-height:100%;height:100dvh;overflow:hidden;
    -webkit-font-smoothing:antialiased;
  }
  #bar{position:fixed;top:0;left:0;height:4px;width:0;background:linear-gradient(90deg,var(--gold),var(--gold-soft));z-index:50;transition:width .35s ease;box-shadow:0 0 14px rgba(200,151,63,.6)}
  #counter{position:fixed;top:16px;right:22px;z-index:40;color:#e7ddc7;font-size:13px;letter-spacing:.14em;font-family:"Helvetica Neue",Arial,sans-serif;opacity:.8}
  #menuBtn{position:fixed;top:13px;left:20px;z-index:40;background:rgba(245,240,230,.08);border:1px solid rgba(232,221,199,.25);color:#e7ddc7;border-radius:9px;padding:7px 12px;font-size:12px;letter-spacing:.12em;cursor:pointer;font-family:"Helvetica Neue",Arial,sans-serif;backdrop-filter:blur(6px)}
  #menuBtn:hover{background:rgba(245,240,230,.16)}
  #deck{position:relative;height:100%;width:100%;display:flex;align-items:center;justify-content:center;padding:46px 22px}
  .slide{
    display:none;width:min(960px,100%);max-height:calc(100dvh - 92px);
    background:linear-gradient(180deg,var(--paper) 0%,var(--paper2) 100%);
    border-radius:20px;box-shadow:var(--shadow);
    padding:48px 56px 60px;overflow:auto;position:relative;
    border:1px solid rgba(255,255,255,.4);
    animation:fade .5s ease;
  }
  .slide.active{display:block}
  .slide.art{padding:0;background:#0c0804}
  .slide.art img{width:100%;height:100%;object-fit:cover;display:block;border-radius:20px}
  @keyframes fade{from{opacity:0;transform:translateY(14px) scale(.99)}to{opacity:1;transform:none}}
  .slide::-webkit-scrollbar{width:9px}
  .slide::-webkit-scrollbar-thumb{background:rgba(31,43,77,.22);border-radius:9px}
  .kicker{font-family:"Helvetica Neue",Arial,sans-serif;font-size:12px;letter-spacing:.28em;text-transform:uppercase;color:var(--gold);font-weight:700;margin-bottom:14px;display:flex;align-items:center;gap:10px}
  h1{font-size:clamp(30px,4.4vw,50px);line-height:1.08;color:var(--navy);font-weight:700;letter-spacing:-.01em}
  h2{font-size:clamp(24px,3.2vw,34px);line-height:1.14;color:var(--navy);margin-bottom:6px;font-weight:700}
  .lead{font-size:17px;color:var(--muted);margin-top:12px;line-height:1.55}
  .lead::first-letter{float:left;font-family:"Iowan Old Style",Georgia,serif;font-size:2.6em;line-height:.78;padding:.04em .09em 0 0;color:var(--rust);font-weight:700}
  p{margin-top:12px;font-size:15.5px;line-height:1.55}
  .rule{height:2px;width:52px;background:linear-gradient(90deg,var(--gold),var(--rust));border-radius:3px;margin:14px 0 4px}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:8px}
  @media(max-width:640px){.grid{grid-template-columns:1fr}}
  .card{background:rgba(43,33,23,.05);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
  .card .tag{font-family:"Helvetica Neue",Arial,sans-serif;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--rust);font-weight:700;display:block;margin-bottom:4px}
  .card p{margin-top:0;font-size:13.5px;line-height:1.45}
  .verse{background:var(--navy);color:#f1e4c4;border-radius:10px;padding:16px 18px;margin:16px 0 4px;font-size:15px;line-height:1.5;position:relative;box-shadow:0 8px 18px rgba(20,14,8,.28)}
  .verse .ref{display:block;margin-top:8px;font-family:"Helvetica Neue",Arial,sans-serif;font-size:11px;letter-spacing:.14em;color:var(--gold-soft);text-transform:uppercase}
  .units{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:20px}
  .meta{font-family:"Helvetica Neue",Arial,sans-serif;font-size:12.5px;letter-spacing:.05em;color:var(--muted);margin-top:22px;line-height:1.7}
  .hint{font-family:"Helvetica Neue",Arial,sans-serif;font-size:11.5px;color:var(--muted);margin-top:18px;letter-spacing:.03em}
  .chain{display:flex;flex-wrap:wrap;align-items:stretch;gap:10px;margin-top:12px}
  .chain .step{flex:1;min-width:120px;background:rgba(43,33,23,.045);border:1px solid var(--line);border-top:3px solid var(--gold);border-radius:9px;padding:11px 12px}
  .chain .step b{display:block;color:var(--navy);font-size:13.5px;font-family:"Helvetica Neue",Arial,sans-serif}
  .chain .step span{font-size:12.5px;color:var(--muted);line-height:1.4}
  #idx{position:fixed;inset:0;background:rgba(10,8,20,.72);backdrop-filter:blur(6px);z-index:60;display:none;padding:60px 20px}
  #idx.open{display:block}
  #idx .close{position:fixed;top:18px;right:22px;color:#e7ddc7;font-size:22px;cursor:pointer}
  #idx .wrap{max-width:640px;margin:0 auto;background:var(--paper);border-radius:16px;padding:24px 10px;max-height:calc(100dvh - 120px);overflow:auto}
  #idx h4{font-family:"Helvetica Neue",Arial,sans-serif;padding:0 16px 10px;color:var(--navy)}
  #idx .item{display:flex;gap:12px;align-items:center;padding:10px 16px;cursor:pointer;border-radius:8px}
  #idx .item:hover{background:rgba(31,43,77,.07)}
  #idx .item .n{font-family:"Helvetica Neue",Arial,sans-serif;color:var(--gold);font-weight:700;font-size:12px}
  .nav{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);display:flex;gap:10px;z-index:40}
  .nav button{background:rgba(245,240,230,.1);border:1px solid rgba(232,221,199,.28);color:#e7ddc7;border-radius:9px;padding:9px 16px;cursor:pointer;font-size:16px}
  .nav button:disabled{opacity:.3;cursor:default}
</style>
</head>
<body>
<div id="bar"></div>
<button id="menuBtn" onclick="openIdx()">☰ ÍNDICE</button>
<div id="counter"></div>

<div id="deck">

"""

TAIL_TEMPLATE = """
</div>

<div id="idx"><span class="close" onclick="closeIdx()">✕</span><div class="wrap" id="idxWrap"></div></div>

<div class="nav">
  <button id="prev" onclick="go(cur-1)">←</button>
  <button id="next" onclick="go(cur+1)">→</button>
</div>

<script>
  const slides=[...document.querySelectorAll('.slide')];
  let cur=0;
  const bar=document.getElementById('bar');
  const counter=document.getElementById('counter');
  function render(){
    slides.forEach((s,i)=>s.classList.toggle('active',i===cur));
    bar.style.width=((cur)/(slides.length-1)*100)+'%';
    counter.textContent=String(cur+1).padStart(2,'0')+' / '+String(slides.length).padStart(2,'0');
    document.getElementById('prev').disabled=cur===0;
    document.getElementById('next').disabled=cur===slides.length-1;
    const a=slides[cur]; if(a) a.scrollTop=0;
  }
  function go(i){ if(i<0||i>=slides.length)return; cur=i; render(); closeIdx(); }
  document.addEventListener('keydown',e=>{
    if(document.getElementById('idx').classList.contains('open')){ if(e.key==='Escape')closeIdx(); return; }
    if(e.key==='ArrowRight'||e.key===' '||e.key==='PageDown'){e.preventDefault();go(cur+1);}
    if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();go(cur-1);}
    if(e.key==='Home')go(0); if(e.key==='End')go(slides.length-1);
    if(e.key.toLowerCase()==='m')openIdx();
  });
  const wrap=document.getElementById('idxWrap');
  let html='<h4>Índice</h4>';
  slides.forEach((s,i)=>{
    const t=s.getAttribute('data-title')||('Slide '+(i+1));
    html+=`<div class="item" onclick="go(${i})"><span class="n">${String(i+1).padStart(2,'0')}</span><span class="t">${t}</span></div>`;
  });
  wrap.innerHTML=html;
  function openIdx(){document.getElementById('idx').classList.add('open');}
  function closeIdx(){document.getElementById('idx').classList.remove('open');}
  render();
</script>
</body>
</html>
"""


def build_source_deck():
    sections = []
    sections.append(
        '  <section class="slide cover active" data-title="Capa">\n'
        '    <div class="kicker">Livros</div>\n'
        '    <h1>Divinamente</h1>\n'
        '    <div class="rule"></div>\n'
        '    <p class="lead">Aprendendo a pensar e sentir como Cristo.</p>\n'
        '    <div class="meta">Dr. Jonatas Leonio</div>\n'
        '    <div class="hint">Capa ilustrada: build/divinamente/cover.jpg</div>\n'
        "  </section>\n"
    )
    sections.append(
        '  <section class="slide" data-title="%s">\n'
        '    <div class="kicker">%s</div>\n'
        "    <h1>%s</h1>\n"
        '    <div class="rule"></div>\n'
        "    %s\n"
        "  </section>\n"
        % (
            esc(ABERTURA["title"]), esc(ABERTURA["kicker"]), esc(ABERTURA["title"]),
            paras_html(ABERTURA["paras"][:1]),
        )
    )
    sections.append(
        '  <section class="slide" data-title="%s (cont.)">\n'
        '    <div class="kicker">%s · continua</div>\n'
        "    %s\n"
        '    <div class="meta">%s</div>\n'
        '    <div class="hint">%s</div>\n'
        "  </section>\n"
        % (
            esc(ABERTURA["title"]), esc(ABERTURA["title"]),
            paras_html(ABERTURA["paras"][1:], lead=False),
            esc(ABERTURA["meta"]), esc(ABERTURA["hint"]),
        )
    )
    for c in CHAPTERS:
        sections.append(
            '  <section class="slide" data-title="Cap. %d — %s">\n'
            '    <div class="kicker"><span class="u">Capítulo %d</span></div>\n'
            "    <h2>%s</h2>\n"
            '    <div class="rule"></div>\n'
            "    %s\n"
            "    %s\n"
            "    %s\n"
            "  </section>\n"
            % (
                c["num"], esc(c["title"]), c["num"], esc(c["title"]),
                paras_html(c["lead"].split("\n\n")),
                framework_html(c["framework"]),
                verse_html(c["verse_ref"], c["verse_text"]),
            )
        )
        sections.append(
            '  <section class="slide art" data-title="Cap. %d — ilustração" data-img="images_jpg/ch%d.jpg">\n'
            '    <img src="build/divinamente/images_jpg/ch%d.jpg" alt="Ilustração do capítulo %d">\n'
            "  </section>\n" % (c["num"], c["num"], c["num"], c["num"])
        )
    sections.append(
        '  <section class="slide cover" data-title="Síntese final">\n'
        '    <div class="kicker">%s</div>\n'
        "    <h1>%s</h1>\n"
        '    <div class="rule"></div>\n'
        "    %s\n"
        "    %s\n"
        "  </section>\n"
        % (
            esc(SINTESE["kicker"]), esc(SINTESE["title"]), paras_html(SINTESE["paras"]),
            verse_html(SINTESE["verse_ref"], SINTESE["verse_text"]),
        )
    )
    return HEAD_TEMPLATE + "\n".join(sections) + TAIL_TEMPLATE


# ---------- 2) pages_divinamente.html + toc_divinamente.json (flipbook, base64 baked in) ----------

def b64_of(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def build_flipbook():
    pages = []
    toc = []
    folio = 1

    cover_b64 = b64_of(COVER_JPG)
    pages.append(
        '<div class="page devo-page devo-cover"><img src="data:image/jpeg;base64,%s" '
        'alt="Capa de Divinamente, de Dr. Jonatas Leonio" draggable="false"></div>' % cover_b64
    )
    toc.append({"folio": folio, "title": "Capa"})
    folio += 1

    # Abertura runs across 2 pages (not 1) on purpose: every chapter after it
    # is exactly 2 pages (texto + arte), so the front matter needs to be an
    # even number of pages too, or the text/image pairs land on the wrong
    # side of every two-page spread for the rest of the book.
    pages.append(
        '<div class="page"><div class="page-inner">'
        '<div class="kicker">%s</div><h1>%s</h1><div class="rule"></div>'
        "%s"
        '</div><div class="folio">%02d</div></div>'
        % (
            esc(ABERTURA["kicker"]), esc(ABERTURA["title"]),
            paras_html(ABERTURA["paras"][:1]), folio,
        )
    )
    toc.append({"folio": folio, "title": ABERTURA["title"]})
    folio += 1

    pages.append(
        '<div class="page"><div class="page-inner">'
        '<div class="pagehead">%s · continua</div>'
        "%s"
        '<div class="meta">%s</div><div class="hint">%s</div>'
        '</div><div class="folio">%02d</div></div>'
        % (
            esc(ABERTURA["title"]), paras_html(ABERTURA["paras"][1:], lead=False),
            esc(ABERTURA["meta"]), esc(ABERTURA["hint"]), folio,
        )
    )
    folio += 1

    for c in CHAPTERS:
        pages.append(
            '<div class="page"><div class="page-inner">'
            '<div class="kicker"><span class="u">Capítulo %d</span></div>'
            "<h2>%s</h2><div class=\"rule\"></div>"
            "%s%s%s"
            '</div><div class="folio">%02d</div></div>'
            % (
                c["num"], esc(c["title"]),
                paras_html(c["lead"].split("\n\n")),
                framework_html(c["framework"]),
                verse_html(c["verse_ref"], c["verse_text"]),
                folio,
            )
        )
        toc.append({"folio": folio, "title": "Cap. %d — %s" % (c["num"], c["title"])})
        folio += 1

        img_b64 = b64_of(os.path.join(IMG_DIR, "ch%d.jpg" % c["num"]))
        focus_x = ART_FOCUS_X.get(c["num"])
        style_attr = ' style="object-position:%d%% 50%%"' % focus_x if focus_x else ""
        pages.append(
            '<div class="page devo-page art-page"><img src="data:image/jpeg;base64,%s" '
            'alt="Ilustração do capítulo %d: %s" draggable="false"%s>'
            '<div class="art-cap">Cap. %02d</div></div>'
            % (img_b64, c["num"], esc(c["title"]), style_attr, c["num"])
        )
        folio += 1

    pages.append(
        '<div class="page"><div class="page-inner">'
        '<div class="kicker">%s</div><h1>%s</h1><div class="rule"></div>'
        "%s%s"
        '</div><div class="folio">%02d</div></div>'
        % (
            esc(SINTESE["kicker"]), esc(SINTESE["title"]), paras_html(SINTESE["paras"]),
            verse_html(SINTESE["verse_ref"], SINTESE["verse_text"]), folio,
        )
    )
    toc.append({"folio": folio, "title": "Síntese final"})

    return "\n".join(pages), toc


def main():
    deck = build_source_deck()
    with open(os.path.join(REPO_ROOT, "RESUMO-DIVINAMENTE.html"), "w", encoding="utf-8") as f:
        f.write(deck)

    pages_html, toc = build_flipbook()
    with open(os.path.join(OUT_DIR, "pages_divinamente.html"), "w", encoding="utf-8") as f:
        f.write(pages_html)
    with open(os.path.join(OUT_DIR, "toc_divinamente.json"), "w", encoding="utf-8") as f:
        json.dump(toc, f, ensure_ascii=False, indent=2)

    import re as _re
    total_pages = len(_re.findall(r'<div class="page["\s]', pages_html))
    print("OK: %d paginas no total (toc com %d entradas)" % (total_pages, len(toc)))
    print("pages_divinamente.html: %d bytes" % os.path.getsize(os.path.join(OUT_DIR, "pages_divinamente.html")))


if __name__ == "__main__":
    main()
