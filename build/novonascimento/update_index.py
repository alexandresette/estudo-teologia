#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualiza o conteudo do livro "Novo Nascimento" ja presente no index.html
(diferente de patch_index.py, que ADICIONA a entrada pela primeira vez e
recusa se ela ja existir). Este script SUBSTITUI a div
id="book-novonascimento" pelo conteudo atual de pages_novonascimento.html,
e atualiza o campo "toc" da entrada correspondente dentro do array JS
LIVROS -- sem mexer em id/title/cover nem na posicao da entrada no array.

Uso: rodar build_novonascimento.py primeiro, depois:
    python3 update_index.py <caminho_para_index.html>
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES_HTML = os.path.join(HERE, "pages_novonascimento.html")
TOC_JSON = os.path.join(HERE, "toc_novonascimento.json")


def find_livros_array_span(data):
    key = "const LIVROS="
    idx = data.find(key)
    if idx == -1:
        raise SystemExit("nao encontrei 'const LIVROS=' no arquivo")
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


def find_book_div_span(data, book_id):
    key = '<div id="book-%s"' % book_id
    start = data.find(key)
    if start == -1:
        raise SystemExit("nao encontrei a div book-%s no arquivo" % book_id)
    close_tag = "\n</div>\n"
    end = data.find(close_tag, start)
    if end == -1:
        raise SystemExit("nao encontrei o fechamento da div book-%s" % book_id)
    end += len(close_tag)
    return start, end


def main():
    if len(sys.argv) != 2:
        raise SystemExit("uso: update_index.py <caminho_para_index.html>")
    target_path = sys.argv[1]

    if not os.path.exists(PAGES_HTML) or not os.path.exists(TOC_JSON):
        raise SystemExit(
            "Rode build_novonascimento.py primeiro (precisa de "
            "pages_novonascimento.html e toc_novonascimento.json)."
        )

    data = open(target_path, encoding="utf-8").read()
    before_len = len(data)

    if 'id="book-novonascimento"' not in data:
        raise SystemExit(
            "book-novonascimento nao existe neste arquivo -- rode "
            "patch_index.py (nao este) para inserir pela primeira vez."
        )

    # ---- 1) substituir a div <div id="book-novonascimento">...</div> ----
    pages_novonascimento = open(PAGES_HTML, encoding="utf-8").read()
    new_book_div = (
        '<div id="book-novonascimento" class="stbook" data-theme="novonascimento">\n%s\n</div>\n'
        % pages_novonascimento
    )
    div_start, div_end = find_book_div_span(data, "novonascimento")
    old_div_len = div_end - div_start
    data = data[:div_start] + new_book_div + data[div_end:]
    print("book-novonascimento div: %d bytes -> %d bytes" % (old_div_len, len(new_book_div)))

    # ---- 2) atualizar o campo "toc" da entrada dentro do array LIVROS ----
    arr_start, arr_end = find_livros_array_span(data)
    arr_text = data[arr_start:arr_end]
    livros = json.loads(arr_text)

    entry = next((e for e in livros if isinstance(e, dict) and e.get("id") == "novonascimento"), None)
    if entry is None:
        raise SystemExit("a entrada novonascimento nao existe dentro do array LIVROS")

    toc = json.load(open(TOC_JSON, encoding="utf-8"))
    entry["toc"] = toc

    new_arr_text = json.dumps(livros, ensure_ascii=False)
    data = data[:arr_start] + new_arr_text + data[arr_end:]
    print("LIVROS array: %d bytes -> %d bytes (%d entradas)" % (len(arr_text), len(new_arr_text), len(livros)))

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(data)
    print("%s: %d bytes -> %d bytes" % (target_path, before_len, len(data)))
    print("OK.")


if __name__ == "__main__":
    main()
