# -*- coding: utf-8 -*-
import base64
import json
import html as htmlmod

# ---- theology "resumão" books (the flipbook-per-subject library) ----
# Adding a new subject = one entry here. Everything else (CSS cover
# gradient, the JS BOOKS array + container wiring, the <div id="book-...">
# assembly, the TOC injection) is generated from this list below --
# nothing else in this file should need a per-book edit.
THEOLOGY_BOOKS = [
    {
        "id": "exegese",
        "title": "Exegese do Antigo Testamento",
        "prof": "Prof. Josias Costa",
        "theme": "at",
        "cover_a": "var(--rust)",
        "cover_b": "var(--rust-deep)",
        "pages_file": "/tmp/pages_exegese.html",
        "toc_file": "/tmp/toc_exegese.json",
    },
    {
        "id": "tbnt",
        "title": "Teologia Bíblica\ndo Novo Testamento",
        "prof": "Profa. Dra. Denise Santana",
        "theme": "nt",
        "cover_a": "var(--teal)",
        "cover_b": "var(--teal-deep)",
        "pages_file": "/tmp/pages_tbnt.html",
        "toc_file": "/tmp/toc_tbnt.json",
    },
    {
        "id": "grego",
        "title": "Grego\nInstrumental",
        "prof": "Prof. Josias Costa",
        "theme": "grc",
        "cover_a": "var(--gold)",
        "cover_b": "var(--umber2)",
        "pages_file": "/tmp/pages_grego.html",
        "toc_file": "/tmp/toc_grego.json",
    },
    {
        "id": "homiletica",
        "title": "Homilética",
        "prof": "Profa. Dra. Denise Santana",
        "theme": "homi",
        "cover_a": "var(--plum)",
        "cover_b": "var(--plum-deep)",
        "pages_file": "/tmp/pages_homi.html",
        "toc_file": "/tmp/toc_homi.json",
    },
    {
        "id": "missio",
        "title": "Missiologia e\nEducação Cristã",
        "prof": "Profa. Dra. Denise Santana",
        "theme": "missio",
        "cover_a": "var(--azure)",
        "cover_b": "var(--azure-deep)",
        "pages_file": "/tmp/pages_missio.html",
        "toc_file": "/tmp/toc_missio.json",
    },
    {
        "id": "arbi",
        "title": "Arqueologia\nBíblica",
        "prof": "Dra. Denise Santana, MSc",
        "theme": "arbi",
        "cover_a": "var(--terracotta)",
        "cover_b": "var(--terracotta-deep)",
        "pages_file": "/tmp/pages_arbi.html",
        "toc_file": "/tmp/toc_arbi.json",
    },
    {
        "id": "tcc1",
        "title": "Projeto de\nPesquisa",
        "prof": "Prof. Josias Costa, MSc",
        "theme": "tcc1",
        "cover_a": "var(--slate)",
        "cover_b": "var(--slate-deep)",
        "pages_file": "/tmp/pages_tcc1.html",
        "toc_file": "/tmp/toc_tcc1.json",
    },
    {
        "id": "exnote",
        "title": "Exegese do\nNovo Testamento",
        "prof": "Prof. Josias Costa, MSc",
        "theme": "exnote",
        "cover_a": "var(--wine)",
        "cover_b": "var(--wine-deep)",
        "pages_file": "/tmp/pages_exnote.html",
        "toc_file": "/tmp/toc_exnote.json",
    },
]
for _b in THEOLOGY_BOOKS:
    _b["pages"] = open(_b["pages_file"], encoding="utf-8").read()
    _b["toc"] = json.load(open(_b["toc_file"], encoding="utf-8"))

pageflip_js = open("/home/claude/estudo-teologia/vendor/page-flip.browser.js", encoding="utf-8").read()
landing_b64 = open("/tmp/landing-corridors_b64.txt", encoding="ascii").read().strip()
corshelf_b64 = open("/tmp/corridor-shelf_b64.txt", encoding="ascii").read().strip()
table_art_b64 = open("/tmp/table_art_b64.txt", encoding="ascii").read().strip()
devo_manifest = json.load(open("/tmp/secreto_manifest.json", encoding="utf-8"))
livros_manifest = json.load(open("/tmp/livros_manifest.json", encoding="utf-8"))

# ---- "Divinamente" (Dr. Jonatas Leonio) -- a rich Livros-shelf book, real
# HTML pages + toc like the theology resumões, but shelved under "Livros"
# with its own designed cover image instead of a CSS-gradient cover. Content
# lives in build/divinamente/ (chapters.py is the authored source; run
# build/divinamente/build_divinamente.py after editing it to refresh the two
# files below plus the human-readable RESUMO-DIVINAMENTE.html deck) -- all
# committed to the repo, not /tmp, so this book stays rebuildable.
_DIVINAMENTE_DIR = "/home/claude/estudo-teologia/build/divinamente"
divinamente_pages = open(_DIVINAMENTE_DIR + "/pages_divinamente.html", encoding="utf-8").read()
divinamente_toc = json.load(open(_DIVINAMENTE_DIR + "/toc_divinamente.json", encoding="utf-8"))
divinamente_cover_b64 = base64.b64encode(open(_DIVINAMENTE_DIR + "/cover.jpg", "rb").read()).decode("ascii")

_MUNDOESPIRITUAL_DIR = "/home/claude/estudo-teologia/build/mundoespiritual"
mundoespiritual_pages = open(_MUNDOESPIRITUAL_DIR + "/pages_mundoespiritual.html", encoding="utf-8").read()
mundoespiritual_toc = json.load(open(_MUNDOESPIRITUAL_DIR + "/toc_mundoespiritual.json", encoding="utf-8"))
mundoespiritual_cover_b64 = base64.b64encode(open(_MUNDOESPIRITUAL_DIR + "/cover.jpg", "rb").read()).decode("ascii")


def build_pdf_book(d):
    """Turn one manifest entry (a PDF rendered page-by-page to JPEGs) into its
    <div id="book-..."> markup plus the small JS-facing dict for its cover.
    Shared by the "No Secreto" devotionals and the general "Livros" shelf --
    both are just a PDF flipped page by page, one image per page."""
    title_esc = htmlmod.escape(d["title"], quote=True)
    n = len(d["pages"])
    # StPageFlip's showCover forces page 0 hard, and also forces the LAST page
    # hard-alone whenever the page count after the cover is odd (n-1 odd, i.e. n even).
    # Give those genuine hardcover pages the same bevel/vignette/grain frame as the
    # theology books' cover-page, so every hard "capa" (front and, where it exists, back)
    # gets the hardcover look.
    last_is_cover = (n % 2 == 0)
    pages_markup = "".join(
        '<div class="page devo-page%s"><img src="data:image/jpeg;base64,%s" alt="%s, pagina %d" draggable="false"></div>\n'
        % (
            " devo-cover" if (i == 0 or (last_is_cover and i == n - 1)) else "",
            p, title_esc, i + 1,
        )
        for i, p in enumerate(d["pages"])
    )
    book_html = (
        '<div id="book-%s" class="stbook devo-book" data-theme="devo">\n%s</div>\n'
        % (d["id"], pages_markup)
    )
    book_js = {
        "id": d["id"],
        "title": d["title"],
        "subtitle": d["subtitle"],
        "pageCount": d["pageCount"],
        "cover": d["pages"][0],
    }
    return book_html, book_js


# ---- build the 3 "No Secreto" devotional books (each PDF page -> one flipbook page) ----
devo_books_html = ""
devos_js = []
for d in devo_manifest:
    html_part, js_part = build_pdf_book(d)
    devo_books_html += html_part
    devos_js.append(js_part)

# ---- build the real books on the "Livros" shelf (same PDF-to-flipbook pipeline) ----
livro_books_html = ""
livros_js = []
for d in livros_manifest:
    html_part, js_part = build_pdf_book(d)
    livro_books_html += html_part
    livros_js.append(js_part)

