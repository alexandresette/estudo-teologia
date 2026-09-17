#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terceira geração das artes de "Anjos, Demônios e o Mundo Espiritual" --
agora com o crédito do Gemini recarregado (confirmado em 2026-09-17), as
imagens passam a ser pinturas de IA de verdade (gemini-3-pro-image), no
mesmo registro épico das referências que o Xande mandou: céu tempestuoso,
luz dourada rasgando as nuvens, figura humana minúscula pra dar escala.

Uso: python3 gemini_gen.py
Gera images_jpg/ch1..7.jpg (paisagem 16:9) e cover.jpg (retrato, com a
tipografia do título aplicada por cima via PIL -- o "mix de imagem com
letras fortes" que o Xande pediu pra capa).
"""
import base64
import json
import os
import time
import urllib.request

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "images_jpg")
COVER_JPG = os.path.join(HERE, "cover.jpg")
os.makedirs(IMG_DIR, exist_ok=True)

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise SystemExit(
        "Defina a variavel de ambiente GEMINI_API_KEY antes de rodar este "
        "script (export GEMINI_API_KEY=... ou um .env local nao versionado)."
    )
MODEL = "gemini-3-pro-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

STYLE = (
    ", epic cinematic religious concept art, dramatic painterly digital "
    "illustration in the style of matte painting, dark stormy atmosphere "
    "pierced by golden divine light, rich painterly brushwork, moody "
    "biblical tone, no text, no watermark, no logo, no signature"
)

CHAPTER_PROMPTS = {
    1: "A vast golden divine throne glimpsed through a massive gap in dark "
       "storm clouds high above, radiant beams of golden light pouring down "
       "from it, tiny silhouette of a person kneeling far below on a rocky "
       "ledge in awe, wide landscape composition, no medieval castle, no "
       "dragons, no knights",
    2: "A massive sunrise breaking through heavy storm clouds like a "
       "radiant eye of light over a vast landscape, golden rays spreading "
       "across a dark sky, tiny silhouette of a person standing on a hill "
       "looking up in wonder, wide landscape composition",
    3: "A tiny silhouette of a person kneeling in prayer, prostrate, bowed "
       "low, on a rocky cliff edge, beneath a massive shaft of golden light "
       "breaking through dark turbulent storm clouds, epic scale, wide "
       "landscape composition",
    4: "A colossal winged angelic figure of pure light emerging from bright "
       "golden clouds high in a stormy sky, radiant glory behind it, a tiny "
       "silhouette of a person standing far below with arms raised in "
       "worship, reverent and majestic not scary, wide landscape composition",
    5: "A massive jagged crack of brilliant white light violently splitting "
       "a heavy dark storm sky in two, a fracture of pure light tearing "
       "through blackness like lightning, small distant rocky landscape "
       "below, dramatic, wide landscape composition, no human figure",
    6: "A small humble stone house glowing with warm golden light from its "
       "windows, standing alone on a hilltop beneath a vast dramatic stormy "
       "sky with golden light breaking through heavy clouds above, a tiny "
       "silhouette of a person walking a path toward it, wide landscape "
       "composition",
    7: "A tiny silhouette of a person standing firm and resolute on a rocky "
       "mountain pinnacle, facing a massive turbulent stormy sky with "
       "golden light breaking through dark clouds, sense of unwavering "
       "faith, wide landscape composition",
}

COVER_PROMPT = (
    "Dark heavy storm clouds parting to reveal an immense radiant golden "
    "gate of light and the faint silhouette of a divine throne beyond, "
    "dramatic god-rays pouring through the gap, a tiny silhouette of a "
    "person standing far below in awe on a rocky ledge, vertical "
    "composition, the lower third of the frame darker and more shadowed "
    "for a calm foreground, atmospheric"
)


def call_gemini(prompt, aspect_ratio, retries=4):
    payload = {
        "contents": [{"parts": [{"text": prompt + STYLE}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect_ratio},
        },
    }
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    last_err = None
    for attempt in range(retries):
        try:
            resp = urllib.request.urlopen(req, timeout=90)
            data = json.loads(resp.read())
            cand = data["candidates"][0]
            parts = cand.get("content", {}).get("parts", [])
            for p in parts:
                inline = p.get("inlineData")
                if inline:
                    return base64.b64decode(inline["data"])
            raise RuntimeError("sem imagem na resposta: finishReason=%s" % cand.get("finishReason"))
        except Exception as e:
            last_err = e
            print("  tentativa %d falhou: %s" % (attempt + 1, e))
            time.sleep(3 * (attempt + 1))
    raise last_err


def gen_chapters():
    for num, prompt in CHAPTER_PROMPTS.items():
        path = os.path.join(IMG_DIR, "ch%d.jpg" % num)
        print("gerando ch%d..." % num)
        img_bytes = call_gemini(prompt, "16:9")
        with open(path, "wb") as f:
            f.write(img_bytes)
        print("  ok:", path, len(img_bytes), "bytes")


FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"
F_TITLE = os.path.join(FONT_DIR, "BigShoulders-Bold.ttf")
F_SUBTITLE = os.path.join(FONT_DIR, "IBMPlexSerif-Italic.ttf")
F_LABEL = os.path.join(FONT_DIR, "WorkSans-Bold.ttf")
F_AUTHOR = os.path.join(FONT_DIR, "IBMPlexSerif-Regular.ttf")


def _wrap_lines(draw, words, font, max_width):
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def compose_cover(raw_bytes, w, h, title, subtitle, author):
    import io
    img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    # cobre pro tamanho alvo (crop central) mantendo a composicao centrada
    src_w, src_h = img.size
    scale = max(w / src_w, h / src_h)
    img = img.resize((int(src_w * scale) + 1, int(src_h * scale) + 1), Image.LANCZOS)
    src_w, src_h = img.size
    left, top = (src_w - w) // 2, (src_h - h) // 2
    img = img.crop((left, top, left + w, top + h))

    # veu escuro gradual na metade inferior, pra sustentar o texto
    veil = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(veil)
    for y in range(h):
        t = max(0, (y - h * 0.5) / (h * 0.5))
        vd.line([(0, y), (w, y)], fill=int(215 * min(1, t ** 0.8)))
    dark = Image.new("RGB", (w, h), (4, 4, 8))
    img = Image.composite(dark, img, veil)

    draw = ImageDraw.Draw(img)
    cream = (238, 227, 202)
    gold = (223, 186, 122)

    # todo o bloco de texto e' construido de cima pra baixo, cada elemento
    # a partir de onde o anterior terminou -- nada de y fixo pro rodape,
    # senao um titulo de 3 linhas empurra o autor pra cima do que sobrar e
    # fica espremido (ou cortado) contra a borda inferior
    kicker = "SÉRIE DECLARAÇÕES PROFÉTICAS"
    f_kicker = ImageFont.truetype(F_LABEL, int(w * 0.022))
    letter_gap = w * 0.013
    char_widths = [draw.textbbox((0, 0), ch, font=f_kicker)[2] for ch in kicker]
    total_w = sum(char_widths) + letter_gap * (len(kicker) - 1)
    ky = h * 0.535
    xk = (w - total_w) / 2
    for ch, cw in zip(kicker, char_widths):
        draw.text((xk, ky), ch, font=f_kicker, fill=gold)
        xk += cw + letter_gap
    draw.line([(w * 0.5 - w * 0.09, ky + h * 0.026), (w * 0.5 + w * 0.09, ky + h * 0.026)],
              fill=gold, width=2)

    words = title.upper().split(" ")
    f_title = ImageFont.truetype(F_TITLE, int(w * 0.115))
    lines = _wrap_lines(draw, words, f_title, w * 0.86)
    while True:
        total_h = 0
        for ln in lines:
            b = draw.textbbox((0, 0), ln, font=f_title)
            total_h += (b[3] - b[1]) * 1.04
        if total_h <= h * 0.215 or f_title.size <= 36:
            break
        f_title = ImageFont.truetype(F_TITLE, f_title.size - 4)
        lines = _wrap_lines(draw, words, f_title, w * 0.86)

    ty = ky + h * 0.075
    for ln in lines:
        b = draw.textbbox((0, 0), ln, font=f_title)
        lw = b[2] - b[0]
        lh = b[3] - b[1]
        draw.text(((w - lw) / 2, ty), ln, font=f_title, fill=cream)
        ty += lh * 1.08

    f_sub = ImageFont.truetype(F_SUBTITLE, int(w * 0.028))
    sub_lines = _wrap_lines(draw, subtitle.split(" "), f_sub, w * 0.7)
    ty += h * 0.018
    for ln in sub_lines:
        b = draw.textbbox((0, 0), ln, font=f_sub)
        lw = b[2] - b[0]
        draw.text(((w - lw) / 2, ty), ln, font=f_sub, fill=(214, 205, 184))
        ty += (b[3] - b[1]) * 1.3

    # autor: pelo menos 9% de margem livre ate a borda inferior, sempre
    ly = min(ty + h * 0.035, h * 0.91)
    draw.line([(w * 0.5 - w * 0.1, ly), (w * 0.5 + w * 0.1, ly)], fill=gold, width=2)
    f_auth = ImageFont.truetype(F_AUTHOR, int(w * 0.026))
    ab = draw.textbbox((0, 0), author, font=f_auth)
    draw.text(((w - (ab[2] - ab[0])) / 2, ly + h * 0.014), author, font=f_auth, fill=cream)

    return img


def gen_cover():
    print("gerando capa...")
    raw = call_gemini(COVER_PROMPT, "2:3")
    img = compose_cover(
        raw, 900, 1320,
        title="Anjos, Demônios e o Mundo Espiritual",
        subtitle="Sete declarações para viver com discernimento e autoridade espiritual",
        author="A partir do estudo de Ingrid Marianno",
    )
    img.save(COVER_JPG, "JPEG", quality=93)
    print("  ok:", COVER_JPG)


if __name__ == "__main__":
    gen_chapters()
    gen_cover()
    print("Pronto.")
