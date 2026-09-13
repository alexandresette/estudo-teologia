"""
Template de "chunker" -- transforma um RESUMAO-<LIVRO>.html (o conteúdo
bruto, autoral, em <section class="slide">) nas páginas físicas do
flipbook (pages_<id>.html) + o índice (toc_<id>.json) que o build6.py
consome.

Como usar pra um livro novo:
1. Copia esse arquivo pra chunk_<id>.py
2. Ajusta BOOK_ID e SRC_PATH abaixo
3. Roda: python3 chunk_<id>.py
4. Confere a contagem de páginas impressa no final -- PRECISA SER PAR
   (a StPageFlip só faz a capa traseira virar "dura"/reta quando o total
   é par; se der ímpar, split uma seção grande em duas, usando o padrão
   de continuação abaixo)
5. Adiciona a entrada em THEOLOGY_BOOKS no build6.py (id, title, prof,
   theme, cover_a, cover_b, pages_file, toc_file) + as variáveis CSS
   --<theme> / --<theme>-deep no :root

Formato esperado de cada <section class="slide"> no RESUMAO de origem:
- data-title="Título da seção" (usado no índice/TOC)
- classe "cover" na PRIMEIRA seção (vira a capa dura do livro)
- pra dividir uma seção grande em duas páginas (evitar ímpar, ou só
  porque o conteúdo é longo demais pra uma página), a seção de
  continuação leva um <div class="pagehead">Título · continua</div>
  como primeiro filho em vez do kicker/h2/hr normal -- isso faz o
  chunker saber que não é uma entrada nova de índice
"""
from bs4 import BeautifulSoup
import json

BOOK_ID = "SEU_ID_AQUI"                                    # ex: "arbi"
SRC_PATH = "/home/claude/estudo-teologia/RESUMAO-XXXXX.html"  # ex: RESUMAO-ARQUEOLOGIA-BIBLICA.html

src = open(SRC_PATH, encoding="utf-8").read()
soup = BeautifulSoup(src, "html.parser")
slides = soup.select("section.slide")

out_pages = []
toc = []

for sec in slides:
    is_cover = "cover" in sec.get("class", [])
    title = sec.get("data-title", "")
    inner = "".join(str(c) for c in sec.contents)
    is_continuation = sec.find("div", class_="pagehead") is not None
    physical_page_num = len(out_pages) + 1

    if is_cover:
        page_html = '<div class="page cover-page" data-density="hard"><div class="page-inner">%s</div></div>' % inner
    else:
        page_html = '<div class="page"><div class="page-inner">%s</div><div class="folio">%02d</div></div>' % (inner, physical_page_num)

    out_pages.append(page_html)
    if is_cover or not is_continuation:
        toc.append({"folio": physical_page_num, "title": title})

with open(f"/tmp/pages_{BOOK_ID}.html", "w", encoding="utf-8") as f:
    f.write("\n".join(out_pages))
with open(f"/tmp/toc_{BOOK_ID}.json", "w", encoding="utf-8") as f:
    json.dump(toc, f, ensure_ascii=False, indent=2)

print("pages:", len(out_pages), "-- PRECISA SER PAR")
print("toc entries:", len(toc))
