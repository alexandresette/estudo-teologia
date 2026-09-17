#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera as 8 ilustracoes internas de "Passado Resolvido, Futuro Decidido"
com o Gemini (gemini-3-pro-image), no estilo animacao das referencias que
o Xande mandou (figuras estilizadas tipo concept art de animacao, silhueta
grafica forte, cores saturadas, toques de textura tipo xilogravura/serigrafia).

A capa NAO e gerada aqui -- e a foto real da capa fisica do livro, ja
recortada em cover.jpg por um script a parte.

Uso: export GEMINI_API_KEY=... && python3 gemini_gen.py
Gera images_jpg/ch1..8.jpg (paisagem 16:9).
"""
import base64
import json
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "images_jpg")
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
    ", vibrant modern animated film concept art, bold cel-shaded "
    "illustration with painterly rim light, strong clean graphic "
    "silhouette, rich saturated color palette, moody dramatic "
    "atmosphere, subtle screenprint and woodcut style textured linework "
    "accents, no text, no watermark, no logo, no signature"
)

CHAPTER_PROMPTS = {
    1: "A single small silhouetted figure sitting alone and curled up in a "
       "vast empty muted landscape, a faint tangled knot of glowing thread "
       "wrapped invisibly around their chest, evoking quiet inner pain that "
       "has no name, soft cool desaturated color palette, wide composition, "
       "melancholic but tender, no text",
    2: "A gnarled thorny plant growing from a deep crack in dry cracked "
       "ground, twisted dark root visible below the surface glowing faintly "
       "red like an old wound, the plant's stem covered in thorns, "
       "producing one shriveled bitter black flower at the top, symbolic "
       "illustration, dramatic side lighting, wide composition",
    3: "A glowing burning bush on a rocky mountainside at dusk, woodcut "
       "and screenprint illustration style, radiant warm orange and gold "
       "light pouring from within the bush without consuming it, a small "
       "silhouetted figure kneeling nearby in awe and hesitation, deep "
       "blue mountain shadows, wide landscape composition",
    4: "A young stylized character breaking out of a cracked stone mask "
       "or shell shaped like their own face, brilliant warm golden light "
       "pouring through the cracks from within, fragments floating away, "
       "animated film character concept art, dramatic close composition, "
       "sense of rebirth and renewal",
    5: "A lone hooded wanderer walking across vast desert dunes at night "
       "toward a huge glowing moon on the horizon, long footprints trailing "
       "behind in the sand, ink and screenprint illustration style, deep "
       "indigo sky, warm moonlight, wide landscape composition, sense of "
       "quiet determination",
    6: "A young stylized character standing in front of a large wall "
       "covered in handwritten notes, pinned photographs, string and "
       "sketches, under a warm desk lamp glow contrasted with a starry "
       "night sky visible through a window, animated illustration style, "
       "cozy and hopeful atmosphere, wide composition",
    7: "A stylized character in glowing translucent protective armor made "
       "of soft golden light, standing guard at the open doorway of a "
       "small warm-lit house, holding back a muted stormy grey world "
       "outside, animated concept art, strong silhouette, dramatic "
       "contrast between warm inside and cold outside, wide composition",
    8: "A tangled dark knot of thread glowing faintly, one end of the "
       "thread pulling free and straightening into a long luminous golden "
       "arrow pointing toward a bright sunrise on the horizon, symbolic "
       "illustration on a deep dark background, screenprint poster style, "
       "clean bold composition, hopeful and resolute mood, wide "
       "composition, no text",
}


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


if __name__ == "__main__":
    gen_chapters()
    print("Pronto.")