CSS = r"""
:root{
  --umber:#170f09;
  --umber2:#241a10;
  --umber3:#332415;
  --paper:#f3e7c9;
  --paper2:#e8d6a6;
  --ink:#2b2117;
  --navy:#241a10;
  --navy2:#3a2a18;
  --gold:#a97c2f;
  --gold-soft:#d9b968;
  --rust:#8a2a1c;
  --rust-deep:#4a170f;
  --teal:#3c5b48;
  --teal-deep:#1f3328;
  --plum:#5c3a5e;
  --plum-deep:#2c1c30;
  --azure:#2c4a6e;
  --azure-deep:#14202f;
  --terracotta:#b5541f;
  --terracotta-deep:#3d1c0c;
  --slate:#3f5566;
  --slate-deep:#161f26;
  --wine:#6b1f3a;
  --wine-deep:#280b16;
  --muted:#6b5a42;
  --line:rgba(43,33,23,.16);
  --shadow:0 18px 50px rgba(20,14,8,.35);
  --hdrH:96px;
}
@media(max-width:600px){:root{--hdrH:76px}}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{
  font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  background:var(--umber);
  color:var(--ink);
  min-height:100%;height:100dvh;overflow:hidden;
  -webkit-font-smoothing:antialiased;
}

#bar{position:fixed;top:0;left:0;height:3px;width:0;background:linear-gradient(90deg,var(--gold),var(--gold-soft));z-index:50;transition:width .35s ease;box-shadow:0 0 12px rgba(169,124,47,.55)}
#counter{position:fixed;top:16px;right:22px;z-index:40;color:#f0e2bc;font-size:13px;letter-spacing:.14em;font-family:"Helvetica Neue",Arial,sans-serif;opacity:.85}
#menuBtn{position:fixed;top:13px;z-index:40;background:rgba(243,231,201,.08);border:1px solid rgba(217,185,104,.28);color:#f0e2bc;border-radius:9px;padding:7px 12px;font-size:12px;letter-spacing:.12em;cursor:pointer;font-family:"Helvetica Neue",Arial,sans-serif;backdrop-filter:blur(6px);display:none}
#menuBtn:hover{background:rgba(243,231,201,.16)}
#menuBtn{right:120px}
#topLeftBtns{position:fixed;top:13px;left:20px;z-index:40;display:none;gap:8px}
#topLeftBtns.show{display:flex}
#backBtn,#homeBtn{background:rgba(243,231,201,.08);border:1px solid rgba(217,185,104,.28);color:#f0e2bc;border-radius:9px;padding:7px 12px;font-size:12px;letter-spacing:.12em;cursor:pointer;font-family:"Helvetica Neue",Arial,sans-serif;backdrop-filter:blur(6px)}
#backBtn:hover,#homeBtn:hover{background:rgba(243,231,201,.16)}
@media(max-width:600px){#menuBtn{right:92px}#backBtn,#homeBtn{font-size:11px;padding:6px 10px}}

/* ---- corner sound toggle (always visible, independent of reader/shelf state) ---- */
#sfxBtn{position:fixed;bottom:16px;right:16px;z-index:60;background:rgba(243,231,201,.08);border:1px solid rgba(217,185,104,.28);color:#f0e2bc;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;font-size:16px;cursor:pointer;backdrop-filter:blur(6px);transition:.18s;position:fixed}
#sfxBtn:hover{background:rgba(217,185,104,.22);border-color:var(--gold)}
#sfxBtn.off{opacity:.5}
#sfxBtn::before{content:"";position:absolute;left:8px;right:8px;top:50%;height:1.5px;background:#f0e2bc;transform:rotate(-40deg) scaleX(0);border-radius:2px;transition:transform .15s ease;transform-origin:center}
#sfxBtn.off::before{transform:rotate(-40deg) scaleX(1)}
@media(max-width:600px){#sfxBtn{width:34px;height:34px;font-size:14px;bottom:12px;right:12px}}

/* ---- background-music button + picker panel (also always visible) ---- */
#musicBtn{position:fixed;bottom:16px;right:64px;z-index:60;background:rgba(243,231,201,.08);border:1px solid rgba(217,185,104,.28);color:#f0e2bc;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;font-size:16px;cursor:pointer;backdrop-filter:blur(6px);transition:.18s}
#musicBtn:hover{background:rgba(217,185,104,.22);border-color:var(--gold)}
#musicBtn.playing{border-color:var(--gold);color:var(--gold)}
@media(max-width:600px){#musicBtn{width:34px;height:34px;font-size:14px;bottom:12px;right:56px}}
#musicPanel{position:fixed;bottom:64px;right:16px;z-index:61;background:rgba(20,14,8,.94);border:1px solid rgba(217,185,104,.28);border-radius:12px;padding:14px;width:240px;backdrop-filter:blur(10px);display:none;box-shadow:0 20px 40px rgba(0,0,0,.5);font-family:"Helvetica Neue",Arial,sans-serif}
#musicPanel.open{display:block}
#musicPanel h5{margin:0 0 10px;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#c9b98f;font-weight:600}
#musicPanel .track{display:flex;align-items:center;gap:8px;padding:6px 8px;border-radius:6px;cursor:pointer;font-size:12.5px;color:#f0e2bc;transition:.15s}
#musicPanel .track:hover{background:rgba(217,185,104,.12)}
#musicPanel .track.active{background:rgba(217,185,104,.2);color:var(--gold)}
#musicPanel .track .dot{width:6px;height:6px;border-radius:50%;background:rgba(240,226,188,.3);flex:none}
#musicPanel .track.active .dot{background:var(--gold)}
#musicPanel .empty{font-size:12px;color:#a08f6a;line-height:1.5}
#musicPanel .empty code{background:rgba(240,226,188,.1);padding:1px 4px;border-radius:3px}
#musicPanel .vol-row{margin-top:12px;padding-top:12px;border-top:1px solid rgba(217,185,104,.15);display:flex;align-items:center;gap:8px}
#musicPanel .vol-row span{font-size:13px;opacity:.8}
#musicPanel input[type=range]{flex:1;accent-color:var(--gold)}
@media(max-width:600px){#musicPanel{right:12px;bottom:56px;width:210px}}

/* ---- content styling (reused verbatim by all extracted page markup) ---- */
.kicker{font-family:"Helvetica Neue",Arial,sans-serif;font-size:11.5px;letter-spacing:.24em;text-transform:uppercase;color:var(--rust);font-weight:700;margin-bottom:12px;display:flex;align-items:center;gap:10px}
.kicker .u{background:var(--navy);color:#f3ead0;border-radius:6px;padding:3px 9px;font-size:11px;letter-spacing:.14em}
h1{font-size:clamp(24px,4vw,38px);line-height:1.1;color:var(--navy);font-weight:700;letter-spacing:-.01em}
h2{font-size:clamp(20px,2.6vw,27px);line-height:1.16;color:var(--navy);margin-bottom:6px;font-weight:700}
.lead{font-size:15.5px;color:var(--muted);margin-top:10px;line-height:1.5}
.lead::first-letter{float:left;font-family:"Iowan Old Style",Georgia,serif;font-size:2.5em;line-height:.78;padding:.04em .09em 0 0;color:var(--rust);font-weight:700}
.rule{height:2px;width:46px;background:linear-gradient(90deg,var(--gold),var(--rust));border-radius:3px;margin:12px 0 16px}

p{font-size:14.5px;line-height:1.56;color:var(--ink);margin-bottom:10px}
p strong{color:var(--navy2)}
em{color:var(--rust);font-style:italic}

.grid{display:grid;gap:10px;margin-top:6px}
.g2{grid-template-columns:1fr 1fr}
.g3{grid-template-columns:1fr 1fr}
@media(max-width:520px){.g2,.g3{grid-template-columns:1fr}}

.card{background:rgba(43,33,23,.05);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.card h3{font-size:13.5px;color:var(--navy);margin-bottom:4px;font-family:"Helvetica Neue",Arial,sans-serif;letter-spacing:.01em}
.card p{font-size:12.5px;line-height:1.44;color:var(--ink);margin:0}
.card .tag{font-family:"Helvetica Neue",Arial,sans-serif;font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--rust);font-weight:700;display:block;margin-bottom:3px}

ul.clean{list-style:none;margin:6px 0 4px}
ul.clean li{position:relative;padding-left:20px;font-size:14px;line-height:1.5;color:var(--ink);margin-bottom:7px}
ul.clean li::before{content:"";position:absolute;left:3px;top:9px;width:6px;height:6px;border-radius:50%;background:var(--gold);box-shadow:0 0 0 3px rgba(169,124,47,.16)}
ul.clean li b{color:var(--navy2)}

.heb{font-family:"Helvetica Neue",Arial,sans-serif}
.term{display:inline-block;background:var(--rust);color:#f6ecd6;border-radius:999px;padding:2px 10px;font-size:11.5px;margin:3px 4px 3px 0;font-family:"Helvetica Neue",Arial,sans-serif;letter-spacing:.02em}
.term.alt{background:var(--teal)}
.term.r{background:var(--navy)}

.verse{background:var(--navy);color:#f1e4c4;border-radius:10px;padding:14px 16px;margin:12px 0;font-size:14px;line-height:1.5;position:relative;box-shadow:0 8px 18px rgba(20,14,8,.28)}
.verse .ref{display:block;margin-top:6px;font-family:"Helvetica Neue",Arial,sans-serif;font-size:10.5px;letter-spacing:.14em;color:var(--gold-soft);text-transform:uppercase}

.chain{display:flex;flex-wrap:wrap;align-items:stretch;gap:8px;margin-top:10px}
.chain .step{flex:1;min-width:100px;background:rgba(43,33,23,.045);border:1px solid var(--line);border-top:3px solid var(--gold);border-radius:9px;padding:9px 10px}
.chain .step b{display:block;color:var(--navy);font-size:12.5px;font-family:"Helvetica Neue",Arial,sans-serif}
.chain .step span{font-size:11.5px;color:var(--muted);line-height:1.35}

.pill{font-family:"Helvetica Neue",Arial,sans-serif;font-size:11px;color:var(--teal);font-weight:700;letter-spacing:.04em}

.hint{font-family:"Helvetica Neue",Arial,sans-serif;font-size:11px;color:var(--muted);margin-top:16px;letter-spacing:.03em}
.footnote{font-family:"Helvetica Neue",Arial,sans-serif;font-size:10.5px;color:var(--muted);margin-top:14px;letter-spacing:.02em;border-top:1px dashed var(--line);padding-top:9px}
.units{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:18px}
.units span{border:1px solid rgba(217,185,104,.4);border-radius:999px;padding:5px 12px;font-size:11.5px;font-family:"Helvetica Neue",Arial,sans-serif;color:var(--gold-soft)}
.meta{font-family:"Helvetica Neue",Arial,sans-serif;font-size:11.5px;letter-spacing:.05em;color:#c9b98f;margin-top:20px;line-height:1.7}

/* ---- book page chrome ---- */
.page{background:linear-gradient(155deg,var(--paper) 0%,var(--paper2) 100%);overflow:hidden;position:relative}
.page-inner{position:absolute;inset:0;padding:7% 8% 11%;overflow-y:auto;user-select:text;-webkit-user-select:text}
.page-inner::-webkit-scrollbar{width:7px}
.page-inner::-webkit-scrollbar-thumb{background:rgba(43,33,23,.2);border-radius:9px}
.pagehead{font-family:"Helvetica Neue",Arial,sans-serif;font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:10px;font-style:italic;opacity:.85}
.folio{position:absolute;bottom:10px;font-family:"Helvetica Neue",Arial,sans-serif;font-size:9.5px;color:var(--muted);opacity:.65;letter-spacing:.06em}
.page:nth-child(odd) .folio{right:16px}
.page:nth-child(even) .folio{left:16px}

.cover-page{background:none;box-shadow:
    inset 0 0 0 1px rgba(0,0,0,.3),
    inset 0 0 0 8px rgba(0,0,0,.16),
    inset 0 0 0 9px rgba(217,185,104,.4),
    inset 0 0 0 11px rgba(0,0,0,.16),
    inset 0 3px 22px rgba(0,0,0,.4),
    inset 0 -3px 26px rgba(0,0,0,.5)}
.cover-page::before{content:"";position:absolute;inset:0;pointer-events:none;z-index:0;
  background:
    linear-gradient(100deg, rgba(0,0,0,.4) 0%, rgba(0,0,0,.08) 4%, transparent 9%, transparent 91%, rgba(255,255,255,.08) 96%, rgba(0,0,0,.3) 100%),
    linear-gradient(180deg, rgba(255,255,255,.14) 0%, transparent 10%, transparent 82%, rgba(0,0,0,.35) 100%),
    radial-gradient(120% 90% at 50% 45%, transparent 45%, rgba(0,0,0,.34) 100%)}
.cover-page::after{content:"";position:absolute;inset:0;pointer-events:none;z-index:2;opacity:.16;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix type='matrix' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .9 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size:140px 140px}
.cover-page .page-inner{z-index:1;text-align:center;display:flex;flex-direction:column;justify-content:center;color:#f3ead0;overflow:visible}
.cover-page .page-inner::before{content:"";position:absolute;inset:16px;pointer-events:none;border:1px solid rgba(217,185,104,.38);
  box-shadow:inset 0 0 0 3px rgba(0,0,0,.14)}
__THEOLOGY_COVER_CSS__
.cover-page .kicker{color:var(--gold-soft);justify-content:center}
.cover-page h1{font-size:clamp(26px,5vw,40px);
  background:linear-gradient(180deg,#fbf3da 0%,#e9d295 42%,#c9a34e 56%,#f6e7bd 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  /* text-shadow, not filter:drop-shadow -- a filter forces the browser to
     re-rasterize this element every frame, and during the cover's fast
     rotateY hard-page flip that re-raster can lag a frame behind the page's
     own transform, so the gold text visibly drifts past the page edge
     ("corta as extremidades"). text-shadow paints from the glyph outlines
     directly (works fine even with color:transparent) at no extra cost. */
  text-shadow:0 1px 0 rgba(255,255,255,.3), 0 3px 5px rgba(0,0,0,.55)}
.cover-page .lead{color:#e7d9b6}
.cover-page .rule{margin:14px auto 18px;background:linear-gradient(90deg,transparent,var(--gold-soft),transparent)}
.cover-page .hint{color:#c9b98f}

/* ---- devotional pages (image-only, one PDF page per flipbook page) ---- */
.devo-page{background:#0c0804}
.devo-page img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;user-select:none;-webkit-user-select:none;-webkit-user-drag:none}

/* hardcover frame for devo front/back covers (real StPageFlip hard-density pages) --
   same bevel + vignette + grain language as .cover-page, kept as overlays so the
   photo underneath still shows through (no solid background, no heading styles) */
.devo-cover{box-shadow:
    inset 0 0 0 1px rgba(0,0,0,.3),
    inset 0 0 0 8px rgba(0,0,0,.16),
    inset 0 0 0 9px rgba(217,185,104,.4),
    inset 0 0 0 11px rgba(0,0,0,.16),
    inset 0 3px 22px rgba(0,0,0,.4),
    inset 0 -3px 26px rgba(0,0,0,.5)}
.devo-cover::before{content:"";position:absolute;inset:0;pointer-events:none;z-index:1;
  background:
    linear-gradient(100deg, rgba(0,0,0,.4) 0%, rgba(0,0,0,.08) 4%, transparent 9%, transparent 91%, rgba(255,255,255,.08) 96%, rgba(0,0,0,.3) 100%),
    linear-gradient(180deg, rgba(255,255,255,.14) 0%, transparent 10%, transparent 82%, rgba(0,0,0,.35) 100%),
    radial-gradient(120% 90% at 50% 45%, transparent 45%, rgba(0,0,0,.34) 100%)}
.devo-cover::after{content:"";position:absolute;inset:0;pointer-events:none;z-index:2;opacity:.16;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix type='matrix' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .9 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size:140px 140px}
/* the photo itself stays full-bleed (same rule as any .devo-page img) -- the
   frame is only ever painted ON TOP as box-shadow/pseudo-element overlays,
   never by resizing the image, because a resized child does not track the
   hard page's rotateY the way the parent's own paint layers do: mid-flip it
   opened a growing gap between the shrunken photo and the frame around it,
   which read as the cover "cutting" at the edges. */

/* ---- full-bleed illustration pages ("Divinamente" and any future rich
   Livros book) -- same borderless photo treatment as .devo-page, plus a
   small caption pill so the chapter number survives without a text box */
.art-page{position:relative}
.art-page .art-cap{position:absolute;bottom:14px;right:16px;font-family:"Helvetica Neue",Arial,sans-serif;font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:#e7d9b6;background:rgba(12,8,4,.55);padding:5px 10px;border-radius:999px;backdrop-filter:blur(3px)}

/* ---- index overlay (unit jump menu) ---- */
#idx{position:fixed;inset:0;background:rgba(15,10,6,.88);backdrop-filter:blur(8px);z-index:60;display:none;padding:60px 24px;overflow:auto}
#idx.open{display:block}
#idx .wrap{max-width:760px;margin:0 auto}
#idx h4{color:var(--gold-soft);font-family:"Helvetica Neue",Arial,sans-serif;letter-spacing:.2em;font-size:13px;text-transform:uppercase;margin:22px 0 10px}
#idx .item{display:flex;gap:14px;align-items:baseline;color:#f0e2bc;padding:9px 12px;border-radius:9px;cursor:pointer;border:1px solid transparent}
#idx .item:hover{background:rgba(243,231,201,.08);border-color:rgba(217,185,104,.2)}
#idx .item .n{font-family:"Helvetica Neue",Arial,sans-serif;font-size:12px;color:var(--gold-soft);width:26px;flex:none}
#idx .item .t{font-size:15px}
#idx .close{position:fixed;top:18px;right:24px;color:#f0e2bc;font-size:26px;cursor:pointer;font-family:Arial}

/* ---- notes side panel (per-book, docked, never blocks the book) ---- */
#notesBtn{position:fixed;top:13px;right:246px;z-index:40;background:rgba(243,231,201,.08);border:1px solid rgba(217,185,104,.28);color:#f0e2bc;border-radius:9px;padding:7px 12px;font-size:12px;letter-spacing:.12em;cursor:pointer;font-family:"Helvetica Neue",Arial,sans-serif;backdrop-filter:blur(6px);display:none}
#notesBtn:hover{background:rgba(243,231,201,.16)}
#notesBtn.has-note::after{content:"";position:absolute;top:6px;right:6px;width:6px;height:6px;border-radius:50%;background:var(--gold-soft)}
@media(max-width:600px){#notesBtn{right:190px;font-size:11px;padding:6px 10px}}
@media(min-width:1000px){body.notes-open .reader-slot{transform:translateX(-160px)}}
.reader-slot{transition:transform .32s ease}
#notesPanel{position:fixed;top:0;right:0;height:100dvh;width:min(400px,92vw);z-index:65;background:var(--paper);box-shadow:-18px 0 40px rgba(20,14,8,.45);transform:translateX(100%);transition:transform .32s ease;display:flex;flex-direction:column;font-family:"Helvetica Neue",Arial,sans-serif}
#notesPanel.open{transform:translateX(0)}
#notesPanel .notes-head{background:rgba(20,14,8,.94);border-bottom:1px solid rgba(217,185,104,.28);backdrop-filter:blur(10px);flex:none}
#notesPanel .notes-head-top{display:flex;align-items:center;gap:8px;padding:12px 14px 8px}
#notesPanel .notes-title{color:#f0e2bc;font-size:12.5px;letter-spacing:.1em;text-transform:uppercase;font-weight:600;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#notesPanel .notes-status{color:#a08f6a;font-size:11px;opacity:0;transition:opacity .25s}
#notesPanel .notes-status.show{opacity:1}
#notesPanel .notes-close{color:#f0e2bc;font-size:20px;cursor:pointer;line-height:1;padding:2px 4px}
#notesPanel .notes-close:hover{color:var(--gold-soft)}
#notesPanel .notes-toolbar{display:flex;flex-wrap:wrap;gap:6px;padding:0 14px 12px}
#notesPanel .toolbtn{background:rgba(243,231,201,.08);border:1px solid rgba(217,185,104,.28);color:#f0e2bc;border-radius:7px;padding:5px 9px;font-size:12px;cursor:pointer;font-family:"Helvetica Neue",Arial,sans-serif}
#notesPanel .toolbtn:hover{background:rgba(243,231,201,.16)}
#notesPanel .toolbtn.active{background:rgba(217,185,104,.28);border-color:var(--gold-soft);color:var(--gold-soft)}
#notesPanel .toolbar-sep{width:1px;background:rgba(217,185,104,.28);margin:2px 2px}
#notesBody{flex:1;overflow-y:auto;padding:18px 22px 18px 46px;font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;font-size:15px;line-height:27px;color:var(--ink);outline:none;background-color:var(--paper);background-attachment:local;background-image:linear-gradient(90deg,transparent 28px,rgba(139,48,48,.24) 28px,rgba(139,48,48,.24) 29px,transparent 29px),repeating-linear-gradient(to bottom,transparent 0,transparent 25px,rgba(43,33,23,.16) 25px,rgba(43,33,23,.16) 26px)}
#notesBody:empty::before{content:attr(data-placeholder);color:rgba(43,33,23,.4)}
#notesBody h2{font-size:19px;line-height:27px;color:var(--rust);margin:0;font-weight:700}
#notesBody h3{font-size:16px;line-height:27px;color:var(--navy2);margin:0;font-weight:700}
#notesBody p{font-size:15px;line-height:27px;color:var(--ink);margin:0}
#notesBody::-webkit-scrollbar{width:9px}
#notesBody::-webkit-scrollbar-thumb{background:rgba(139,124,47,.35);border-radius:5px}
#notesBody::-webkit-scrollbar-track{background:transparent}
@media(max-width:600px){#notesPanel{width:100vw}#notesBody{padding:16px 16px 16px 38px}}

/* ---- reader stage (StPageFlip) — the book resting on a real painted wooden table.
   The container's aspect-ratio is locked to the exact spread aspect (920:640) that
   StPageFlip's own 'stretch' sizing computes internally, so the two can never drift
   apart and the page content can never overflow/get clipped at odd viewport shapes. */
#reader{position:fixed;inset:0;z-index:5;display:none;flex-direction:column;align-items:center;justify-content:center;opacity:0;transition:opacity .35s ease;
  background:
    linear-gradient(180deg, rgba(10,7,4,.28) 0%, rgba(10,7,4,.5) 55%, rgba(10,7,4,.76) 100%),
    url(data:image/jpeg;base64,__TABLE_ART__) center/cover no-repeat;
}
#reader.show{display:flex}
#reader.shown{opacity:1}
/* .reader-slot is the book's fixed footprint on the table: always the full
   double-page size, always centered, never resized — StPageFlip measures its
   container once and does not react to it being resized by CSS alone (no
   resize event fires), so .reader-stage itself must never change size once
   the book is built, or its rendering breaks. A lone page (front/back cover)
   simply occupies the right half, same as always; the left half is left
   transparent so the table underneath shows through, matching what a single
   leaf really looks like — not a page, so no visible box. */
.reader-slot{position:relative;width:min(94vw, calc(82dvh * 1.4375));aspect-ratio:920/640}
/* The book's drop shadow lives on each page's own stf__item box, not on
   .reader-slot -- .reader-slot is always sized for a full double-page
   spread (StPageFlip needs that fixed footprint, see note below), but a
   lone hard cover only ever fills HALF of it. A shadow cast from the full
   slot used to spill into that empty half as a ghost page-shaped shadow
   with nothing above it. Casting it from the page itself means a single
   cover only ever throws a shadow the size of the cover, and two facing
   pages in a normal spread still add up to one continuous shadow since
   they sit edge to edge with no gap.
   box-shadow, not filter:drop-shadow -- each stf__item is always a plain
   rectangle, so a box-shadow looks identical here but is computed purely
   from the box's geometry. filter:drop-shadow instead has to re-rasterize
   this element's ENTIRE subtree (every frame) to trace its silhouette,
   and that per-frame re-raster of everything inside is what was lagging
   a frame behind a hard cover's own fast rotateY transform -- the actual
   cause of covers visibly "cutting" mid-flip. */
.reader-stage .stf__item{box-shadow:0 46px 70px rgba(0,0,0,.6)}
.reader-slot::after{content:"";position:absolute;left:6%;right:6%;bottom:-26px;height:26px;border-radius:50%;
  background:radial-gradient(closest-side, rgba(0,0,0,.5), transparent 75%);z-index:-1}
.reader-stage{position:absolute;inset:0;overflow:hidden;border-radius:2px}
/* While a flip is actually animating, the flipping leaf can briefly become
   edge-on (a real hardcover swings rigidly, it doesn't bend) — fill the
   stage with the same paper color as the pages so that instant shows a
   plain, book-colored gap instead of a hole into the background behind.
   The moment it settles back to rest, this goes transparent again. */
.reader-stage.flip-live{background:linear-gradient(155deg,var(--paper) 0%,var(--paper2) 100%)}
.stbook{width:100%;height:100%;display:none}
.stbook.active{display:block}
.reader-hint{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);z-index:40;font-family:"Helvetica Neue",Arial,sans-serif;font-size:11px;color:#c9b98f;letter-spacing:.06em;opacity:.75;display:none}
#reader.show ~ .reader-hint{display:block}
.flipbtn{position:fixed;top:50%;transform:translateY(-50%);z-index:40;background:rgba(243,231,201,.08);border:1px solid rgba(217,185,104,.28);color:#f0e2bc;width:42px;height:56px;border-radius:10px;font-size:18px;cursor:pointer;backdrop-filter:blur(6px);transition:.18s;display:none}
.flipbtn:hover{background:rgba(217,185,104,.22);border-color:var(--gold)}
#reader.show ~ .flipbtn{display:block}
#flipPrev{left:14px}
#flipNext{right:14px}
@media(max-width:640px){.flipbtn{width:34px;height:46px;font-size:15px}}

/* ============ header (persists across landing + corridor) ============ */
#shelf{height:100dvh;width:100%;display:none;overflow:hidden}
#shelf.show{display:flex;flex-direction:column}

#libHeader{height:var(--hdrH);flex:none;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;
  background:linear-gradient(180deg,#1c130b 0%,#150e08 85%);border-bottom:1px solid rgba(217,185,104,.18);position:relative;z-index:3;padding:4px 16px}
.hdr-title{color:#f6ecd6;font-size:clamp(19px,3vw,28px);font-weight:700;letter-spacing:-.01em;font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;text-shadow:0 6px 22px rgba(0,0,0,.5)}
.hdr-verse{font-family:"Helvetica Neue",Arial,sans-serif;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold-soft);opacity:.8}
@media(max-width:600px){.hdr-verse{font-size:9px}}

/* ============ viewport: landing (corridor picker) <-> corridor (frontal shelf) ============ */
#viewport{flex:1;min-height:0;position:relative;overflow:hidden}
.view{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;opacity:1;transform:scale(1);
  transition:opacity .48s ease, transform .48s ease}
.view.show{display:flex}
.view.leaving{opacity:0;transform:scale(1.07)}
.view.entering-from{opacity:0;transform:scale(1.05)}

.hall-area{width:100%;height:100%;display:flex;align-items:center;justify-content:center;padding:14px 16px 20px}
.hall-art{position:relative;width:100%;height:100%;
  container-type:inline-size;border-radius:6px;overflow:hidden;box-shadow:0 30px 90px rgba(0,0,0,.65)}
.hall-art img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;user-select:none;pointer-events:none}

.hall-picks{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:clamp(14px,3.2cqw,46px);padding:0 4cqw;z-index:2}
.corridor-zone{position:relative;cursor:pointer;display:flex;flex-direction:column;align-items:center;justify-content:center;outline:none}
.corridor-zone .placard-hang{position:relative;overflow:hidden;display:flex;align-items:center;gap:clamp(9px,1cqw,15px);
  background:linear-gradient(180deg,#2b1c0eee,#140d05ee);border:1.5px solid rgba(217,185,104,.42);border-radius:clamp(9px,.9cqw,15px);
  padding:clamp(15px,1.6cqw,26px) clamp(22px,2.6cqw,40px);
  font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;font-size:clamp(15px,1.5cqw,25px);letter-spacing:.04em;color:var(--gold-soft);
  font-weight:700;box-shadow:0 .8cqw 2cqw rgba(0,0,0,.55);white-space:nowrap;
  transition:transform .32s cubic-bezier(.2,.8,.25,1),box-shadow .32s ease,border-color .32s ease}
.corridor-zone .placard-hang::before{content:"";position:absolute;top:0;left:-60%;width:40%;height:100%;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.22),transparent);transform:skewX(-18deg);transition:left .6s ease}
.corridor-zone:hover .placard-hang,.corridor-zone:focus-visible .placard-hang{
  transform:translateY(-.4cqw) scale(1.09);border-color:rgba(217,185,104,.85);
  box-shadow:0 1.5cqw 3.2cqw rgba(0,0,0,.65),0 0 0 1px rgba(217,185,104,.35),0 0 2.6cqw rgba(217,185,104,.28)}
.corridor-zone:hover .placard-hang::before,.corridor-zone:focus-visible .placard-hang::before{left:130%}
.corridor-zone .placard-hang .n{display:inline-flex;align-items:center;justify-content:center;flex:none;
  width:clamp(21px,2cqw,32px);height:clamp(21px,2cqw,32px);border-radius:50%;border:1px solid rgba(217,185,104,.5);
  font-size:clamp(11px,.95cqw,16px);opacity:.85}
.corridor-zone .enter-cue{margin-top:clamp(7px,.8cqw,12px);font-family:"Helvetica Neue",Arial,sans-serif;font-size:clamp(10px,.85cqw,14px);letter-spacing:.1em;color:#c9b98f;
  text-transform:uppercase;opacity:0;transform:translateY(-3px);transition:opacity .25s ease,transform .25s ease}
.corridor-zone:hover .enter-cue,.corridor-zone:focus-visible .enter-cue{opacity:.9;transform:translateY(0)}
@media(max-width:640px){
  .hall-picks{flex-direction:column;gap:16px;padding:0 24px}
}

/* ============ inside a corridor: frontal shelf, front-facing book covers ============ */
.corridorExitBtn{position:absolute;top:calc(var(--hdrH) + 14px);left:16px;z-index:6;background:rgba(243,231,201,.08);border:1px solid rgba(217,185,104,.28);
  color:#f0e2bc;border-radius:9px;padding:7px 14px;font-size:12px;letter-spacing:.1em;cursor:pointer;font-family:"Helvetica Neue",Arial,sans-serif;backdrop-filter:blur(6px)}
.corridorExitBtn:hover{background:rgba(243,231,201,.16)}
.corridor-area{width:100%;height:100%;display:flex;align-items:center;justify-content:center;padding:14px 16px 20px}
.corridor-stage{position:relative;width:100%;height:100%;
  container-type:inline-size;border-radius:6px;overflow:hidden;box-shadow:0 30px 90px rgba(0,0,0,.65)}
.corridor-stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;user-select:none;pointer-events:none}
.corridor-tint{position:absolute;inset:0;pointer-events:none;mix-blend-mode:multiply;opacity:.5}
.corridor-tint.t-teologia{background:radial-gradient(80% 70% at 50% 30%, transparent 30%, rgba(138,42,28,.35))}
.corridor-tint.t-secreto{background:radial-gradient(80% 70% at 50% 30%, transparent 30%, rgba(60,91,72,.35))}
.corridor-tint.t-livros{background:radial-gradient(80% 70% at 50% 30%, transparent 30%, rgba(169,124,47,.35))}

.corridor-heading{position:absolute;top:5%;left:50%;transform:translateX(-50%);text-align:center;z-index:2}
.corridor-heading .n{display:block;font-family:"Helvetica Neue",Arial,sans-serif;font-size:clamp(9px,.9cqw,15px);letter-spacing:.3em;color:var(--gold-soft);opacity:.75;margin-bottom:.3em}
.corridor-heading h2{color:#f6ecd6;font-size:clamp(17px,2.1cqw,34px);font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;font-weight:700;text-shadow:0 6px 20px rgba(0,0,0,.6)}

.cshelf{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);display:flex;flex-wrap:wrap;gap:clamp(10px,1.6cqw,26px);
  align-items:center;justify-content:center;max-width:88%;z-index:2}

.bcover{position:relative;width:clamp(100px,9.6cqw,190px);aspect-ratio:11/15.4;cursor:pointer;border-radius:4px;overflow:hidden;outline:none;
  box-shadow:0 1cqw 2.2cqw rgba(0,0,0,.55);transition:transform .25s cubic-bezier(.2,.8,.3,1), box-shadow .25s ease;
  display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:9% 8%;
  background:radial-gradient(120% 140% at 50% 0%,var(--rust) 0%,var(--rust-deep) 72%);border:1px solid rgba(217,185,104,.25)}
__THEOLOGY_BCOVER_CSS__
.bcover:hover,.bcover:focus-visible{transform:scale(1.1) translateY(-.5cqw);box-shadow:0 1.7cqw 3.2cqw rgba(0,0,0,.65),0 0 0 2px rgba(217,185,104,.55)}
.bc-orn{color:var(--gold-soft);font-size:clamp(13px,1.3cqw,22px);margin-bottom:.5em}
.bc-title{color:#f6ecd6;font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;font-weight:700;font-size:clamp(12px,1.05cqw,20px);line-height:1.28}
.bc-rule{width:26%;height:2px;background:var(--gold-soft);margin:.6em auto;opacity:.8}
.bc-prof{color:#d9c79c;font-size:clamp(9.5px,.72cqw,13px);font-family:"Helvetica Neue",Arial,sans-serif}

.bcover.placeholder{cursor:default;opacity:.42;background:rgba(20,14,8,.4);border:1.5px dashed rgba(217,185,104,.32)}
.bcover.placeholder:hover{transform:none;box-shadow:none}
.bcover.placeholder .bc-title{font-family:"Helvetica Neue",Arial,sans-serif;font-weight:600;font-size:clamp(10.5px,.86cqw,15px);color:#c9b98f}

.bcover.devo{padding:0;background:#0c0804}
.bcover.devo img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}

.flying-cover{pointer-events:none}

.motes{position:fixed;inset:0;z-index:1;pointer-events:none;overflow:hidden}
.motes span{position:absolute;width:3px;height:3px;border-radius:50%;background:var(--gold-soft);opacity:.3;filter:blur(.3px);animation:drift 9s ease-in-out infinite}
.motes span:nth-child(1){left:18%;top:70%;animation-delay:0s}
.motes span:nth-child(2){left:42%;top:30%;animation-delay:1.6s}
.motes span:nth-child(3){left:68%;top:60%;animation-delay:3.1s}
.motes span:nth-child(4){left:82%;top:22%;animation-delay:4.4s}
.motes span:nth-child(5){left:28%;top:15%;animation-delay:5.7s}
@keyframes drift{0%,100%{transform:translateY(0);opacity:.12}50%{transform:translateY(-26px);opacity:.5}}

@media(max-width:600px){
  #counter{top:14px;right:14px;font-size:11px}
}
"""

