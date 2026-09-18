#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera as 10 ilustracoes internas do resumo de "Novo Nascimento" (Bispo
Paulo Filho) com o Gemini (gemini-3-pro-image), no estilo realista e
cinematografico das referencias que o Xande mandou (luz dramatica de
alto contraste, textura fotografica / pintura digital hiper-realista,
atmosfera epica e tensa) -- bem diferente do aquarela lilas usado em
"O Poder de Ser Mulher".

A capa (cover.jpg) NAO e gerada aqui -- e a foto real da capa fisica
do livro, so recortada/redimensionada (ver crop_cover.py). So as 10
artes de capitulo saem do Gemini.

Uso: export GEMINI_API_KEY=... && python3 gemini_gen.py
Gera images_jpg/ch1..10.jpg em retrato (3:4) -- a pagina de arte do
site e um container retrato com object-fit:cover, entao composicao
vertical com o elemento central empilhado, sem espalhar de ponta a
ponta horizontalmente.
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
        "script (export GEMINI_API_KEY=...)."
    )
MODEL = "gemini-3-pro-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

STYLE = (
    ", hyperrealistic cinematic digital painting, dramatic chiaroscuro "
    "lighting, high contrast, epic and tense atmosphere, photographic "
    "detail and texture, muted earth tones with warm gold or cool teal "
    "highlights, painterly but realistic rendering, no text, no "
    "watermark, no logo, no signature, no captions"
)

CHAPTER_PROMPTS = {
    1: "A sleeping housecat curled peacefully on a windowsill at night, "
       "but its shadow cast on the wall behind it is a crouching wild "
       "tiger with bared teeth, dramatic single light source, tall "
       "vertical portrait composition, unsettling and revealing mood",
    2: "A regal figure in fine robes wearing an ornate cracked golden "
       "theatrical mask, a sliver of pure darkness visible through the "
       "crack where the true face should be, dramatic single-source "
       "side lighting, tall vertical portrait composition, unsettling "
       "and revealing mood",
    3: "A single ornate golden chalice standing center frame, polished "
       "and gleaming on the outside, cracked open on one side to reveal "
       "rot and darkness inside, dramatic spotlight from above, deep "
       "black background, tall vertical portrait composition",
    4: "A solitary figure sitting hidden beneath a large fig tree at "
       "night, a single powerful beam of light breaking through the "
       "branches from directly above and falling only on him, vast dark "
       "landscape around, tall vertical portrait composition, epic and "
       "quietly exposed mood",
    5: "A strong hand breaking the surface of dark turbulent water from "
       "above, sunlight breaking through storm clouds behind it, "
       "reaching down to grasp a smaller drowning hand rising just "
       "beneath the surface, dramatic cinematic light rays underwater, "
       "tall vertical portrait composition",
    6: "A large dead gnarled tree struck at its base by a heavy axe, "
       "tangled dark roots exposed in torn soil beneath it, storm clouds "
       "and a single shaft of lightning-lit sky above, tall vertical "
       "portrait composition, epic and severe mood",
    7: "An ornate porcelain theatrical mask cracking and falling away in "
       "mid-air from an unseen face shrouded in shadow, fragments "
       "catching dramatic side light as they fall, deep black "
       "background, tall vertical portrait composition",
    8: "A lone donkey standing at the base of tall ancient stone city "
       "gates at dusk, trampled palm branches scattered on the ground "
       "before it, the massive gates slowly closing, warm fading light, "
       "tall vertical portrait composition, bittersweet epic mood",
    9: "A narrow ancient stone doorway glowing with bright warm light "
       "beyond it, set into a vast towering dark stone wall, a single "
       "small silhouetted figure walking toward the narrow opening, "
       "tall vertical portrait composition, epic scale and quiet hope",
    10: "A rugged wooden cross standing in silhouette on a hilltop "
        "against a dramatic golden sunset sky breaking through heavy "
        "storm clouds, rays of light spilling downward around it, tall "
        "vertical portrait composition, epic and resolute mood",
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
