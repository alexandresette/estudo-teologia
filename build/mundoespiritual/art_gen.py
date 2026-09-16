#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador procedural das artes de "Anjos, Demônios e o Mundo Espiritual".

Sem crédito disponível na API do Gemini (esgotado em 2026-09-16, confirmado
esgotado de novo ao iniciar este livro), as ilustrações deste livro não são
pinturas de IA como as de Divinamente. São composições geométricas geradas
por código: fundo com brilho radial, anéis concêntricos, um símbolo de linha
por capítulo e uma leve textura de grão, no mesmo espírito visual que a capa
do PDF de origem já usava (círculos dourados sobre azul-marinho). Como toda
composição é centrada e simétrica por construção, o corte automático
object-fit:cover do site (que despreza ~60% da largura da imagem) nunca
perde o motivo principal -- ao contrário do que aconteceu com as pinturas
figurativas de Divinamente, aqui não existe "sujeito" que possa cair fora
do quadro.

Quando o crédito do Gemini for recarregado, essas imagens podem ser
substituídas por pinturas geradas, sem mudar o pipeline: basta trocar os
arquivos em images_jpg/ e cover.jpg.
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"
F_TITLE = os.path.join(FONT_DIR, "BigShoulders-Bold.ttf")
F_SUBTITLE = os.path.join(FONT_DIR, "IBMPlexSerif-Italic.ttf")
F_LABEL = os.path.join(FONT_DIR, "WorkSans-Bold.ttf")
F_AUTHOR = os.path.join(FONT_DIR, "IBMPlexSerif-Regular.ttf")


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def radial_bg(w, h, base_rgb, glow_rgb, cx=0.5, cy=0.46, radius=0.75, glow_strength=1.0):
    """Fundo com brilho radial suave (numpy, sem banding)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xx = (xx / w - cx) / 1.0
    yy = (yy / h - cy) * (w / h)
    dist = np.sqrt(xx ** 2 + yy ** 2) / radius
    dist = np.clip(dist, 0, 1)
    t = (1 - dist) ** 1.6
    t = np.clip(t * glow_strength, 0, 1)
    base = np.array(base_rgb, dtype=np.float32)
    glow = np.array(glow_rgb, dtype=np.float32)
    img = base[None, None, :] * (1 - t[..., None]) + glow[None, None, :] * t[..., None]
    # leve gradiente vertical extra (mais escuro embaixo, como estúdio)
    vig = 1 - 0.16 * (yy - yy.min()) / (yy.max() - yy.min())
    img = img * vig[..., None]
    return np.clip(img, 0, 255).astype(np.uint8)


def add_rings(img, cx, cy, base_r, n=6, color=(230, 195, 130), max_alpha=70, width=2, gap=0.62):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    r = base_r
    for i in range(n):
        a = max(0, int(max_alpha * (1 - i / n)))
        bbox = [cx - r, cy - r * (h / w) * 0.001 - r, cx + r, cy + r]
        # manter proporcao circular real (nao elipse) usando mesmo raio em x/y de pixels
        bbox = [cx - r, cy - r, cx + r, cy + r]
        d.ellipse(bbox, outline=color + (a,), width=width)
        r *= (1 + gap)
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.6))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"), (0, 0))
    return img


def add_stars(img, n, color=(240, 228, 195), seed=0):
    rnd = random.Random(seed)
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.uniform(0.5, 1.8)
        a = int(rnd.uniform(40, 160))
        d.ellipse([x - r, y - r, x + r, y + r], fill=color + (a,))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"), (0, 0))
    return img


def add_grain(img, amount=10, seed=0):
    rnd = np.random.default_rng(seed)
    arr = np.array(img).astype(np.int16)
    noise = rnd.normal(0, amount, arr.shape[:2])[..., None]
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def add_rays(img, cx, cy, n_rays, color, max_len, spread_deg=360, start_deg=0,
             max_alpha=46, seed=0, width_range=(2, 6)):
    rnd = random.Random(seed)
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(n_rays):
        ang = math.radians(start_deg + spread_deg * (i / max(1, n_rays - 1)) + rnd.uniform(-4, 4))
        length = max_len * rnd.uniform(0.55, 1.0)
        x2 = cx + length * math.cos(ang)
        y2 = cy + length * math.sin(ang)
        a = int(max_alpha * rnd.uniform(0.4, 1.0))
        wdt = rnd.uniform(*width_range)
        d.line([cx, cy, x2, y2], fill=color + (a,), width=int(wdt))
    overlay = overlay.filter(ImageFilter.GaussianBlur(3))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"), (0, 0))
    return img


# ---------- motivos de linha por capítulo (desenhados com primitives do PIL) ----------

def motif_crown(d, cx, cy, s, color, alpha):
    pts = []
    n_spikes = 5
    base_y = cy + s * 0.35
    band_y = cy + s * 0.55
    top_ys = []
    xs = np.linspace(cx - s * 0.85, cx + s * 0.85, n_spikes * 2 + 1)
    pts = [(xs[0], band_y)]
    for i in range(n_spikes):
        x_l, x_m, x_r = xs[2 * i], xs[2 * i + 1], xs[2 * i + 2]
        peak_h = s * (0.75 if i % 2 == 0 else 0.55)
        pts.append((x_m, cy - peak_h))
        pts.append((x_r, band_y))
    pts.append((xs[-1], band_y))
    pts.append((xs[-1], base_y))
    pts.append((xs[0], base_y))
    d.line(pts, fill=color + (alpha,), width=6, joint="curve")
    d.line([(xs[0], base_y), (xs[-1], base_y)], fill=color + (alpha,), width=6)
    # joia central
    d.ellipse([cx - s * 0.05, cy - s * 0.1, cx + s * 0.05, cy], outline=color + (alpha,), width=5)


def motif_eye(d, cx, cy, s, color, alpha):
    w_ = s * 1.5
    h_ = s * 0.7
    d.arc([cx - w_, cy - h_, cx + w_, cy + h_], 200, 340, fill=color + (alpha,), width=6)
    d.arc([cx - w_, cy - h_, cx + w_, cy + h_], 20, 160, fill=color + (alpha,), width=6)
    d.ellipse([cx - s * 0.28, cy - s * 0.28, cx + s * 0.28, cy + s * 0.28], outline=color + (alpha,), width=6)
    d.ellipse([cx - s * 0.09, cy - s * 0.09, cx + s * 0.09, cy + s * 0.09], fill=color + (alpha,))
    for ang in range(0, 360, 30):
        r1, r2 = s * 0.9, s * 1.25
        a = math.radians(ang)
        d.line([cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                cx + r2 * math.cos(a), cy + r2 * math.sin(a)], fill=color + (int(alpha * 0.6),), width=3)


def motif_bow(d, cx, cy, s, color, alpha):
    d.arc([cx - s, cy - s * 0.2, cx + s, cy + s * 1.4], 200, 340, fill=color + (alpha,), width=7)
    d.line([cx, cy - s * 1.3, cx, cy - s * 0.35], fill=color + (int(alpha * 0.85),), width=6)
    for dx in (-s * 0.22, s * 0.22):
        d.line([cx, cy - s * 0.35, cx + dx, cy + s * 0.05], fill=color + (int(alpha * 0.7),), width=5)


def motif_wings(d, cx, cy, s, color, alpha):
    for side in (-1, 1):
        pts = []
        for i in range(6):
            t = i / 5
            fx = cx + side * s * (0.15 + 1.15 * t)
            fy = cy - s * 0.55 * math.sin(t * math.pi * 0.85) + s * 0.1
            pts.append((fx, fy))
        d.line(pts, fill=color + (alpha,), width=6, joint="curve")
        for i in range(1, 6):
            t = i / 5
            fx = cx + side * s * (0.15 + 1.15 * t)
            fy = cy - s * 0.55 * math.sin(t * math.pi * 0.85) + s * 0.1
            bx = cx + side * s * 0.1
            by = cy + s * 0.25
            d.line([bx, by, fx, fy], fill=color + (int(alpha * 0.55),), width=3)


def motif_fracture(d, cx, cy, s, color, alpha):
    rnd = random.Random(7)
    x, y = cx - s * 0.9, cy - s * 0.9
    pts = [(x, y)]
    for _ in range(7):
        x += s * rnd.uniform(0.18, 0.3)
        y += s * rnd.uniform(0.18, 0.3) * rnd.choice([-1, 1])
        pts.append((x, y))
    d.line(pts, fill=color + (alpha,), width=5, joint="curve")
    # feixe reto atravessando
    d.line([cx - s * 1.3, cy + s * 0.9, cx + s * 1.3, cy - s * 0.9], fill=color + (int(alpha * 0.9),), width=9)


def motif_house(d, cx, cy, s, color, alpha):
    d.line([cx - s * 0.9, cy + s * 0.55, cx - s * 0.9, cy - s * 0.05,
            cx, cy - s * 0.75, cx + s * 0.9, cy - s * 0.05, cx + s * 0.9, cy + s * 0.55,
            cx - s * 0.9, cy + s * 0.55], fill=color + (alpha,), width=6, joint="curve")
    d.rectangle([cx - s * 0.18, cy + s * 0.05, cx + s * 0.18, cy + s * 0.55],
                outline=color + (alpha,), width=5)


def motif_pillar(d, cx, cy, s, color, alpha):
    d.line([cx, cy - s * 1.1, cx, cy + s * 0.9], fill=color + (alpha,), width=9)
    d.line([cx - s * 0.35, cy + s * 0.9, cx + s * 0.35, cy + s * 0.9], fill=color + (alpha,), width=8)
    d.line([cx - s * 0.3, cy - s * 1.1, cx + s * 0.3, cy - s * 1.1], fill=color + (alpha,), width=8)
    for ang, ln in [(-160, 0.5), (160, 0.55), (-20, 0.45), (20, 0.5)]:
        a = math.radians(ang)
        d.line([cx + s * 0.4 * math.cos(a), cy + s * 0.2 * math.sin(a) - s * 0.1,
                cx + s * (0.4 + ln) * math.cos(a), cy + s * (0.2 + ln) * math.sin(a) - s * 0.1],
               fill=color + (int(alpha * 0.55),), width=3)


MOTIFS = {
    "crown": motif_crown,
    "eye": motif_eye,
    "bow": motif_bow,
    "wings": motif_wings,
    "fracture": motif_fracture,
    "house": motif_house,
    "pillar": motif_pillar,
}


def make_chapter_art(path, w, h, base_hex, glow_hex, motif, seed=0, ring_color=None):
    base = _hex(base_hex)
    glow = _hex(glow_hex)
    arr = radial_bg(w, h, base, glow, cx=0.5, cy=0.46, radius=0.8)
    img = Image.fromarray(arr).convert("RGB")

    cx, cy = w * 0.5, h * 0.46
    ring_col = ring_color or tuple(min(255, c + 40) for c in glow)
    img = add_rings(img, cx, cy, base_r=h * 0.16, n=7, color=ring_col, max_alpha=55, width=2, gap=0.5)
    img = add_rays(img, cx, cy, n_rays=18, color=tuple(min(255, c + 25) for c in glow),
                    max_len=max(w, h) * 0.75, max_alpha=30, seed=seed)

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    s = h * 0.17
    motif_col = tuple(min(255, c + 55) for c in glow)
    MOTIFS[motif](d, cx, cy, s, motif_col, 235)
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.4))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    img = add_stars(img, n=140, seed=seed + 1)
    img = add_grain(img, amount=7, seed=seed + 2)
    img = img.filter(ImageFilter.GaussianBlur(0.3))
    img.save(path, "JPEG", quality=90)
    return path


def _fit_text(draw, text, font_path, max_width, start_size, min_size=18):
    size = start_size
    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(font_path, min_size)


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


def make_cover(path, w, h, title, subtitle, author, base_hex="#070a14", glow_hex="#d8b46a", seed=99):
    base = _hex(base_hex)
    glow = _hex(glow_hex)
    arr = radial_bg(w, h, base, glow, cx=0.5, cy=0.33, radius=0.62, glow_strength=1.15)
    img = Image.fromarray(arr).convert("RGB")
    cx, cy = w * 0.5, h * 0.33

    img = add_rings(img, cx, cy, base_r=h * 0.07, n=10, color=tuple(min(255, c + 35) for c in glow),
                     max_alpha=95, width=2, gap=0.34)
    img = add_rays(img, cx, cy, n_rays=26, color=tuple(min(255, c + 30) for c in glow),
                    max_len=max(w, h) * 0.95, max_alpha=42, seed=seed, width_range=(2, 7))
    img = add_stars(img, n=220, seed=seed + 1)

    # véu escuro na metade inferior pra sustentar o texto
    veil = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(veil)
    for y in range(h):
        t = max(0, (y - h * 0.48) / (h * 0.52))
        vd.line([(0, y), (w, y)], fill=int(160 * min(1, t)))
    dark = Image.new("RGB", (w, h), (5, 6, 12))
    img = Image.composite(dark, img, veil)

    img = add_grain(img, amount=6, seed=seed + 2)

    draw = ImageDraw.Draw(img)
    cream = (238, 227, 202)
    gold = (223, 186, 122)

    # kicker (com letter-spacing manual, largura total calculada antes de centralizar)
    kicker = "SÉRIE DECLARAÇÕES PROFÉTICAS"
    f_kicker = ImageFont.truetype(F_LABEL, int(w * 0.024))
    letter_gap = w * 0.014
    char_widths = [draw.textbbox((0, 0), ch, font=f_kicker)[2] for ch in kicker]
    total_w = sum(char_widths) + letter_gap * (len(kicker) - 1)
    ky = h * 0.545
    xk = (w - total_w) / 2
    for ch, cw in zip(kicker, char_widths):
        draw.text((xk, ky), ch, font=f_kicker, fill=gold)
        xk += cw + letter_gap
    draw.line([(w * 0.5 - w * 0.09, ky + h * 0.028), (w * 0.5 + w * 0.09, ky + h * 0.028)], fill=gold, width=2)

    # titulo grande (BigShoulders, condensado, maiusculo)
    words = title.upper().split(" ")
    f_title = ImageFont.truetype(F_TITLE, int(w * 0.135))
    lines = _wrap_lines(draw, words, f_title, w * 0.86)
    while True:
        total_h = 0
        line_boxes = []
        for ln in lines:
            b = draw.textbbox((0, 0), ln, font=f_title)
            line_boxes.append(b)
            total_h += (b[3] - b[1]) * 1.06
        if total_h <= h * 0.30 or f_title.size <= 40:
            break
        f_title = ImageFont.truetype(F_TITLE, f_title.size - 4)
        lines = _wrap_lines(draw, words, f_title, w * 0.86)

    ty = h * 0.60
    for ln in lines:
        b = draw.textbbox((0, 0), ln, font=f_title)
        lw = b[2] - b[0]
        lh = b[3] - b[1]
        draw.text(((w - lw) / 2, ty), ln, font=f_title, fill=cream)
        ty += lh * 1.08

    # subtitulo
    f_sub = ImageFont.truetype(F_SUBTITLE, int(w * 0.032))
    sub_lines = _wrap_lines(draw, subtitle.split(" "), f_sub, w * 0.7)
    ty += h * 0.018
    for ln in sub_lines:
        b = draw.textbbox((0, 0), ln, font=f_sub)
        lw = b[2] - b[0]
        draw.text(((w - lw) / 2, ty), ln, font=f_sub, fill=(214, 205, 184))
        ty += (b[3] - b[1]) * 1.35

    # linha + autor no rodape
    ly = h * 0.93
    draw.line([(w * 0.5 - w * 0.1, ly), (w * 0.5 + w * 0.1, ly)], fill=gold, width=2)
    f_auth = ImageFont.truetype(F_AUTHOR, int(w * 0.028))
    ab = draw.textbbox((0, 0), author, font=f_auth)
    draw.text(((w - (ab[2] - ab[0])) / 2, ly + h * 0.015), author, font=f_auth, fill=cream)

    img.save(path, "JPEG", quality=93)
    return path