# fill in the per-book cover CSS generated from THEOLOGY_BOOKS before CSS
# gets baked into HEAD below -- must happen here, not near the bottom of
# the file, or HEAD would capture the unresolved __THEOLOGY_..._CSS__ text.
theology_cover_css = "\n".join(
    "#book-%s .cover-page{background:radial-gradient(120%% 140%% at 50%% 0%%,%s 0%%,%s 72%%)}"
    % (b["id"], b["cover_a"], b["cover_b"])
    for b in THEOLOGY_BOOKS
)
theology_bcover_css = "\n".join(
    ".bcover.%s{background:radial-gradient(120%% 140%% at 50%% 0%%,%s 0%%,%s 72%%)}"
    % (b["theme"], b["cover_a"], b["cover_b"])
    for b in THEOLOGY_BOOKS
)
CSS = CSS.replace("__THEOLOGY_COVER_CSS__", theology_cover_css).replace("__THEOLOGY_BCOVER_CSS__", theology_bcover_css)

HALL_HTML = """
<section id="shelf" class="show">
  <header id="libHeader">
    <h1 class="hdr-title">Biblioteca de Estudos</h1>
    <div class="hdr-verse">Colossenses 3:23-24</div>
  </header>

  <div id="viewport">
    <div id="viewLanding" class="view show">
      <div class="hall-area">
        <div class="hall-art">
          <img src="data:image/jpeg;base64,__LANDING_ART__" alt="Uma grande biblioteca antiga com vários andares, escadas em espiral e corredores se perdendo ao fundo" draggable="false">
          <div class="hall-picks">
            <div class="corridor-zone" data-corridor="teologia" tabindex="0" role="button" aria-label="Entrar no corredor Teologia" onclick="enterCorridor('teologia')" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();enterCorridor('teologia')}">
              <div class="placard-hang"><span class="n">1</span>Teologia</div>
              <div class="enter-cue">entrar &#8594;</div>
            </div>
            <div class="corridor-zone" data-corridor="secreto" tabindex="0" role="button" aria-label="Entrar no corredor No Secreto" onclick="enterCorridor('secreto')" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();enterCorridor('secreto')}">
              <div class="placard-hang"><span class="n">2</span>No Secreto</div>
              <div class="enter-cue">entrar &#8594;</div>
            </div>
            <div class="corridor-zone" data-corridor="livros" tabindex="0" role="button" aria-label="Entrar no corredor Livros" onclick="enterCorridor('livros')" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();enterCorridor('livros')}">
              <div class="placard-hang"><span class="n">3</span>Livros</div>
              <div class="enter-cue">entrar &#8594;</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div id="viewCorridor" class="view">
      <button class="corridorExitBtn" onclick="exitCorridor()">&#8592; Corredores</button>
      <div class="corridor-area">
        <div class="corridor-stage">
          <img src="data:image/jpeg;base64,__CORRIDOR_ART__" alt="Estante de biblioteca vista de frente" draggable="false">
          <div class="corridor-tint" id="corridorTint"></div>
          <div class="corridor-heading"><span class="n" id="corridorNum"></span><h2 id="corridorTitle"></h2></div>
          <div class="cshelf" id="corridorBooks"></div>
        </div>
      </div>
    </div>
  </div>
</section>
"""

