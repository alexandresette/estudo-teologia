import difflib
from bs4 import BeautifulSoup

def norm_text(path, decompose_classes):
    soup = BeautifulSoup(open(path, encoding="utf-8").read(), "html.parser")
    for cls in decompose_classes:
        for el in soup.select("." + cls):
            el.decompose()
    txt = soup.get_text(" ", strip=True)
    return " ".join(txt.split())

pairs = [
    ("/home/claude/estudo-teologia/RESUMAO-EXEGESE-AT.html", "book-exegese"),
    ("/home/claude/estudo-teologia/RESUMAO-TBNT.html", "book-tbnt"),
    ("/home/claude/estudo-teologia/RESUMAO-GREGO-INSTRUMENTAL.html", "book-grego"),
    ("/home/claude/estudo-teologia/RESUMAO-HOMILETICA.html", "book-homiletica"),
    ("/home/claude/estudo-teologia/RESUMAO-MISSIOLOGIA.html", "book-missio"),
    ("/home/claude/estudo-teologia/RESUMAO-ARQUEOLOGIA-BIBLICA.html", "book-arbi"),
    ("/home/claude/estudo-teologia/RESUMAO-PROJETO-PESQUISA.html", "book-tcc1"),
    ("/home/claude/estudo-teologia/RESUMAO-EXEGESE-NT.html", "book-exnote"),
]

built = open("/home/claude/estudo-teologia/index.html", encoding="utf-8").read()
soup_built = BeautifulSoup(built, "html.parser")

for orig_path, book_id in pairs:
    orig_txt = norm_text(orig_path, ["folio", "pagehead", "cover-page"])

    book_div = soup_built.find(id=book_id)
    for cls in ["folio", "pagehead", "cover-page"]:
        for el in book_div.select("." + cls):
            el.decompose()
    built_txt = " ".join(book_div.get_text(" ", strip=True).split())

    sm = difflib.SequenceMatcher(None, orig_txt, built_txt)
    ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    print(f"=== {book_id} ===")
    print("opcodes (non-equal):", len(ops))
    for op in ops:
        tag, i1, i2, j1, j2 = op
        print(" ", tag, repr(orig_txt[i1:i2][:120]), "->", repr(built_txt[j1:j2][:120]))
