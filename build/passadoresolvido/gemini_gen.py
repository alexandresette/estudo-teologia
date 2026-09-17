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
Gera images_jpg/ch1..8.jpg em retrato (3:4) -- a pagina de arte do site e'
um container retrato (460x640, razao ~0.72) com object-fit:cover, entao
gerar em paisagem 16:9 cortava o objeto principal pras laterais (foi o
que aconteceu na primeira geracao). 3:4 (0.75) e' quase igual a razao da
pagina, corte minimo.
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

# As paginas de arte do site sao um container RETRATO (460x640, razao
# ~0.72), nao paisagem -- a imagem entra com object-fit:cover, entao tudo
# que nao estiver dentro da faixa vertical central acaba cortado nas
# laterais. Por isso os prompts abaixo pedem composicao VERTICAL, com o
# elemento principal empilhado no centro (nao espalhado de ponta a ponta
# horizontalmente), e geramos em "3:4" (0.75), quase igual a razao real da
# pagina -- corte minimo, sem depender de sorte no enquadramento.
CHAPTER_PROMPTS = {
    1: "A single small silhouetted figure sitting alone and curled up in a "
       "vast empty muted landscape, centered in frame, a faint tangled "
       "knot of glowing thread wrapped invisibly around their chest, "
       "evoking quiet inner pain that has no name, soft cool desaturated "
       "color palette, vertical portrait composition, melancholic but "
       "tender, no text",
    2: "A gnarled thorny plant growing straight up from a deep crack in "
       "dry cracked ground, centered in frame, twisted dark root visible "
       "below the surface glowing faintly red like an old wound, the "
       "plant's stem covered in thorns rising up the middle of the frame, "
       "producing one shriveled bitter black flower at the very top, "
       "symbolic illustration, dramatic side lighting, tall vertical "
       "portrait composition",
    3: "A glowing burning bush centered in frame on a rocky mountainside "
       "at dusk, woodcut and screenprint illustration style, radiant warm "
       "orange and gold light pouring from within the bush without "
       "consuming it, a small silhouetted figure kneeling directly in "
       "front of it in awe and hesitation, deep blue mountain shadows "
       "behind, tall vertical portrait composition, the bush and the "
       "kneeling figure both fully inside the frame",
    4: "A young stylized character's face centered in frame, breaking out "
       "of a cracked stone mask or shell shaped like their own face, "
       "brilliant warm golden light pouring through the cracks from "
       "within, fragments floating away, animated film character concept "
       "art, vertical portrait composition, sense of rebirth and renewal",
    5: "A lone hooded wanderer centered in frame, walking across vast "
       "desert dunes at night toward a huge glowing full moon directly "
       "above on the horizon, long footprints trailing behind in the "
       "sand, ink and screenprint illustration style, deep indigo sky, "
       "warm moonlight, tall vertical portrait composition, the "
       "wanderer and the moon both fully inside the frame, sense of "
       "quiet determination",
    6: "A small silhouetted figure standing centered in frame, facing a "
       "tall wall covered in handwritten notes, pinned photographs, "
       "string and sketches rising above and around them, lit from below "
       "by a single warm desk lamp glowing at the base of the wall, deep "
       "indigo night sky with stars visible through a window to the "
       "side, moody painterly animated concept art matching the same "
       "dramatic lighting and muted color grading as the rest of this "
       "series, no cartoonish or cute character design, tall vertical "
       "portrait composition, cozy but atmospheric mood",
    7: "A large ornate glowing golden key turning inside a heart-shaped "
       "keyhole carved into a dark stone wall, centered in frame, warm "
       "radiant golden light pouring out from within the heart through "
       "the keyhole, engraved vine and thorn patterns on the stone around "
       "it slowly turning into leaves near the light, symbolic "
       "illustration, screenprint poster style, tall vertical portrait "
       "composition, clean bold centered composition, no text",
    8: "A tangled dark knot of thread glowing faintly at the bottom of "
       "the frame, one end of the thread pulling free and rising "
       "straight up through the center, straightening into a long "
       "luminous golden arrow pointing upward toward a bright glowing "
       "sunrise centered at the very top of the frame, symbolic "
       "illustration on a deep dark background, screenprint poster "
       "style, tall vertical portrait composition, clean bold centered "
       "composition, hopeful and resolute mood, no text",
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
        img_bytes = call_gemini(prompt, "3:4")
        with open(path, "wb") as f:
            f.write(img_bytes)
        print("  ok:", path, len(img_bytes), "bytes")


if __name__ == "__main__":
    gen_chapters()
    print("Pronto.")