HEAD = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Biblioteca de Estudos · Xande</title>
<meta name="description" content="Biblioteca viva de resumões de estudo do curso de Teologia. Cada disciplina, um livro na estante.">
<style>""" + CSS + """</style>
</head>
<body>
<script>""" + pageflip_js + """</script>
<div id="bar"></div>
<div id="topLeftBtns">
  <button id="backBtn" onclick="goShelf()">&#8592; Estante</button>
  <button id="homeBtn" onclick="goBookStart()" title="Voltar ao início do livro">&#8607; Início</button>
</div>
<button id="menuBtn" onclick="openIdx()">&#9776; ÍNDICE</button>
<button id="sfxBtn" onclick="toggleSfx()" title="Ativar ou desativar som" aria-label="Ativar ou desativar som">&#9834;</button>
<button id="musicBtn" onclick="toggleMusicPanel()" title="Música de fundo" aria-label="Música de fundo">&#9835;</button>
<div id="musicPanel">
  <h5>Música de fundo</h5>
  <div id="musicTrackList"></div>
  <div class="vol-row"><span>&#128266;</span><input type="range" id="musicVolSlider" min="0" max="100" value="35"></div>
</div>
<div id="counter"></div>

<div class="motes" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div>
""" + HALL_HTML + """

<div id="reader">
  <div class="reader-slot">
  <div class="reader-stage">
