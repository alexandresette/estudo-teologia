#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplica no index.html já implantado a conversão de "O Poder de Ser
Mulher" (livro1) do formato plano (PDF escaneado, 32 páginas, sem
capítulos) pro formato rico do resumo de estudo (7 capítulos, com
verso/framework/declaração + as 7 artes do Gemini), mantendo a capa
(página 1) e a última página (biografia da autora, página 32) do livro
original.

Roda direto sobre o index.html final, sem depender dos /tmp assets que
o build6.py completo normalmente precisa (mesma técnica usada pra
adicionar Divinamente / Anjos e Demônios / Passado Resolvido).

Pré-requisito: rodar build_livro1.py neste mesmo diretório antes, pra
gerar pages_livro1.html e toc_livro1.json a partir de chapters.py + as
7 imagens em images_jpg/ch1..7.jpg.
"""
import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
INDEX_PATH = os.path.join(REPO_ROOT, "index.html")

PAGES_HTML = os.path.join(HERE, "pages_livro1.html")
TOC_JSON = os.path.join(HERE, "toc_livro1.json")
COVER_JPG = os.path.join(HERE, "cover.jpg")


def b64_of(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def find_book_div_span(data, book_id):
    start_tag = '<div id="book-%s"' % book_id
    start = data.find(start_tag)
    if start == -1:
        raise SystemExit("nao encontrei %r no index.html" % start_tag)
    nxt = data.find('<div id="book-', start + len(start_tag))
    if nxt == -1:
        raise SystemExit("nao encontrei o proximo book div depois de %r" % start_tag)
    return start, nxt


def find_livros_array_span(data):
    key = "const LIVROS="
    idx = data.find(key)
    if idx == -1:
        raise SystemExit("nao encontrei 'const LIVROS=' no index.html")
    arr_start = idx + len(key)
    depth = 0
    in_str = False
    esc = False
    for i in range(arr_start, len(data)):
        c = data[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return arr_start, i + 1
    raise SystemExit("nao fechei o array LIVROS (colchetes desbalanceados?)")


def main():
    if not os.path.exists(PAGES_HTML) or not os.path.exists(TOC_JSON):
        raise SystemExit(
            "Rode build_livro1.py primeiro (precisa de pages_livro1.html e "
            "toc_livro1.json)."
        )

    data = open(INDEX_PATH, encoding="utf-8").read()
    before_len = len(data)

    # ---- 1) trocar o <div id="book-livro1">...</div> plano pelo rico ----
    pages_livro1 = open(PAGES_HTML, encoding="utf-8").read()
    new_book_div = (
        '<div id="book-livro1" class="stbook" data-theme="livro1">\n%s\n</div>\n'
        % pages_livro1
    )
    start, end = find_book_div_span(data, "livro1")
    old_len = end - start
    data = data[:start] + new_book_div + data[end:]
    print("book-livro1 div: %d bytes -> %d bytes" % (old_len, len(new_book_div)))

    # ---- 2) trocar a entrada "livro1" no array JS LIVROS ----
    arr_start, arr_end = find_livros_array_span(data)
    arr_text = data[arr_start:arr_end]
    livros = json.loads(arr_text)

    toc = json.load(open(TOC_JSON, encoding="utf-8"))
    cover_b64 = b64_of(COVER_JPG)
    new_entry = {
        "id": "livro1",
        "title": "O Poder de Ser Mulher",
        "cover": cover_b64,
        "toc": toc,
    }

    found = False
    for i, entry in enumerate(livros):
        if entry.get("id") == "livro1":
            livros[i] = new_entry
            found = True
            break
    if not found:
        raise SystemExit("nao achei a entrada livro1 dentro do array LIVROS")

    new_arr_text = json.dumps(livros, ensure_ascii=False)
    data = data[:arr_start] + new_arr_text + data[arr_end:]
    print("LIVROS array: %d bytes -> %d bytes (%d entradas)" % (len(arr_text), len(new_arr_text), len(livros)))

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(data)
    print("index.html: %d bytes -> %d bytes" % (before_len, len(data)))
    print("OK.")


if __name__ == "__main__":
    main()
