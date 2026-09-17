#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera os artefatos de "Passado Resolvido, Futuro Decidido" (Márcio
Micheli) no mesmo formato que build_divinamente.py / build_mundoespiritual.py:

  1. RESUMO-PASSADORESOLVIDO.html -- deck standalone pra revisar fora do site.
  2. pages_passadoresolvido.html  -- <div class="page">...</div> prontos pro
     flipbook, com as imagens já embutidas em base64.
  3. toc_passadoresolvido.json    -- [{"folio": N, "title": "..."}] pro índice.

A capa (cover.jpg) é a foto real da capa física do livro, recortada pro
formato padrão do site -- não é gerada por IA. As 8 ilustrações internas
(images_jpg/ch1..8.jpg) são pintadas pelo Gemini (ver gemini_gen.py neste
mesmo diretório), no estilo animação das referências que o Xande mandou.

Rodar este script sempre que chapters.py mudar. Tudo fica versionado dentro
de build/passadoresolvido/, sem depender de /tmp.
"""
import base64
import html as htmlmod
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from chapters import ABERTURA, SINTESE, CHAPTERS

IMG_DIR = os.path.join(HERE, "images_jpg")
COVER_JPG = os.path.join(HERE, "cover.jpg")
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
OUT_DIR = HERE

os.makedirs(IMG_DIR, exist_ok=True)


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


def declaration_html(num, text):
    label = "DECLARAÇÃO %d" % num if isinstance(num, int) else "DECLARAÇÃO %s" % num
    return (
        '<div class="verse" style="background:var(--rust);margin-top:14px">'
        "“%s”<span class=\"ref\">%s</span></div>" % (esc(text), label)
    )


# ---------- 1) RESUMO-PASSADORESOLVIDO.html (standalone, imagens por caminho) ----------

HEAD_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Resumão · Passado Resolvido, Futuro Decidido</title>
<style>
  :root{
    --ink:#1a1c2e; --paper:#f5f0e6; --paper2:#efe8d8;
    --navy:#1f2b4d; --navy2:#27376a; --gold:#c8973f; --gold-soft:#e4c178;
    --rust:#a8482f; --teal:#2f6f6a; --muted:#6b6657;
    --line:rgba(31,43,77,.14); --shadow:0 18px 50px rgba(20,24,46,.18);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{height:100%}
  body{
    font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
    background:
      radial-gradient(1200px 700px at 80% -10%, #243463 0%, rgba(36,52,99,0) 55%),
      radial-gradient(900px 600px at -5% 110%, #2c1f3f 0%, rgba(44,31,63,0) 55%),
      #15182b;
    color:var(--ink); min-height:100%;height:100dvh;overflow:hidden;
    -webkit-font-smoothing:antialiased;
  }
  #bar{position:fixed;top:0;left:0;height:4px;width:0;background:linear-gradient(90deg,var(--gold),var(--gold-soft));z-index:50;transition:width .35s ease;box-shadow:0 0 14px rgba(200,151,63,.6)}
  #counter{position:fixed;top:16px;right:22px;z-index:40;color:#e7ddc7;font-size:13px;letter-spacing:.14em;font-family:"Helvetica Neue",Arial,sans-serif;opacity:.8}
  #menuBtn{position:fixed;top:13px;left:20px;z-index:40;background:rgba(245,240,230,.08);border:1px solid rgba(232,221,199,.25);color:#e7ddc7;border-radius:9px;padding:7px 12px;font-size:12px;letter-spacing:.12em;cursor:pointer;font-family:"Helvetica Neue",Arial,sans-serif;backdrop-filter:blur(6px)}
  #menuBtn:hover{background:rgba(245,240,230,.16)}
  #deck{position:relative;height:100%;width:100%;display:flex;align-items:center;justify-content:center;padding:46px 22px}
  .slide{display:none;width:min(960px,100%);max-height:calc(100dvh - 92px);background:linear-gradient(180deg,var(--paper) 0%,var(--paper2) 100%);border-radius:20px;box-shadow:var(--shadow);padding:48px 56px 60px;overflow:auto;position:relative;border:1px solid rgba(255,255,255,.4);animation:fade .5s ease}
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
  .meta{font-family:"Helvetica Neue",Arial,sans-serif;font-size:12.5px;letter-spacing:.05em;color:var(--muted);margin-top:22px;line-height:1.7}
  .hint{font-family:"Helvetica Neue",Arial,sans-serif;font-size:11.5px;color:var(--muted);margin-top:18px;letter-spacing:.03em}
  .recap{margin-top:14px}
  .recap li{font-family:"Iowan Old Style",Georgia,serif;font-style:italic;color:var(--navy2);font-size:15.5px;line-height:1.8;list-style:none;padding-left:26px;position:relative}
  .recap li::before{content:counter(r);counter-increment:r;position:absolute;left:0;top:2px;font-family:"Helvetica Neue",Arial,sans-serif;font-style:normal;font-size:11px;color:var(--gold);border:1px solid var(--gold);border-radius:50%;width:17px;height:17px;display:flex;align-items:center;justify-content:center}
  .recap{counter-reset:r}
</style>
</head>
<body>
<div id="bar"></div>
<div id="counter"></div>
<button id="menuBtn" onclick="location.reload()">&larr; Início</button>
<div id="deck">
"""