"""

TAIL_END = """
  </div>
  </div>
</div>
<button id="flipPrev" class="flipbtn" onclick="flipPrev()">&#8592;</button>
<button id="flipNext" class="flipbtn" onclick="flipNext()">&#8594;</button>
<div class="reader-hint">setas do teclado ou clique na borda da página pra virar</div>

<div id="idx"><span class="close" onclick="closeIdx()">&#10005;</span><div class="wrap" id="idxWrap"></div></div>
<button id="notesBtn" onclick="toggleNotes()" title="Minhas anotações" aria-label="Minhas anotações">&#9998; NOTAS</button>
<div id="notesPanel">
  <div class="notes-head">
    <div class="notes-head-top">
      <span class="notes-title" id="notesTitle">Notas</span>
      <span class="notes-status" id="notesStatus">salvo</span>
      <span class="notes-close" onclick="closeNotes()" title="Fechar anotações">&#10005;</span>
    </div>
    <div class="notes-toolbar">
      <button type="button" class="toolbtn" data-cmd="bold" title="Negrito"><b>N</b></button>
      <button type="button" class="toolbtn" data-cmd="italic" title="Itálico"><i>I</i></button>
      <button type="button" class="toolbtn" data-cmd="underline" title="Sublinhado"><u>S</u></button>
      <span class="toolbar-sep"></span>
      <button type="button" class="toolbtn" data-block="H2" title="Título">Título</button>
      <button type="button" class="toolbtn" data-block="H3" title="Subtítulo">Subtítulo</button>
      <button type="button" class="toolbtn" data-block="P" title="Corpo">Corpo</button>
      <span class="toolbar-sep"></span>
      <button type="button" class="toolbtn" id="notesCopyBtn" title="Copiar anotação">Copiar</button>
    </div>
  </div>
  <div id="notesBody" contenteditable="true" spellcheck="false" data-placeholder="Escreva sua anotação..."></div>
</div>

