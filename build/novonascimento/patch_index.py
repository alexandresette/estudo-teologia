#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insere "Novo Nascimento" (Bispo Paulo Filho) no index.html (e,
opcionalmente, no build6.py) como um livro NOVO -- diferente de
patch_index.py do livro1, que SUBSTITUI uma entrada ja existente, este
script ADICIONA uma div "book-novonascimento" nova e insere a entrada
como o PRIMEIRO item do array LIVROS (na frente de livro1), sem tocar
nas entradas ja existentes.

Roda direto sobre um arquivo alvo passado por argumento (index.html ou
build6.py), sem depender dos /tmp assets que o build6.py completo
normalmente precisa -- mesma tecnica usada pra livro1 / Divinamente /
Anjos e Demonios / Passado Resolvido.

Pre-requisito: rodar build_novonascimento.py neste mesmo diretorio
antes, pra gerar pages_novonascimento.html e toc_novonascimento.json.
"""
import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

PAGES_HTML = os.path.join(HERE, "pages_novonascimento.html")
TOC_JSON = os.path.join(HERE, "toc_novonascimento.json")
COVER_JPG = os.path.join(HERE, "cover.jpg")


def b64_of(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


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


def find_insertion_point_for_div(data):
    """Insere a nova div logo antes da primeira 'book-' div existente
    (atualmente book-exegese, a primeira do corredor Teologia) -- nao
    importa a posicao exata no DOM, o JS mapeia por id, mas manter perto
    das outras 'book-' divs facilita leitura do arquivo."""
    key = '<div id="book-'
    idx = data.find(key)
    if idx == -1:
        raise SystemExit("nao encontrei nenhuma div 'book-' no arquivo")
    return idx


def main():
    if len(sys.argv) != 2:
        raise SystemExit("uso: patch_index.py <caminho_para_index.html_ou_build6.py>")
    target_path = sys.argv[1]

    if not os.path.exists(PAGES_HTML) or not os.path.exists(TOC_JSON):
        raise SystemExit(
            "Rode build_novonascimento.py primeiro (precisa de "
            "pages_novonascimento.html e toc_novonascimento.json)."
        )

    data = open(target_path, encoding="utf-8").read()
    before_len = len(data)

    if 'id="book-novonascimento"' in data:
        raise SystemExit(
            "book-novonascimento ja existe neste arquivo -- rode o script de "
            "atualizacao (nao este) se a intencao e apenas atualizar o conteudo."
        )

    # ---- 1) inserir a nova <div id="book-novonascimento">...</div> ----
    pages_novonascimento = open(PAGES_HTML, encoding="utf-8").read()
    new_book_div = (
        '<div id="book-novonascimento" class="stbook" data-theme="novonascimento">\n%s\n</div>\n'
        % pages_novonascimento
    )
    insert_at = find_insertion_point_for_div(data)
    data = data[:insert_at] + new_book_div + data[insert_at:]
    print("book-novonascimento div inserida: %d bytes" % len(new_book_div))

    # ---- 2) inserir a entrada "novonascimento" como PRIMEIRO item do array JS LIVROS ----
    arr_start, arr_end = find_livros_array_span(data)
    arr_text = data[arr_start:arr_end]
    livros = json.loads(arr_text)

    if any(isinstance(e, dict) and e.get("id") == "novonascimento" for e in livros):
        raise SystemExit("a entrada novonascimento ja existe dentro do array LIVROS")

    toc = json.load(open(TOC_JSON, encoding="utf-8"))
    cover_b64 = b64_of(COVER_JPG)
    new_entry = {
        "id": "novonascimento",
        "title": "Novo Nascimento",
        "cover": cover_b64,
        "toc": toc,
    }

    livros.insert(0, new_entry)

    new_arr_text = json.dumps(livros, ensure_ascii=False)
    data = data[:arr_start] + new_arr_text + data[arr_end:]
    print("LIVROS array: %d bytes -> %d bytes (%d entradas)" % (len(arr_text), len(new_arr_text), len(livros)))

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(data)
    print("%s: %d bytes -> %d bytes" % (target_path, before_len, len(data)))
    print("OK.")


if __name__ == "__main__":
    main()
