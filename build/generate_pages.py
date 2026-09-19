#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Segunda etapa: usa o que extract_multipage.py já preparou na raiz do repo
(_meta.json, livro/<id>/_content.html, livro/<id>/cover.jpg|img/*, assets/*)
pra montar as páginas HTML de verdade: index.html (landing), corredor/*.html
e livro/<id>/index.html -- cada uma um arquivo físico próprio, sem
hash-routing. _meta.json/_content.html são intermediários: apagar depois
que o rebuild estiver validado (não afetam o site publicado).
"""
import json
import os
import shutil

OUT = "/home/claude/estudo-teologia"
BUILD_DIR = os.path.dirname(os.path.abspath(__file__))

TITLE_SITE = "Biblioteca de Estudos · Xande"
DESC_SITE = "Biblioteca viva de resumões de estudo do curso de Teologia. Cada disciplina, um livro na estante."

MOTES_HTML = '<div class="motes" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div>'

GATE_HTML = open(os.path.join(OUT, "_gate.html"), encoding="utf-8").read()

CORRIDOR_TITLES = {
    "teologia": ("1", "Teologia"),
    "secreto": ("2", "No Secreto"),
    "livros": ("3", "Resumo de Livros"),
}


def head(rel, title):
    return (
        '<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>%s</title>\n'
        '<meta name="description" content="%s">\n'
        '<link rel="stylesheet" href="%sassets/site.css">\n'
        '</head>\n<body data-rel="%s">\n' % (title, DESC_SITE, rel, rel)
    )


def gate_for(rel):
    return GATE_HTML.replace("{{REL}}", rel)


def ambient(rel):
    return (
        MOTES_HTML + "\n"
        '<button id="sfxBtn" onclick="toggleSfx()" title="Ativar ou desativar som" '
        'aria-label="Ativar ou desativar som">&#9834;</button>\n'
    )


def shelf_header():
    return (
        '<header id="libHeader">\n'
        '  <h1 class="hdr-title">Biblioteca de Estudos</h1>\n'
        '  <div class="hdr-verse">Colossenses 3:23-24</div>\n'
        '  <button id="gateExitBtn" class="gateExitBtn" onclick="exitToGate()" '
        'title="Sair da biblioteca">&#8592; Sair</button>\n'
        '</header>\n'
    )


def bcover_html(b, rel_to_livro):
    """b: meta dict. rel_to_livro: caminho relativo até a pasta livro/ (ex.: '../livro/')."""
    bid = b["id"]
    href = "%s%s/" % (rel_to_livro, bid)
    title_html = b["title"].replace("\n", "<br>")
    title_flat = b["title"].replace("\n", " ")
    if b["kind"] == "books":
        theme = b.get("theme") or ""
        return (
            '<a class="bcover %s" data-id="%s" href="%s" aria-label="Abrir %s">'
            '<span class="bc-frame"></span>'
            '<span class="bc-corner tl">&#9670;</span><span class="bc-corner tr">&#9670;</span>'
            '<span class="bc-corner bl">&#9670;</span><span class="bc-corner br">&#9670;</span>'
            '<span class="bc-body"><span class="bc-orn">&#10022;</span>'
            '<span class="bc-title">%s</span><span class="bc-rule"></span></span>'
            '</a>' % (theme, bid, href, title_flat, title_html)
        )
    else:
        cover_rel = "%s%s/%s" % (rel_to_livro, bid, b["_cover_rel"])
        return (
            '<a class="bcover devo" data-id="%s" href="%s" aria-label="Abrir %s">'
            '<img src="%s" alt="%s" draggable="false"></a>'
            % (bid, href, title_flat, cover_rel, title_flat)
        )


def build_landing(meta_by_kind):
    rel = ""
    html = []
    html.append(head(rel, TITLE_SITE))
    html.append(gate_for(rel))
    html.append(ambient(rel))
    html.append('<section id="shelf" class="show">\n')
    html.append(shelf_header())
    html.append('<div id="viewport">\n<div id="viewLanding" class="view show">\n')
    html.append('  <div class="hall-art">\n    <img src="assets/img/hall-art.jpg" alt="">\n')
    html.append('    <div class="hall-picks">\n')
    for key in ("teologia", "secreto", "livros"):
        num, title = CORRIDOR_TITLES[key]
        html.append(
            '      <a class="corridor-zone" href="corredor/%s.html" aria-label="Entrar no corredor %s">'
            '<div class="placard-hang"><span class="n">%s</span>%s</div>'
            '<div class="enter-cue">entrar &#8594;</div></a>\n' % (key, title, num, title)
        )
    html.append('    </div>\n  </div>\n')
    html.append('</div>\n</div>\n</section>\n')
    html.append('<script src="assets/site.js"></script>\n</body>\n</html>\n')
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write("".join(html))


def build_corredor(key, items):
    rel = "../"
    num, title = CORRIDOR_TITLES[key]
    html = []
    html.append(head(rel, title + " · " + TITLE_SITE))
    html.append(gate_for(rel))
    html.append(ambient(rel))
    html.append('<section id="shelf" class="show">\n')
    html.append(shelf_header())
    html.append('<div id="viewport">\n<div id="viewCorridor" class="view show">\n')
    html.append('<button class="corridorExitBtn" onclick="location.href=\'../index.html\'">&#8592; Corredores</button>\n')
    html.append('  <div class="corridor-area">\n    <div class="corridor-stage">\n')
    html.append('      <img src="../assets/img/corridor-bg.jpg" alt="">\n')
    html.append('      <div class="corridor-tint t-%s"></div>\n' % key)
    html.append('      <div class="corridor-heading"><span class="n">CORREDOR %s</span><h2>%s</h2></div>\n' % (num, title))
    html.append('      <div class="cshelf">\n')
    for b in items:
        html.append(bcover_html(b, "../livro/"))
    html.append('      </div>\n    </div>\n  </div>\n')
    html.append('</div>\n</div>\n</section>\n')
    html.append('<script src="../assets/site.js"></script>\n</body>\n</html>\n')
    open(os.path.join(OUT, "corredor", key + ".html"), "w", encoding="utf-8").write("".join(html))


def build_livro(b, corridor_key):
    rel = "../../"
    bid = b["id"]
    title_flat = b["title"].replace("\n", " ")
    has_toc = bool(b.get("toc"))
    content_path = os.path.join(OUT, "livro", bid, "_content.html")
    content_html = open(content_path, encoding="utf-8").read()

    html = []
    html.append(head(rel, title_flat + " · " + TITLE_SITE))
    html.append(gate_for(rel))
    html.append('<div id="bar"></div>\n')
    html.append('<div id="topLeftBtns" class="show">\n')
    html.append('  <a id="backBtn" href="../../corredor/%s.html">&#8592; Estante</a>\n' % corridor_key)
    html.append('  <button id="homeBtn" onclick="goBookStart()" title="Voltar ao início do livro">&#8607; Início</button>\n')
    html.append('</div>\n')
    if has_toc:
        html.append('<button id="menuBtn" style="display:block" onclick="openIdx()">&#9776; ÍNDICE</button>\n')
    html.append(ambient(rel))
    html.append('<div id="counter"></div>\n')

    html.append('<div id="reader" class="show shown" data-book-id="%s">\n' % bid)
    html.append('  <div class="reader-slot">\n  <div class="reader-stage">\n')
    html.append(content_html)
    html.append('  </div>\n  </div>\n')
    html.append('</div>\n')
    html.append('<button id="flipPrev" class="flipbtn" onclick="flipPrev()">&#8592;</button>\n')
    html.append('<button id="flipNext" class="flipbtn" onclick="flipNext()">&#8594;</button>\n')
    html.append('<div class="reader-hint">setas do teclado ou clique na borda da página pra virar</div>\n')

    if has_toc:
        html.append('<div id="idx"><span class="close" onclick="closeIdx()">&#10005;</span><div class="wrap" id="idxWrap">\n')
        html.append('  <h4>%s</h4>\n' % title_flat)
        for t in b["toc"]:
            html.append(
                '  <div class="item" onclick="jumpTo(%d)"><span class="n">%s</span><span class="t">%s</span></div>\n'
                % (t["folio"], str(t["folio"]).zfill(2), t["title"])
            )
        html.append('</div></div>\n')

    if has_toc:
        html.append('<button id="notesBtn" style="display:block" onclick="toggleNotes()" title="Minhas anotações" aria-label="Minhas anotações">&#9998; NOTAS</button>\n')
        html.append(
            '<div id="notesPanel">\n'
            '  <div class="notes-head">\n'
            '    <div class="notes-head-top">\n'
            '      <span class="notes-title" id="notesTitle">Notas &middot; %s</span>\n'
            '      <span class="notes-status" id="notesStatus">salvo</span>\n'
            '      <span class="notes-close" onclick="closeNotes()" title="Fechar anotações">&#10005;</span>\n'
            '    </div>\n'
            '    <div class="notes-toolbar">\n'
            '      <button type="button" class="toolbtn" data-cmd="bold" title="Negrito"><b>N</b></button>\n'
            '      <button type="button" class="toolbtn" data-cmd="italic" title="Itálico"><i>I</i></button>\n'
            '      <button type="button" class="toolbtn" data-cmd="underline" title="Sublinhado"><u>S</u></button>\n'
            '      <span class="toolbar-sep"></span>\n'
            '      <button type="button" class="toolbtn" data-block="H2" title="Título">Título</button>\n'
            '      <button type="button" class="toolbtn" data-block="H3" title="Subtítulo">Subtítulo</button>\n'
            '      <button type="button" class="toolbtn" data-block="P" title="Corpo">Corpo</button>\n'
            '      <span class="toolbar-sep"></span>\n'
            '      <button type="button" class="toolbtn" id="notesCopyBtn" title="Copiar anotação">Copiar</button>\n'
            '    </div>\n'
            '  </div>\n'
            '  <div id="notesBody" contenteditable="true" spellcheck="false" data-placeholder="Escreva sua anotação..."></div>\n'
            '</div>\n' % title_flat
        )

    html.append('<script src="../../assets/pageflip.js"></script>\n')
    html.append('<script src="../../assets/site.js"></script>\n')
    html.append('</body>\n</html>\n')

    out_path = os.path.join(OUT, "livro", bid, "index.html")
    open(out_path, "w", encoding="utf-8").write("".join(html))


def main():
    # site.js é autoral (não gerado a partir do monólito) -- vive em build/
    # e é copiado pra dentro do site a cada geração, pra "rm -rf site_v2 &&
    # extract && generate" ser sempre um rebuild completo e confiável.
    shutil.copyfile(os.path.join(BUILD_DIR, "site.js"), os.path.join(OUT, "assets", "site.js"))

    meta = json.load(open(os.path.join(OUT, "_meta.json"), encoding="utf-8"))
    by_corr = {"teologia": [], "secreto": [], "livros": []}
    for b in meta:
        by_corr[b["_corr"]].append(b)

    build_landing(by_corr)
    for key, items in by_corr.items():
        build_corredor(key, items)
    for b in meta:
        build_livro(b, b["_corr"])

    print("Gerado:")
    print(" - index.html")
    for key in by_corr:
        print(" - corredor/%s.html" % key)
    for b in meta:
        print(" - livro/%s.html" % b["id"])


if __name__ == "__main__":
    main()