TAIL_TEMPLATE = """
</div>
<script>
  const slides=[...document.querySelectorAll('.slide')];
  let i=0;
  function render(){slides.forEach((s,idx)=>s.classList.toggle('active',idx===i));
    document.getElementById('counter').textContent=(i+1)+' / '+slides.length;
    document.getElementById('bar').style.width=((i+1)/slides.length*100)+'%';}
  document.addEventListener('keydown',e=>{
    if(e.key==='ArrowRight'&&i<slides.length-1){i++;render();}
    if(e.key==='ArrowLeft'&&i>0){i--;render();}
  });
  document.getElementById('deck').addEventListener('click',e=>{
    const r=document.getElementById('deck').getBoundingClientRect();
    if(e.clientX>r.left+r.width/2){if(i<slides.length-1){i++;render();}}
    else{if(i>0){i--;render();}}
  });
  render();
</script>
</body>
</html>
"""


def build_source_deck():
    slides = []
    slides.append(
        '<div class="slide art"><img src="build/passadoresolvido/cover.jpg" alt="Capa"></div>'
    )
    slides.append(
        '<div class="slide"><div class="kicker">%s</div><h1>%s</h1><div class="rule"></div>'
        "%s"
        '<div class="meta">%s</div><div class="hint">%s</div></div>'
        % (esc(ABERTURA["kicker"]), esc(ABERTURA["title"]), paras_html(ABERTURA["paras"]),
           esc(ABERTURA["meta"]), esc(ABERTURA["hint"]))
    )
    for c in CHAPTERS:
        slides.append(
            '<div class="slide"><div class="kicker">Capítulo %d</div><h2>%s</h2>'
            '<div class="rule"></div>%s%s%s%s</div>'
            % (
                c["num"], esc(c["title"]),
                paras_html(c["lead"].split("\n\n")),
                framework_html(c["framework"]),
                verse_html(c["verse_ref"], c["verse_text"]),
                declaration_html(c["num"], c["declaration"]),
            )
        )
        slides.append(
            '<div class="slide art"><img src="build/passadoresolvido/images_jpg/ch%d.jpg" alt="Arte do capítulo %d"></div>'
            % (c["num"], c["num"])
        )
    recap_items = "".join("<li>%s</li>" % esc(t) for t in SINTESE["recap"])
    slides.append(
        '<div class="slide"><div class="kicker">%s</div><h1>%s</h1><div class="rule"></div>'
        '%s<p style="margin-top:18px;font-weight:700;color:var(--navy)">%s</p>'
        '<ol class="recap">%s</ol>%s</div>'
        % (
            esc(SINTESE["kicker"]), esc(SINTESE["title"]), paras_html(SINTESE["paras"]),
            esc(SINTESE["recap_title"]), recap_items,
            declaration_html("Final", SINTESE["declaration"]),
        )
    )
    html = HEAD_TEMPLATE + "\n".join(slides) + TAIL_TEMPLATE
    out_path = os.path.join(REPO_ROOT, "RESUMO-PASSADORESOLVIDO.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("RESUMO-PASSADORESOLVIDO.html: %d bytes" % len(html))


# ---------- 2) pages_passadoresolvido.html + toc_passadoresolvido.json ----------

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
        'alt="Capa de Passado Resolvido, Futuro Decidido" draggable="false"></div>' % cover_b64
    )
    toc.append({"folio": folio, "title": "Capa"})
    folio += 1

    # Abertura em 2 paginas por causa da regra de paridade (ver
    # site-arquitetura.md): o front matter antes do capitulo 1 precisa ser
    # par, senao todo par texto/imagem sai desalinhado no spread.
    pages.append(
        '<div class="page"><div class="page-inner">'
        '<div class="kicker">%s</div><h1>%s</h1><div class="rule"></div>'
        "%s"
        '</div><div class="folio">%02d</div></div>'
        % (esc(ABERTURA["kicker"]), esc(ABERTURA["title"]), paras_html(ABERTURA["paras"][:2]), folio)
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
            esc(ABERTURA["title"]), paras_html(ABERTURA["paras"][2:], lead=False),
            esc(ABERTURA["meta"]), esc(ABERTURA["hint"]), folio,
        )
    )
    folio += 1

    for c in CHAPTERS:
        pages.append(
            '<div class="page"><div class="page-inner">'
            '<div class="kicker"><span class="u">Capítulo %d</span></div>'
            "<h2>%s</h2><div class=\"rule\"></div>"
            "%s%s%s%s"
            '</div><div class="folio">%02d</div></div>'
            % (
                c["num"], esc(c["title"]),
                paras_html(c["lead"].split("\n\n")),
                framework_html(c["framework"]),
                verse_html(c["verse_ref"], c["verse_text"]),
                declaration_html(c["num"], c["declaration"]),
                folio,
            )
        )
        toc.append({"folio": folio, "title": "Cap. %d — %s" % (c["num"], c["title"])})
        folio += 1

        img_b64 = b64_of(os.path.join(IMG_DIR, "ch%d.jpg" % c["num"]))
        pages.append(
            '<div class="page devo-page art-page"><img src="data:image/jpeg;base64,%s" '
            'alt="Ilustração do capítulo %d: %s" draggable="false">'
            '<div class="art-cap">Cap. %02d</div></div>'
            % (img_b64, c["num"], esc(c["title"]), c["num"])
        )
        folio += 1

    recap_items = "".join("<li>%s</li>" % esc(t) for t in SINTESE["recap"])
    pages.append(
        '<div class="page"><div class="page-inner">'
        '<div class="kicker">%s</div><h1>%s</h1><div class="rule"></div>'
        '%s<p style="margin-top:18px;font-weight:700;color:var(--navy);'
        'font-family:\'Helvetica Neue\',Arial,sans-serif;font-size:12.5px;'
        'letter-spacing:.03em">%s</p>'
        '<ol class="recap" style="margin-top:14px;counter-reset:r">%s</ol>'
        "%s"
        '</div><div class="folio">%02d</div></div>'
        % (
            esc(SINTESE["kicker"]), esc(SINTESE["title"]), paras_html(SINTESE["paras"]),
            esc(SINTESE["recap_title"]), recap_items,
            declaration_html("Final", SINTESE["declaration"]),
            folio,
        )
    )
    toc.append({"folio": folio, "title": "Síntese final"})
    folio += 1

    pages_html = "\n".join(pages)
    total_pages = len(re.findall(r'<div class="page["\s]', pages_html))
    out_pages = os.path.join(OUT_DIR, "pages_passadoresolvido.html")
    with open(out_pages, "w", encoding="utf-8") as f:
        f.write(pages_html)
    out_toc = os.path.join(OUT_DIR, "toc_passadoresolvido.json")
    with open(out_toc, "w", encoding="utf-8") as f:
        json.dump(toc, f, ensure_ascii=False, indent=2)
    print("OK: %d paginas no total (toc com %d entradas)" % (total_pages, len(toc)))
    print("pages_passadoresolvido.html: %d bytes" % len(pages_html))


def main():
    # A capa (cover.jpg) e' a foto real do livro fisico, ja recortada pro
    # formato padrao do site -- nao gerar de novo aqui. As 8 ilustracoes de
    # capitulo (images_jpg/ch1..8.jpg) sao pintadas pelo Gemini via
    # gemini_gen.py, rodado a parte (precisa de GEMINI_API_KEY no ambiente) e
    # versionadas no repo, no mesmo padrao do build_mundoespiritual.py.
    build_source_deck()
    build_flipbook()


if __name__ == "__main__":
    main()