<script>
  const BOOKS=__BOOKS_ARRAY__;
  const DEVOS=__DEVOS__;
  const LIVROS=__LIVROS__;
  // any book flipped from plain PDF pages (devotionals, most of the general
  // "Livros" shelf) has no per-unit table of contents, unlike the theology
  // resumões -- but a rich Livros book (real HTML pages, like "Divinamente")
  // ships its own .toc same as a theology book, so only items without one
  // land in the no-toc set
  const NO_TOC_IDS=new Set([...DEVOS,...LIVROS].filter(x=>x.id && !x.toc).map(x=>x.id));
  const CORRIDORS={
    teologia:{num:1,title:'Teologia',items:BOOKS},
    secreto:{num:2,title:'No Secreto',items:DEVOS},
    livros:{num:3,title:'Livros',items:LIVROS}
  };

  const shelf=document.getElementById('shelf');
  const viewLanding=document.getElementById('viewLanding');
  const viewCorridor=document.getElementById('viewCorridor');
  const corridorBooksEl=document.getElementById('corridorBooks');
  const corridorNumEl=document.getElementById('corridorNum');
  const corridorTitleEl=document.getElementById('corridorTitle');
  const corridorTintEl=document.getElementById('corridorTint');
  const reader=document.getElementById('reader');
  const readerStageEl=document.querySelector('.reader-stage');
  const bar=document.getElementById('bar');
  const counter=document.getElementById('counter');
  const topLeftBtns=document.getElementById('topLeftBtns');
  const backBtn=document.getElementById('backBtn');
  const homeBtn=document.getElementById('homeBtn');
  const menuBtn=document.getElementById('menuBtn');
  const notesBtn=document.getElementById('notesBtn');
  const containers={};
  BOOKS.forEach(b=>{containers[b.id]=document.getElementById('book-'+b.id);});
  DEVOS.forEach(d=>{containers[d.id]=document.getElementById('book-'+d.id);});
  LIVROS.forEach(l=>{if(l.id) containers[l.id]=document.getElementById('book-'+l.id);});
  const flips={};
  let curDeck=null, curCorridor=null;

  function bookCoverHTML(b){
    return '<div class="bcover '+b.theme+'" data-id="'+b.id+'" tabindex="0" role="button" '+
      'aria-label="Abrir '+b.title.replace(/\\n/g,' ')+'" onclick="openBook(\\''+b.id+'\\')" '+
      'onkeydown="if(event.key===\\'Enter\\'||event.key===\\' \\'){event.preventDefault();openBook(\\''+b.id+'\\')}">'+
        '<span class="bc-orn">&#10022;</span>'+
        '<span class="bc-title">'+b.title.replace(/\\n/g,'<br>')+'</span>'+
        '<span class="bc-rule"></span>'+
        '<span class="bc-prof">'+b.prof+'</span>'+
      '</div>';
  }
  function devoCoverHTML(d){
    return '<div class="bcover devo" data-id="'+d.id+'" tabindex="0" role="button" '+
      'aria-label="Abrir '+d.title+'" onclick="openBook(\\''+d.id+'\\')" '+
      'onkeydown="if(event.key===\\'Enter\\'||event.key===\\' \\'){event.preventDefault();openBook(\\''+d.id+'\\')}">'+
        '<img src="data:image/jpeg;base64,'+d.cover+'" alt="'+d.title+'" draggable="false">'+
      '</div>';
  }
  function placeholderHTML(f){
    return '<div class="bcover placeholder" title="Em breve"><span class="bc-title">'+f.label.replace(/\\n/g,'<br>')+'</span></div>';
  }
  /* an item is a theology resumão (has .toc), a PDF-flipped book with a real
     cover photo (devotional or "Livros" shelf entry, has .cover), or an
     empty upcoming slot (just a .label) -- dispatch on shape, not corridor */
  function renderItem(item){
    if(item.cover) return devoCoverHTML(item);
    if(item.toc) return bookCoverHTML(item);
    return placeholderHTML(item);
  }

  function populateCorridor(corId){
    const c=CORRIDORS[corId];
    corridorNumEl.textContent='CORREDOR '+c.num;
    corridorTitleEl.textContent=c.title;
    corridorTintEl.className='corridor-tint t-'+corId;
    corridorBooksEl.innerHTML=c.items.map(renderItem).join('');
  }

  function enterCorridor(corId){
    if(curCorridor) return;
    curCorridor=corId;
    sfxWhoosh();
    populateCorridor(corId);
    viewLanding.classList.add('leaving');
    setTimeout(()=>{
      viewLanding.classList.remove('show','leaving');
      viewCorridor.classList.add('show','entering-from');
      void viewCorridor.offsetWidth;
      viewCorridor.classList.remove('entering-from');
    },460);
  }

  function exitCorridor(){
    if(!curCorridor) return;
    curCorridor=null;
    sfxWhoosh();
    viewCorridor.classList.add('leaving');
    setTimeout(()=>{
      viewCorridor.classList.remove('show','leaving');
      viewLanding.classList.add('show','entering-from');
      void viewLanding.offsetWidth;
      viewLanding.classList.remove('entering-from');
    },460);
  }

  function showChrome(on){
    bar.style.display='none';
    counter.style.display=on?'block':'none';
    topLeftBtns.classList.toggle('show',on);
    menuBtn.style.display=on?'block':'none';
    // notesBtn segue o mesmo liga/desliga -- sem isso, ao sair de um livro
    // com anotacoes (hasNoToc=false, notesBtn 'block') de volta pro shelf/
    // pagina inicial, showChrome(false) escondia o menuBtn mas deixava o
    // NOTAS visivel por cima da estante/corredores. Quando on=true o valor
    // e' sobrescrito logo em seguida por enterReader() de acordo com hasNoToc.
    notesBtn.style.display=on?'block':'none';
  }

  /* ---- FLIP flight using a clone of the REAL front-cover card (transform-only) ----
     there is no separate illustrative "actor" element any more: what flies to the
     center of the screen is a literal clone of the clicked cover, so the cover can
     never render blank/transparent — it is the same opaque DOM node the whole time. */
  function openBook(id){
    if(curDeck) return;
    const originEl=document.querySelector('.bcover[data-id="'+id+'"]');
    if(!originEl) return;
    sfxOpen();
    const originRect=originEl.getBoundingClientRect();

    const targetW=Math.min(300, window.innerWidth*0.42, window.innerHeight*0.6*(originRect.width/originRect.height));
    const targetH=targetW*(originRect.height/originRect.width);

    const clone=originEl.cloneNode(true);
    clone.classList.add('flying-cover');
    clone.style.position='fixed';
    clone.style.left='50%';
    clone.style.top='50%';
    clone.style.width=targetW+'px';
    clone.style.height=targetH+'px';
    clone.style.margin='0';
    clone.style.zIndex='41';
    clone.style.transition='none';
    const scaleX=originRect.width/targetW, scaleY=originRect.height/targetH;
    const dx=(originRect.left+originRect.width/2)-(window.innerWidth/2);
    const dy=(originRect.top+originRect.height/2)-(window.innerHeight/2);
    clone.style.transform='translate(-50%,-50%) translate('+dx+'px,'+dy+'px) scale('+scaleX+','+scaleY+')';
    document.body.appendChild(clone);
    originEl.style.visibility='hidden';
    void clone.offsetWidth;

    requestAnimationFrame(()=>{
      clone.style.transition='transform .42s cubic-bezier(.16,1,.3,1)';
      clone.style.transform='translate(-50%,-50%) scale(1)';
    });

    /* hold on the cover for a beat once it lands centered, then the real reader takes
       over instantly — the clone is removed the same moment the reader appears, so it
       is never visible at the same time as the real StPageFlip content */
    setTimeout(()=>{
      clone.remove();
      shelf.classList.remove('show');
      enterReader(id);
    }, 420+60);
  }

  function ensureFlip(id){
    if(flips[id]) return flips[id];
    const container=containers[id];
    /* Devotionals use the exact same landscape, 2-page-spread book as the
       theology resumões: each PDF page is one "page", shown side by side
       (front/back, like a real open book) instead of alone. */
    const pf=new St.PageFlip(container, {
      width:460, height:640, size:'stretch',
      minWidth:260, maxWidth:760, minHeight:360, maxHeight:920,
      showCover:true, usePortrait:true, maxShadowOpacity:0.45,
      mobileScrollSupport:false, flippingTime:650,
      /* showPageCorners:false turns off the passive "corner lifts as soon as
         the mouse hovers nearby" preview -- the corner should only lift once
         the user actually clicks and holds to drag it; a plain click (no
         drag) still flips the page fully either way, that part of the
         library's own logic is untouched. */
      showPageCorners:false
    });
    /* StPageFlip auto-detects "hard" only for page 0 and, when the count
       after it is odd, the lone last page -- but a book's own designed back
       cover (.cover-page / .devo-cover) should swing rigid too whenever it
       exists, regardless of parity. StPageFlip reads data-density off each
       page element at load time, so mark those pages explicitly instead of
       depending on page-count luck. */
    container.querySelectorAll('.page.cover-page, .page.devo-cover')
      .forEach(p=>{ p.dataset.density='hard'; });
    pf.loadFromHTML(container.querySelectorAll('.page'));
    pf.on('flip',(e)=>{ if(curDeck===id){ updateCounter(id); sfxPage(); } });
    /* A hard cover (front or back) swings as a rigid, non-bending plane
       instead of curling like paper, so for one instant, right in the
       middle of the swing, it is turned exactly edge-on to the camera and
       is (correctly!) render-thin. That instant is the ONLY moment that
       needs a stand-in fill behind it — filling the whole flip's duration
       is what caused a "blank page" to flash in for the entire swing, not
       just that instant. So instead of reacting to the flip state alone,
       watch the actual rendered width of the flipping leaf every frame
       while a flip is in progress, and only switch on the paper-colored
       fill for the handful of frames where it truly is near zero-width. */
    let hardWatch=null;
    pf.on('changeState',(e)=>{
      if(curDeck!==id) return;
      if(hardWatch){ cancelAnimationFrame(hardWatch); hardWatch=null; }
      if(e.data==='read'){ readerStageEl.classList.remove('flip-live'); return; }
      const tick=()=>{
        if(curDeck!==id){ hardWatch=null; return; }
        const widths=[...container.querySelectorAll('.stf__item')]
          .filter(el=>getComputedStyle(el).display!=='none')
          .map(el=>el.getBoundingClientRect().width);
        const minW=widths.length?Math.min(...widths):999;
        readerStageEl.classList.toggle('flip-live', minW<12);
        hardWatch=requestAnimationFrame(tick);
      };
      tick();
    });
    flips[id]=pf;
    return pf;
  }

  function updateCounter(id){
    const pf=flips[id]; if(!pf) return;
    const cur=pf.getCurrentPageIndex()+1;
    const total=pf.getPageCount();
    counter.textContent=String(cur).padStart(2,'0')+' / '+String(total).padStart(2,'0');
    bar.style.width=(cur/total*100)+'%';
  }

  function enterReader(id){
    curDeck=id;
    const hasNoToc=NO_TOC_IDS.has(id);
    reader.classList.add('show');
    /* StPageFlip stamps an inline style="display:block" directly onto whichever
       container it is attached to (it doesn't just rely on our CSS classes), and
       that inline style sticks forever once a book has been opened once. So once
       two different books have both been opened in the same session, a plain
       .active class toggle is not enough to hide the one not being read — we have
       to override that inline style ourselves, explicitly, for every container,
       every time. */
    Object.entries(containers).forEach(([k,c])=>{
      const on=k===id;
      c.classList.toggle('active',on);
      c.style.display=on?'block':'none';
    });
    showChrome(true);
    menuBtn.style.display=hasNoToc?'none':'block';
    notesBtn.style.display=hasNoToc?'none':'block';
    notesRefreshDot();
    bar.style.display='block';
    requestAnimationFrame(()=>{
      ensureFlip(id);
      updateCounter(id);
      readerStageEl.classList.remove('flip-live');
      reader.classList.add('shown');
    });
  }

  function flipNext(){ if(curDeck&&flips[curDeck]) flips[curDeck].flipNext(); }
  function flipPrev(){ if(curDeck&&flips[curDeck]) flips[curDeck].flipPrev(); }
  function goBookStart(){
    /* Salto instantâneo pra capa (turnToPage, não flip animado) -- um botão
       de "reset" não precisa folhear todas as páginas de volta. O segundo
       turnToPage, depois do tempo de uma animação (flippingTime:650), é só
       uma trava de segurança: se o clique pegou uma virada de página ainda
       em andamento, essa virada termina DEPOIS do nosso salto e sobrescreve
       o índice sozinha -- o reforço garante que a página 1 realmente fique
       a que sobra no final. */
    if(!curDeck||!flips[curDeck]) return;
    const pf=flips[curDeck];
    pf.turnToPage(0);
    setTimeout(()=>{ if(curDeck&&flips[curDeck]===pf) pf.turnToPage(0); }, 700);
  }

  function goShelf(){
    if(!curDeck) return;
    const id=curDeck;
    const originEl=document.querySelector('.bcover[data-id="'+id+'"]');
    sfxClose();
    closeIdx();
    closeNotes();
    reader.classList.remove('shown');
    showChrome(false);
    setTimeout(()=>{
      reader.classList.remove('show');
      curDeck=null;
      shelf.classList.add('show');
      if(!originEl){ return; }

      const originRect=originEl.getBoundingClientRect();
      const targetW=Math.min(300, window.innerWidth*0.42, window.innerHeight*0.6*(originRect.width/originRect.height));
      const targetH=targetW*(originRect.height/originRect.width);

      const clone=originEl.cloneNode(true);
      clone.classList.add('flying-cover');
      clone.style.position='fixed';
      clone.style.left='50%';
      clone.style.top='50%';
      clone.style.width=targetW+'px';
      clone.style.height=targetH+'px';
      clone.style.margin='0';
      clone.style.zIndex='41';
      clone.style.transition='none';
      clone.style.transform='translate(-50%,-50%) scale(1)';
      document.body.appendChild(clone);
      void clone.offsetWidth;

      requestAnimationFrame(()=>{
        clone.style.transition='transform .42s cubic-bezier(.16,1,.3,1)';
        const scaleX=originRect.width/targetW, scaleY=originRect.height/targetH;
        const dx=(originRect.left+originRect.width/2)-(window.innerWidth/2);
        const dy=(originRect.top+originRect.height/2)-(window.innerHeight/2);
        clone.style.transform='translate(-50%,-50%) translate('+dx+'px,'+dy+'px) scale('+scaleX+','+scaleY+')';
      });
      setTimeout(()=>{
        clone.remove();
        originEl.style.visibility='';
      }, 420+60);
    },90);
  }

  function openIdx(){
    if(!curDeck)return;
    // a book's toc can live on BOOKS (theology) or, for a rich Livros title
    // like "Divinamente", on LIVROS -- look it up wherever it actually is
    const book=BOOKS.find(b=>b.id===curDeck) || LIVROS.find(b=>b.id===curDeck);
    if(!book||!book.toc)return;
    const wrap=document.getElementById('idxWrap');
    let html='<h4>'+book.title.replace(/\\n/g,' ')+'</h4>';
    book.toc.forEach(t=>{
      html+='<div class="item" onclick="jumpTo('+t.folio+')"><span class="n">'+String(t.folio).padStart(2,'0')+'</span><span class="t">'+t.title+'</span></div>';
    });
    wrap.innerHTML=html;
    document.getElementById('idx').classList.add('open');
  }
  function closeIdx(){document.getElementById('idx').classList.remove('open');}

  /* ---- notes (per-book, contenteditable, persisted per browser in localStorage) ---- */
  function notesKey(id){ return 'estudoNotas_'+id; }
  function notesHasContent(id){
    const v=localStorage.getItem(notesKey(id));
    return !!(v && v.replace(/<[^>]*>/g,'').trim().length);
  }
  function notesRefreshDot(){
    if(!curDeck) return;
    notesBtn.classList.toggle('has-note', notesHasContent(curDeck));
  }
  let notesSaveTimer=null;
  function notesStatus(msg,show){
    const el=document.getElementById('notesStatus');
    el.textContent=msg;
    el.classList.toggle('show',!!show);
  }
  function openNotes(){
    if(!curDeck) return;
    const book=BOOKS.find(b=>b.id===curDeck) || LIVROS.find(b=>b.id===curDeck);
    document.getElementById('notesTitle').textContent='Notas · '+(book?book.title.replace(/\n/g,' '):'');
    const body=document.getElementById('notesBody');
    body.innerHTML=localStorage.getItem(notesKey(curDeck))||'';
    document.getElementById('notesPanel').classList.add('open');
    document.body.classList.add('notes-open');
    notesStatus('',false);
    setTimeout(()=>body.focus(),260);
  }
  function closeNotes(){
    document.getElementById('notesPanel').classList.remove('open');
    document.body.classList.remove('notes-open');
  }
  function toggleNotes(){
    if(!curDeck) return;
    document.getElementById('notesPanel').classList.contains('open') ? closeNotes() : openNotes();
  }
  function notesSave(){
    if(!curDeck) return;
    const body=document.getElementById('notesBody');
    localStorage.setItem(notesKey(curDeck), body.innerHTML);
    notesRefreshDot();
    notesStatus('salvo',true);
    clearTimeout(notesSaveTimer);
    notesSaveTimer=setTimeout(()=>notesStatus('',false),1400);
  }
  function notesUpdateToolbarState(){
    ['bold','italic','underline'].forEach(cmd=>{
      const btn=document.querySelector('#notesPanel .toolbtn[data-cmd="'+cmd+'"]');
      if(btn) btn.classList.toggle('active', document.queryCommandState(cmd));
    });
  }
  function jumpTo(folio){
    if(!curDeck||!flips[curDeck])return;
    flips[curDeck].flip(folio-1);
    closeIdx();
  }

  document.addEventListener('keydown',e=>{
    if(document.getElementById('notesPanel').classList.contains('open')){ if(e.key==='Escape')closeNotes(); return; }
    if(document.getElementById('idx').classList.contains('open')){ if(e.key==='Escape')closeIdx(); return; }
    if(curDeck){
      if(e.key==='Escape'){goShelf();return;}
      if(e.key==='ArrowRight'){flipNext();}
      if(e.key==='ArrowLeft'){flipPrev();}
      if(e.key.toLowerCase()==='m')openIdx();
      if(e.key.toLowerCase()==='n')openNotes();
      return;
    }
    if(curCorridor && e.key==='Escape'){ exitCorridor(); }
  });

  const notesBodyEl=document.getElementById('notesBody');
  notesBodyEl.addEventListener('input', ()=>{ clearTimeout(notesSaveTimer); notesSaveTimer=setTimeout(notesSave,500); });
  document.querySelectorAll('#notesPanel .toolbtn[data-cmd]').forEach(btn=>{
    btn.addEventListener('mousedown', e=>e.preventDefault());
    btn.addEventListener('click', ()=>{ document.execCommand(btn.dataset.cmd); notesBodyEl.focus(); notesUpdateToolbarState(); notesSave(); });
  });
  document.querySelectorAll('#notesPanel .toolbtn[data-block]').forEach(btn=>{
    btn.addEventListener('mousedown', e=>e.preventDefault());
    btn.addEventListener('click', ()=>{ document.execCommand('formatBlock', false, '<'+btn.dataset.block+'>'); notesBodyEl.focus(); notesSave(); });
  });
  document.getElementById('notesCopyBtn').addEventListener('click', ()=>{
    const text=notesBodyEl.innerText.trim();
    if(!text) return;
    if(navigator.clipboard) navigator.clipboard.writeText(text).then(()=>notesStatus('copiado',true)).catch(()=>{});
  });
  document.addEventListener('selectionchange', ()=>{
    if(document.getElementById('notesPanel').classList.contains('open') && document.activeElement===notesBodyEl){
      notesUpdateToolbarState();
    }
  });
  document.addEventListener('click', e=>{
    const panel=document.getElementById('notesPanel');
    if(panel.classList.contains('open') && !panel.contains(e.target) && e.target!==notesBtn){
      closeNotes();
    }
  }, true);

  /* ============================================================
     Efeitos sonoros -- sintetizados na hora via Web Audio, sem
     nenhum arquivo de áudio externo (mantém o index.html
     autocontido). São só cliques/whooshes curtos, não música. Ligar
     / desligar persiste em localStorage; o AudioContext só é criado
     no primeiro gesto do usuário (autoplay policy dos navegadores).
     ============================================================ */
  let sfxCtx=null, sfxOn=true;
  try{ sfxOn = localStorage.getItem('bibliotecaSfxOn')!=='0'; }catch(err){}

  function sfxEnsureCtx(){
    if(!sfxCtx){
      try{ sfxCtx=new (window.AudioContext||window.webkitAudioContext)(); }catch(err){ return null; }
    }
    if(sfxCtx.state==='suspended'){ sfxCtx.resume(); }
    return sfxCtx;
  }
  function sfxTone(freqStart,freqEnd,dur,peak,type,delay){
    if(!sfxOn) return;
    const ctx=sfxEnsureCtx(); if(!ctx) return;
    const t0=ctx.currentTime+(delay||0);
    const osc=ctx.createOscillator(), gain=ctx.createGain();
    osc.type=type||'sine';
    osc.frequency.setValueAtTime(freqStart,t0);
    osc.frequency.exponentialRampToValueAtTime(Math.max(freqEnd,1),t0+dur);
    gain.gain.setValueAtTime(0.0001,t0);
    gain.gain.exponentialRampToValueAtTime(peak,t0+dur*0.18);
    gain.gain.exponentialRampToValueAtTime(0.0001,t0+dur);
    osc.connect(gain); gain.connect(ctx.destination);
    osc.start(t0); osc.stop(t0+dur+0.03);
  }
  function sfxNoise(dur,peak,filterFreq,delay){
    if(!sfxOn) return;
    const ctx=sfxEnsureCtx(); if(!ctx) return;
    const t0=ctx.currentTime+(delay||0);
    const len=Math.max(1,Math.floor(ctx.sampleRate*dur));
    const buf=ctx.createBuffer(1,len,ctx.sampleRate);
    const data=buf.getChannelData(0);
    for(let i=0;i<len;i++){ data[i]=(Math.random()*2-1)*(1-i/len); }
    const src=ctx.createBufferSource(); src.buffer=buf;
    const filter=ctx.createBiquadFilter(); filter.type='bandpass'; filter.frequency.value=filterFreq||1800; filter.Q.value=0.7;
    const gain=ctx.createGain();
    gain.gain.setValueAtTime(0.0001,t0);
    gain.gain.exponentialRampToValueAtTime(peak,t0+dur*0.12);
    gain.gain.exponentialRampToValueAtTime(0.0001,t0+dur);
    src.connect(filter); filter.connect(gain); gain.connect(ctx.destination);
    src.start(t0);
  }
  function sfxHover(){ sfxTone(1050,1400,0.05,0.02,'sine'); }
  function sfxClick(){ sfxTone(720,300,0.09,0.06,'triangle'); }
  function sfxPage(){ sfxNoise(0.26,0.05,2200); }
  function sfxOpen(){ sfxTone(220,440,0.22,0.045,'sine'); sfxNoise(0.3,0.03,2600,0.05); }
  function sfxClose(){ sfxTone(440,180,0.2,0.045,'sine'); }
  function sfxWhoosh(){ sfxNoise(0.35,0.035,1400); }

  function setSfxOn(on){
    sfxOn=on;
    try{ localStorage.setItem('bibliotecaSfxOn', on?'1':'0'); }catch(err){}
    document.getElementById('sfxBtn').classList.toggle('off', !on);
  }
  function toggleSfx(){ setSfxOn(!sfxOn); if(sfxOn) sfxClick(); }
  setSfxOn(sfxOn);

  const SFX_SELECTOR='.bcover,.corridor-zone,.flipbtn,#backBtn,#homeBtn,#menuBtn,.corridorExitBtn,#idx .item,#idx .close,#sfxBtn,#musicBtn,#musicPanel .track,#notesBtn,#notesPanel .toolbtn,#notesPanel .notes-close';
  let sfxLastHoverEl=null;
  document.addEventListener('mouseover',e=>{
    const el=e.target.closest(SFX_SELECTOR);
    if(el && el!==sfxLastHoverEl){ sfxLastHoverEl=el; sfxHover(); }
    else if(!el){ sfxLastHoverEl=null; }
  },true);
  document.addEventListener('click',e=>{
    if(e.target.closest(SFX_SELECTOR)) sfxClick();
  },true);

  /* ============================================================
     Seleção de texto dentro do livro -- a StPageFlip, por padrão,
     faz preventDefault() em QUALQUER mousedown sobre a página (é
     assim que ela consegue "grudar" no dedo/mouse pra virar a
     folha), o que também cancela a seleção nativa de texto do
     navegador. Aqui a gente intercepta em fase de captura, antes do
     evento chegar no handler da biblioteca: se o alvo do clique é
     conteúdo de texto de verdade (não a margem em branco da página,
     nem uma imagem de devocional escaneado), a gente para a
     propagação e deixa o navegador cuidar da seleção normalmente.
     Clicar na margem em branco, no folio ou numa imagem continua
     virando a página como sempre. */
  function isFlipZoneTarget(t){
    if(!t || t.nodeType!==1) return true;
    if(t.tagName==='IMG') return true;
    if(t.classList && (t.classList.contains('page') || t.classList.contains('page-inner'))) return true;
    if(t.closest && t.closest('.folio,.pagehead')) return true;
    return false;
  }
  function guardTextSelection(e){
    if(!curDeck) return;
    if(!isFlipZoneTarget(e.target)) e.stopPropagation();
  }
  readerStageEl.addEventListener('mousedown', guardTextSelection, true);
  readerStageEl.addEventListener('touchstart', guardTextSelection, true);

  /* ============================================================
     Música de fundo -- diferente dos efeitos sonoros (sintetizados
     na hora), aqui são faixas de verdade, e faixa de música em
     base64 dentro do index.html infla o arquivo em dezenas de MB por
     música -- por isso NÃO fica embutida: cada faixa é um mp3 solto
     numa pasta audio/ ao lado do index.html, e o player só referencia
     o caminho relativo. Pra adicionar uma faixa: solta o mp3 em
     audio/ e acrescenta uma linha em MUSIC_TRACKS abaixo (id, título
     pra mostrar no painel, e o caminho do arquivo). Toca em loop, com
     volume próprio, separado do volume do som do sistema. */
  const MUSIC_TRACKS = [
    // { id:'ambiente1', title:'Nome da faixa', file:'audio/nome-do-arquivo.mp3' },
  ];

  let musicAudio=null, musicCurrentId=null, musicVolume=0.35;
  try{
    const savedTrack=localStorage.getItem('bibliotecaMusicTrack');
    if(savedTrack) musicCurrentId=savedTrack;
    const savedVol=localStorage.getItem('bibliotecaMusicVol');
    if(savedVol!==null) musicVolume=Math.max(0,Math.min(1,parseFloat(savedVol)));
  }catch(err){}

  function musicEnsureAudio(){
    if(!musicAudio){
      musicAudio=new Audio();
      musicAudio.loop=true;
      musicAudio.volume=musicVolume;
      musicAudio.addEventListener('play',musicUpdateBtn);
      musicAudio.addEventListener('pause',musicUpdateBtn);
    }
    return musicAudio;
  }
  function musicPlay(id){
    const track=MUSIC_TRACKS.find(t=>t.id===id);
    if(!track) return;
    const audio=musicEnsureAudio();
    if(musicCurrentId===id && !audio.paused){
      audio.pause();
    } else {
      if(musicCurrentId!==id) audio.src=track.file;
      musicCurrentId=id;
      audio.play().catch(()=>{});
      try{ localStorage.setItem('bibliotecaMusicTrack', id); }catch(err){}
    }
    musicRenderTracks();
  }
  function musicSetVolume(v){
    musicVolume=v;
    if(musicAudio) musicAudio.volume=v;
    try{ localStorage.setItem('bibliotecaMusicVol', String(v)); }catch(err){}
  }
  function musicRenderTracks(){
    const wrap=document.getElementById('musicTrackList');
    if(!wrap) return;
    if(!MUSIC_TRACKS.length){
      wrap.innerHTML='<div class="empty">Nenhuma faixa na biblioteca ainda. Solte arquivos em <code>audio/</code> e liste em <code>MUSIC_TRACKS</code>.</div>';
      return;
    }
    const playing=musicAudio&&!musicAudio.paused;
    wrap.innerHTML=MUSIC_TRACKS.map(t=>
      '<div class="track'+(musicCurrentId===t.id&&playing?' active':'')+'" onclick="musicPlay(\\''+t.id+'\\')"><span class="dot"></span>'+t.title+'</div>'
    ).join('');
  }
  function musicUpdateBtn(){
    document.getElementById('musicBtn').classList.toggle('playing', !!(musicAudio && !musicAudio.paused));
    musicRenderTracks();
  }
  function toggleMusicPanel(){
    const panel=document.getElementById('musicPanel');
    panel.classList.toggle('open');
    if(panel.classList.contains('open')) musicRenderTracks();
  }
  document.addEventListener('click',e=>{
    const panel=document.getElementById('musicPanel'), btn=document.getElementById('musicBtn');
    if(panel.classList.contains('open') && !panel.contains(e.target) && e.target!==btn){
      panel.classList.remove('open');
    }
  }, true);
  const musicVolSlider=document.getElementById('musicVolSlider');
  musicVolSlider.value=Math.round(musicVolume*100);
  musicVolSlider.addEventListener('input', e=>{ musicSetVolume(parseInt(e.target.value,10)/100); });
