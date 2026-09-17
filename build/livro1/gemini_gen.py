#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera as 7 ilustracoes internas do resumo de "O Poder de Ser Mulher"
com o Gemini (gemini-3-pro-image), no estilo lilas/roxo das referencias
que o Xande mandou (aquarela suave, nanquim/sumi-e, silhueta feminina,
lua, coracao, pomba, abraco, tom espiritual e intimista).

A capa e a ultima pagina NAO sao geradas aqui -- sao as paginas reais
do livro fisico (cover.jpg / lastpage.jpg), extraidas sem alteracao.

Uso: export GEMINI_API_KEY=... && python3 gemini_gen.py
Gera images_jpg/ch1..7.jpg em retrato (3:4) -- a pagina de arte do site e'
um container retrato (460x640, razao ~0.72) com object-fit:cover, entao
gerar em paisagem cortaria o objeto principal pras laterais (foi o que
aconteceu na primeira geracao de outro livro desta biblioteca). 3:4
(0.75) e' quase igual a razao da pagina, corte minimo.
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
    ", soft dreamy watercolor and ink-wash illustration, muted lavender "
    "and violet monochrome palette with warm gold light accents, gentle "
    "feminine and spiritual mood, delicate flowing brushwork, tranquil "
    "atmosphere, subtle paper texture, no text, no watermark, no logo, "
    "no signature, no calligraphy characters"
)

# As paginas de arte do site sao um container RETRATO (460x640, razao
# ~0.72), nao paisagem -- a imagem entra com object-fit:cover, entao tudo
# que nao estiver dentro da faixa vertical central acaba cortado nas
# laterais. Por isso os prompts abaixo pedem composicao VERTICAL, com o
# elemento principal empilhado no centro (nao espalhado de ponta a ponta
# horizontalmente), e geramos em "3:4" (0.75), quase igual a razao real da
# pagina -- corte minimo, sem depender de sorte no enquadramento.
CHAPTER_PROMPTS = {
    1: "A lone feminine silhouette standing centered at a quiet threshold, "
       "one side of the frame faintly turbulent and shadowed like a "
       "receding dark storm, the other side calm and glowing with soft "
       "violet light and a single white dove flying upward, the figure "
       "centered exactly between both, vertical portrait composition, "
       "soft watercolor illustration, tranquil and hopeful mood",
    2: "A feminine silhouette in flowing robes centered in frame, arms "
       "gently open, standing in soft violet clouds with warm golden "
       "light rays pouring down from above, a white dove descending "
       "directly toward her, delicate watercolor brushwork, tall "
       "vertical portrait composition, serene and reverent mood",
    3: "A small feminine silhouette held in a warm, gentle embrace from "
       "behind by a larger radiant figure of soft golden light, both "
       "centered in frame against a deep violet background, the light "
       "wrapping protectively around her shoulders, tender watercolor "
       "illustration, tall vertical portrait composition, quiet and "
       "secure mood",
    4: "A single glowing open book resting at the center of the frame, "
       "soft golden light rising from its pages like gentle flame, a "
       "delicate flowering vine growing up and around it, muted violet "
       "ink-wash background in the style of a sumi-e painting, tall "
       "vertical portrait composition, wise and tranquil mood",
    5: "A feminine hand at the bottom of the frame gently releasing a "
       "single small glowing seed of light upward, the light multiplying "
       "into a soft trail of small stars rising and spreading toward the "
       "top of the frame, deep violet night sky background, delicate "
       "watercolor illustration, tall vertical portrait composition, "
       "hopeful and generous mood",
    6: "A small warmly lit window glowing softly at the base of a quiet "
       "house silhouette, the light through the window shaped gently "
       "like a heart, a vast violet dusk sky full of soft stars above, "
       "muted watercolor illustration, tall vertical portrait "
       "composition, tender and homely mood",
    7: "A feminine silhouette standing on a gentle hilltop at the center "
       "of the frame, arms open wide, facing a bright dawn breaking "
       "through soft violet clouds on the horizon, warm golden light "
       "spilling upward and outward around her, delicate watercolor "
       "illustration, tall vertical portrait composition, luminous and "
       "resolute mood",
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
