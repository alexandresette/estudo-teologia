#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrai o monólito antigo (build/source_monolith.html -- single-file, tudo
embutido em base64) e gera a árvore de site multi-página de verdade: cada
corredor e cada livro é um arquivo HTML fisicamente separado, com uma URL
própria, e as imagens (que no monólito são base64 embutido) viram arquivos
de imagem reais, referenciados por caminho relativo -- cacheáveis pelo
navegador, inspecionáveis, e que não obrigam a baixar o site inteiro (49MB)
só pra ler uma página.

Lê build/source_monolith.html (fonte da verdade de conteúdo, nunca é
sobrescrito por este script) e escreve o site direto na raiz do repo
(index.html, corredor/, livro/, assets/) -- rodar de novo é sempre um
rebuild completo e seguro.
"""
import base64
import json
import os
import re
import sys
import hashlib

SRC = "/home/claude/estudo-teologia/build/source_monolith.html"
OUT = "/home/claude/estudo-teologia"

def read_src():
    return open(SRC, encoding="utf-8").read()

def find_balanced(data, open_ch, close_ch, start):
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(data)):
        c = data[i]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
            continue
        if c == '"': in_str = True
        elif c == open_ch: depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
    raise SystemExit("unbalanced %s/%s from %d" % (open_ch, close_ch, start))

def find_array_span(data, key):
    idx = data.find(key)
    if idx == -1:
        raise SystemExit("key not found: %r" % key)
    arr_start = idx + len(key)
    arr_end = find_balanced(data, "[", "]", arr_start)
    return arr_start, arr_end

_DIV_TAG_RE = re.compile(r'<div\b|</div>')

def find_div_span(data, div_id):
    """Acha o span de <div id="div_id">...</div> contando profundidade de
    <div>/</div> aninhados de verdade -- não pode confiar em achar o
    primeiro "\\n</div>\\n" literal, porque livros com HTML bonito
    (multi-linha, </div> sozinho numa linha) tem esse padrão bem antes
    do fechamento real do div externo, cortando o conteúdo pela metade."""
    key = '<div id="%s"' % div_id
    start = data.find(key)
    if start == -1:
        raise SystemExit("div not found: %s" % div_id)
    tag_end = data.find(">", start)
    if tag_end == -1:
        raise SystemExit("malformed opening div for %s" % div_id)
    pos = tag_end + 1
    depth = 1
    for m in _DIV_TAG_RE.finditer(data, pos):
        if m.group() == "</div>":
            depth -= 1
            if depth == 0:
                return start, m.end()
        else:
            depth += 1
    raise SystemExit("closing div not found for %s" % div_id)

def parse_book_objects(arr_text):
    """Extrai objetos top-level de um array JS tipo `[{...},{...}]`, tolerando
    chaves sem aspas (BOOKS) -- devolve a lista de (texto_do_objeto)."""
    objs = []
    i = 0
    n = len(arr_text)
    while i < n:
        if arr_text[i] == "{":
            j = find_balanced(arr_text, "{", "}", i)
            objs.append(arr_text[i:j])
            i = j
        else:
            i += 1
    return objs

def get_field(obj_text, field, default=None):
    m = re.search(r'"?%s"?\s*:\s*"((?:[^"\\]|\\.)*)"' % re.escape(field), obj_text)
    if not m:
        return default
    return m.group(1).encode().decode("unicode_escape").encode("latin1").decode("utf-8", "ignore") \
        if False else m.group(1).replace('\\n', '\n').replace('\\"', '"')

def get_toc(obj_text):
    m = re.search(r'"?toc"?\s*:\s*\[', obj_text)
    if not m:
        return None
    start = m.end() - 1
    end = find_balanced(obj_text, "[", "]", start)
    return json.loads(obj_text[start:end])

def get_cover_b64(obj_text):
    m = re.search(r'"?cover"?\s*:\s*"([A-Za-z0-9+/=]+)"', obj_text)
    return m.group(1) if m else None

def main():
    data = read_src()
    print("source size:", len(data))
    os.makedirs(OUT, exist_ok=True)
    assets_dir = os.path.join(OUT, "assets")
    img_dir = os.path.join(assets_dir, "img")
    livro_dir = os.path.join(OUT, "livro")
    corredor_dir = os.path.join(OUT, "corredor")
    for d in (assets_dir, img_dir, livro_dir, corredor_dir):
        os.makedirs(d, exist_ok=True)

    # ---- 1) CSS ----
    s = data.find("<style>") + len("<style>")
    e = data.find("</style>")
    css = data[s:e]
    open(os.path.join(assets_dir, "site.css"), "w", encoding="utf-8").write(css)
    print("site.css:", len(css), "bytes")

    # ---- 2) StPageFlip lib ----
    s = data.find("<script>!function")
    body_start = s + len("<script>")
    e = data.find("</script>", s)
    pageflip_js = data[body_start:e]
    open(os.path.join(assets_dir, "pageflip.js"), "w", encoding="utf-8").write(pageflip_js)
    print("pageflip.js:", len(pageflip_js), "bytes")

    # ---- 3) gate video + poster ----
    m = re.search(r'<video id="gateVideo"[^>]*poster="data:image/jpeg;base64,([A-Za-z0-9+/=]+)"', data)
    poster_b64 = m.group(1)
    open(os.path.join(assets_dir, "gate-poster.jpg"), "wb").write(base64.b64decode(poster_b64))
    m2 = re.search(r'<source src="data:video/mp4;base64,([A-Za-z0-9+/=]+)"', data)
    video_b64 = m2.group(1)
    open(os.path.join(assets_dir, "gate.mp4"), "wb").write(base64.b64decode(video_b64))
    print("gate.mp4:", len(video_b64)*3//4, "bytes (approx)")

    # gate markup verbatim (from <div id="gate"> to its closing </div>) with video/poster swapped
    gs, ge = find_div_span(data, "gate")
    gate_html = data[gs:ge]
    gate_html = re.sub(r'poster="data:image/jpeg;base64,[A-Za-z0-9+/=]+"', 'poster="{{REL}}assets/gate-poster.jpg"', gate_html)
    gate_html = re.sub(r'<source src="data:video/mp4;base64,[A-Za-z0-9+/=]+" type="video/mp4">',
                        '<source src="{{REL}}assets/gate.mp4" type="video/mp4">', gate_html)

    # ---- 4) landing hall-art + corridor-stage bg ----
    m = re.search(r'<div class="hall-art">\s*<img src="data:image/jpeg;base64,([A-Za-z0-9+/=]+)"', data)
    hall_b64 = m.group(1)
    open(os.path.join(img_dir, "hall-art.jpg"), "wb").write(base64.b64decode(hall_b64))

    # corridor-stage's own bg img (inside viewCorridor, not inside .hall-art)
    vc_start = data.find('<div id="viewCorridor"')
    m = re.search(r'<div class="corridor-stage">\s*<img src="data:image/jpeg;base64,([A-Za-z0-9+/=]+)"', data[vc_start:])
    corridor_bg_b64 = m.group(1)
    open(os.path.join(img_dir, "corridor-bg.jpg"), "wb").write(base64.b64decode(corridor_bg_b64))
    print("hall-art.jpg + corridor-bg.jpg written")

    # ---- 5) parse BOOKS / DEVOS / LIVROS ----
    bs, be = find_array_span(data, "const BOOKS=")
    books_objs = parse_book_objects(data[bs:be])
    ds, de_ = find_array_span(data, "const DEVOS=")
    devos_objs = parse_book_objects(data[ds:de_])
    ls, le = find_array_span(data, "const LIVROS=")
    livros_objs = parse_book_objects(data[ls:le])

    def as_meta(obj_text, kind):
        return {
            "kind": kind,
            "id": get_field(obj_text, "id"),
            "title": get_field(obj_text, "title"),
            "theme": get_field(obj_text, "theme"),
            "toc": get_toc(obj_text),
            "cover_b64": get_cover_b64(obj_text),
        }

    all_books = []
    for o in books_objs:
        meta = as_meta(o, "books")
        if meta["id"]:
            all_books.append(meta)
    for o in devos_objs:
        meta = as_meta(o, "devos")
        if meta["id"]:
            all_books.append(meta)
    for o in livros_objs:
        meta = as_meta(o, "livros")
        if meta["id"]:
            all_books.append(meta)

    print("total books found:", len(all_books))
    for b in all_books:
        print("  -", b["kind"], b["id"], "toc:", len(b["toc"]) if b["toc"] else 0, "cover:", bool(b["cover_b64"]))

    # save intermediate metadata for the next script (page generation) to reuse
    meta_out = []
    for b in all_books:
        meta_out.append({k: v for k, v in b.items() if k != "cover_b64"})
    json.dump(meta_out, open(os.path.join(OUT, "_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    CORRIDOR_OF_KIND = {"books": "teologia", "devos": "secreto", "livros": "livros"}

    # ---- 6) per-book: extract div content, decode images, write cover ----
    for b in all_books:
        bid = b["id"]
        corr = CORRIDOR_OF_KIND[b["kind"]]
        book_out_dir = os.path.join(livro_dir, bid)
        img_out_dir = os.path.join(book_out_dir, "img")
        os.makedirs(img_out_dir, exist_ok=True)

        ds2, de2 = find_div_span(data, "book-%s" % bid)
        book_html = data[ds2:de2]

        # decode every embedded base64 image inside the book div into img/NN.jpg|png
        seen_hash = {}
        counter = [0]
        def repl(m):
            mime = m.group(1)
            b64 = m.group(2)
            raw = base64.b64decode(b64)
            h = hashlib.sha1(raw).hexdigest()
            if h in seen_hash:
                fname = seen_hash[h]
            else:
                counter[0] += 1
                ext = "png" if mime == "png" else "jpg"
                fname = "img/img%02d.%s" % (counter[0], ext)
                open(os.path.join(book_out_dir, fname), "wb").write(raw)
                seen_hash[h] = fname
            return 'src="%s"' % fname

        book_html_new = re.sub(r'src="data:image/(jpeg|png);base64,([A-Za-z0-9+/=]+)"', repl, book_html)
        n_images = counter[0]

        # cover from LIVROS/DEVOS json (usada tanto como thumb da estante quanto,
        # na maioria dos livros, é literalmente o mesmo arquivo da capa dentro do
        # livro -- dedup por hash pra nao gravar o mesmo jpg duas vezes)
        cover_rel = None
        if b["cover_b64"]:
            cover_bytes = base64.b64decode(b["cover_b64"])
            h = hashlib.sha1(cover_bytes).hexdigest()
            if h in seen_hash:
                cover_rel = seen_hash[h]
            else:
                cover_rel = "cover.jpg"
                open(os.path.join(book_out_dir, cover_rel), "wb").write(cover_bytes)

        b["_corr"] = corr
        b["_n_images"] = n_images
        b["_cover_rel"] = cover_rel
        open(os.path.join(book_out_dir, "_content.html"), "w", encoding="utf-8").write(book_html_new)
        print("book %-20s corr=%-9s images=%2d cover=%s" % (bid, corr, n_images, cover_rel))

    # persist updated meta (with corridor + image counts) for the page-generation step
    meta_out2 = []
    for b in all_books:
        meta_out2.append({k: v for k, v in b.items() if k != "cover_b64"})
    json.dump(meta_out2, open(os.path.join(OUT, "_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---- 7) gate markup file (shared, with {{REL}} placeholder) ----
    open(os.path.join(OUT, "_gate.html"), "w", encoding="utf-8").write(gate_html)

    print("\nOK. Extraction complete -> ", OUT)

if __name__ == "__main__":
    main()