</script>
</body>
</html>
"""

# ---- generate everything that's per-theology-book from THEOLOGY_BOOKS ----
books_js_array = "[\n    " + ",\n    ".join(
    "{id:%s,title:%s,prof:%s,theme:%s,toc:__TOC_%s__}"
    % (json.dumps(b["id"]), json.dumps(b["title"], ensure_ascii=False),
       json.dumps(b["prof"], ensure_ascii=False), json.dumps(b["theme"]), b["id"].upper())
    for b in THEOLOGY_BOOKS
) + "\n  ]"
theology_books_html = "".join(
    '<div id="book-%s" class="stbook" data-theme="%s">\n%s\n</div>\n' % (b["id"], b["theme"], b["pages"])
    for b in THEOLOGY_BOOKS
)

TAIL_END = TAIL_END.replace("__BOOKS_ARRAY__", books_js_array)

# "Divinamente" -- its cover is the designed photo (not a CSS gradient), so
# it rides the shelf like a devo/Livros PDF book (renderItem dispatches on
# .cover first), but it also ships a real .toc like a theology book, which
# is what keeps ÍNDICE and NOTAS switched on for it (see NO_TOC_IDS above).
divinamente_js = {
    "id": "divinamente",
    "title": "Divinamente",
    "cover": divinamente_cover_b64,
    "toc": divinamente_toc,
}
divinamente_book_html = (
    '<div id="book-divinamente" class="stbook" data-theme="divinamente">\n%s\n</div>\n'
    % divinamente_pages
)

# "Anjos, Demônios e o Mundo Espiritual" -- mesmo esquema do Divinamente:
# capa fotográfica própria (gerada por código, não pintura de IA -- ver
# build/mundoespiritual/art_gen.py) + toc real, também no corredor Livros.
mundoespiritual_js = {
    "id": "mundoespiritual",
    "title": "Anjos, Demônios e\no Mundo Espiritual",
    "cover": mundoespiritual_cover_b64,
    "toc": mundoespiritual_toc,
}
mundoespiritual_book_html = (
    '<div id="book-mundoespiritual" class="stbook" data-theme="mundoespiritual">\n%s\n</div>\n'
    % mundoespiritual_pages
)

devos_json = json.dumps(devos_js, ensure_ascii=False)
# the "Livros" shelf mixes real books already added with empty placeholder slots
# for what's not on it yet, so ship both in one JS array
livros_json = json.dumps(
    livros_js + [divinamente_js, mundoespiritual_js] + [{"label": "Próxima\nleitura"}],
    ensure_ascii=False,
)
TAIL_END = TAIL_END.replace("__DEVOS__", devos_json).replace("__LIVROS__", livros_json)
for b in THEOLOGY_BOOKS:
    TAIL_END = TAIL_END.replace(
        "__TOC_%s__" % b["id"].upper(),
        json.dumps(b["toc"], ensure_ascii=False),
    )

books_html = (
    theology_books_html + devo_books_html + livro_books_html
    + divinamente_book_html + mundoespiritual_book_html
)

out = HEAD + books_html + TAIL_END
out = (out.replace("__LANDING_ART__", landing_b64)
          .replace("__CORRIDOR_ART__", corshelf_b64)
          .replace("__TABLE_ART__", table_art_b64))

with open("/home/claude/estudo-teologia/index.html", "w", encoding="utf-8") as f:
    f.write(out)

print("written v6, bytes:", len(out))
