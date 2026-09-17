#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador procedural das artes de "Anjos, Demônios e o Mundo Espiritual".

Sem crédito disponível na API do Gemini (esgotado, confirmado de novo em
2026-09-17), as ilustrações deste livro não são pinturas de IA. São cenas
de silhueta construídas por código: céu com gradiente e nuvens, uma linha
de horizonte com colinas em camadas, feixes de luz, e uma figura ou objeto
central em silhueta (coroa sobre um trono, uma figura ajoelhada, asas em
voo, um raio partindo a escuridão, uma casa na colina, uma figura de pé).
Cada cena é centrada no eixo horizontal por construção, o que evita o
mesmo problema de enquadramento que as pinturas do Divinamente tiveram
com o corte automático object-fit:cover do site.

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


def _lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


# ---------- céu, horizonte, nuvens, raios ----------

def sky_gradient(w, h, top_rgb, mid_rgb, glow_rgb, horizon_y):
    """Céu em três paradas: topo escuro, meio, e um halo quente no horizonte."""
    yy = np.linspace(0, 1, h).astype(np.float32)
    colors = np.zeros((h, 3), dtype=np.float32)
    hz = horizon_y / h
    for y in range(h):
        t = yy[y]
        if t < hz:
            local = t / max(hz, 1e-6)
            c = _lerp(top_rgb, mid_rgb, local ** 1.3)
        else:
            local = (t - hz) / max(1 - hz, 1e-6)
            c = _lerp(mid_rgb, glow_rgb, (1 - local) ** 1.6)
        colors[y] = c
    arr = np.repeat(colors[:, None, :], w, axis=1)
    # halo horizontal quente centrado
    xx = np.linspace(-1, 1, w).astype(np.float32)
    halo = np.exp(-(xx ** 2) / 0.55)[None, :, None]
    band = np.exp(-((yy - hz) ** 2) / 0.02)[:, None, None]
    glow = np.array(glow_rgb, dtype=np.float32)
    arr = arr + halo * band * (glow[None, None, :] - arr) * 0.9
    return np.clip(arr, 0, 255).astype(np.uint8)


def add_clouds(img, horizon_y, color, n=9, seed=0, band_top=0.08, band_bot=0.55, alpha_range=(18, 46)):
    rnd = random.Random(seed)
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for _ in range(n):
        cx = rnd.uniform(0, w)
        cy = horizon_y * rnd.uniform(band_top, band_bot)
        rw = rnd.uniform(w * 0.12, w * 0.32)
        rh = rw * rnd.uniform(0.16, 0.3)
        a = int(rnd.uniform(*alpha_range))
        blob = Image.new("RGBA", (int(rw * 2.4), int(rh * 2.4)), (0, 0, 0, 0))
        bd = ImageDraw.Draw(blob)
        for i in range(5):
            dx = rnd.uniform(-rw * 0.5, rw * 0.5)
            dy = rnd.uniform(-rh * 0.4, rh * 0.4)
            rr = rnd.uniform(rw * 0.35, rw * 0.6)
            bd.ellipse([blob.width / 2 + dx - rr, blob.height / 2 + dy - rr * 0.55,
                        blob.width / 2 + dx + rr, blob.height / 2 + dy + rr * 0.55],
                       fill=color + (a,))
        blob = blob.filter(ImageFilter.GaussianBlur(rw * 0.06))
        overlay.alpha_composite(blob, (int(cx - blob.width / 2), int(cy - blob.height / 2)))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"), (0, 0))
    return img


def add_god_rays(img, cx, cy, color, n=14, max_len=900, spread=100, alpha=34, seed=0, upward=False):
    rnd = random.Random(seed)
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    base_ang = -90 if upward else 90
    for i in range(n):
        ang = math.radians(base_ang + rnd.uniform(-spread, spread))
        length = max_len * rnd.uniform(0.55, 1.0)
        x2 = cx + length * math.sin(ang)
        y2 = cy - length * math.cos(ang) if not upward else cy + length * math.cos(ang)
        wdt = rnd.uniform(10, 34)
        a = int(alpha * rnd.uniform(0.5, 1.0))
        poly_w = wdt
        dx = math.cos(ang) * poly_w
        dy = math.sin(ang) * poly_w
        d.polygon([(cx - dx, cy + dy), (cx + dx, cy - dy), (x2 + dx * 0.15, y2 - dy * 0.15),
                   (x2 - dx * 0.15, y2 + dy * 0.15)], fill=color + (a,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(6))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"), (0, 0))
    return img


def add_sun(img, cx, cy, r, color, glow_r=None, alpha=230):
    glow_r = glow_r or r * 3.2
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    steps = 8
    for i in range(steps, 0, -1):
        rr = glow_r * i / steps
        a = int(alpha * 0.16 * (1 - i / steps + 0.15))
        od.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(glow_r * 0.06))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    return img


def hill_layer(w, h, horizon_y, amplitude, color, seed=0, n_pts=9):
    rnd = random.Random(seed)
    pts = [(0, h)]
    xs = np.linspace(0, w, n_pts)
    for x in xs:
        y = horizon_y + rnd.uniform(-amplitude, amplitude * 0.4)
        pts.append((x, y))
    pts.append((w, h))
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.polygon(pts, fill=color + (255,))
    return layer, pts


def add_hills(img, horizon_y, colors, seed=0):
    w, h = img.size
    n = len(colors)
    for i, col in enumerate(colors):
        amp = (h * 0.05) * (n - i) / n + h * 0.015
        hy = horizon_y + i * (h * 0.05)
        layer, _ = hill_layer(w, h, hy, amp, col, seed=seed + i, n_pts=7 + i)
        img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))
    return img


def add_stars(img, n, color=(240, 228, 195), seed=0, y_max=None):
    rnd = random.Random(seed)
    w, h = img.size
    y_max = y_max or h
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, y_max)
        r = rnd.uniform(0.5, 1.7)
        a = int(rnd.uniform(50, 175))
        d.ellipse([x - r, y - r, x + r, y + r], fill=color + (a,))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"), (0, 0))
    return img


def add_grain(img, amount=8, seed=0):
    rnd = np.random.default_rng(seed)
    arr = np.array(img).astype(np.int16)
    noise = rnd.normal(0, amount, arr.shape[:2])[..., None]
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def vignette_soft(img, strength=0.28):
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xx = (xx / w - 0.5) * 2
    yy = (yy / h - 0.5) * 2
    dist = np.sqrt(xx ** 2 + yy ** 2)
    fall = np.clip(1 - strength * np.clip(dist - 0.55, 0, None), 0, 1)
    arr = np.array(img).astype(np.float32) * fall[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ---------- silhuetas de figura humana ----------

def _limb(d, x1, y1, x2, y2, w1, w2, color):
    ang = math.atan2(y2 - y1, x2 - x1)
    nx, ny = math.sin(ang), -math.cos(ang)
    pts = [
        (x1 + nx * w1, y1 + ny * w1), (x2 + nx * w2, y2 + ny * w2),
        (x2 - nx * w2, y2 - ny * w2), (x1 - nx * w1, y1 - ny * w1),
    ]
    d.polygon(pts, fill=color)
    d.ellipse([x1 - w1, y1 - w1, x1 + w1, y1 + w1], fill=color)
    d.ellipse([x2 - w2, y2 - w2, x2 + w2, y2 + w2], fill=color)


def draw_figure_standing(d, cx, foot_y, total_h, color, arms="down"):
    """total_h e a altura da figura inteira, dos pes ao topo da cabeca --
    proporcoes fixas (~7.5 cabecas), entao a figura sempre cabe no quadro
    partindo de foot_y pra cima, nunca corta a cabeca."""
    head_r = total_h * 0.065
    head_cy = foot_y - total_h + head_r
    d.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], fill=color)
    neck_y = head_cy + head_r * 1.25
    shoulder_y = neck_y + total_h * 0.015
    hip_y = foot_y - total_h * 0.46
    d.polygon([
        (cx - total_h * 0.15, shoulder_y), (cx + total_h * 0.15, shoulder_y),
        (cx + total_h * 0.095, hip_y), (cx - total_h * 0.095, hip_y),
    ], fill=color)
    _limb(d, cx - total_h * 0.065, hip_y, cx - total_h * 0.085, foot_y, total_h * 0.045, total_h * 0.032, color)
    _limb(d, cx + total_h * 0.065, hip_y, cx + total_h * 0.085, foot_y, total_h * 0.045, total_h * 0.032, color)
    if arms == "down":
        _limb(d, cx - total_h * 0.14, shoulder_y + total_h * 0.02, cx - total_h * 0.18, hip_y + total_h * 0.08,
              total_h * 0.036, total_h * 0.026, color)
        _limb(d, cx + total_h * 0.14, shoulder_y + total_h * 0.02, cx + total_h * 0.18, hip_y + total_h * 0.08,
              total_h * 0.036, total_h * 0.026, color)
    elif arms == "raised":
        _limb(d, cx - total_h * 0.14, shoulder_y + total_h * 0.015, cx - total_h * 0.3, shoulder_y - total_h * 0.35,
              total_h * 0.036, total_h * 0.026, color)
        _limb(d, cx + total_h * 0.14, shoulder_y + total_h * 0.015, cx + total_h * 0.3, shoulder_y - total_h * 0.35,
              total_h * 0.036, total_h * 0.026, color)
    return {"head_r": head_r, "head_cy": head_cy, "shoulder_y": shoulder_y, "hip_y": hip_y}


def _quad_bezier(p0, p1, p2, n=16):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


def draw_figure_kneeling(d, cx, ground_y, scale, color):
    """Figura prostrada: quadril alto (sentado sobre os calcanhares), dorso
    curvado para baixo e à frente, cabeça baixa quase tocando o chão, braço
    estendido no chão. Postura de reverência profunda, lida como corpo
    humano curvado, não como bloco geométrico solto."""
    s = scale
    hip = (cx - s * 0.18, ground_y - s * 0.34)
    shoulder = (cx + s * 0.04, ground_y - s * 0.20)
    head_c = (cx + s * 0.32, ground_y - s * 0.09)
    head_r = s * 0.09

    # base: pernas dobradas sob o quadril, sentado sobre os calcanhares
    d.polygon([
        (cx - s * 0.42, ground_y), (cx - s * 0.38, ground_y - s * 0.05),
        (hip[0] - s * 0.08, hip[1] + s * 0.01), (hip[0] + s * 0.14, hip[1] + s * 0.03),
        (cx - s * 0.02, ground_y - s * 0.02), (cx - s * 0.06, ground_y),
    ], fill=color)

    # dorso: curva única do quadril (ponto mais alto, atrás) até o ombro
    # (baixo, à frente) -- arqueado para baixo, reverência profunda
    spine_top = _quad_bezier(
        (hip[0] - s * 0.02, hip[1] - s * 0.02), (cx + s * 0.06, ground_y - s * 0.30), shoulder, n=14
    )
    spine_bot = _quad_bezier(
        (hip[0] + s * 0.16, hip[1] + s * 0.03), (cx + s * 0.18, ground_y - s * 0.20),
        (shoulder[0] + s * 0.09, shoulder[1] + s * 0.09), n=14
    )
    torso = spine_top + list(reversed(spine_bot))
    d.polygon(torso, fill=color)

    # braço apoiado à frente no chão (passa perto da cabeça, conectando a
    # silhueta) + cabeça baixa, quase encostando no chão
    _limb(d, shoulder[0] + s * 0.05, shoulder[1] + s * 0.08, cx + s * 0.50, ground_y - s * 0.01,
          s * 0.046, s * 0.03, color)
    d.ellipse([head_c[0] - head_r, head_c[1] - head_r, head_c[0] + head_r, head_c[1] + head_r], fill=color)
    return {"head_r": head_r, "head_cy": head_c[1]}


def draw_wings(d, cx, cy, span, color, spread=1.0):
    for side in (-1, 1):
        pts = [(cx, cy + span * 0.08)]
        n = 7
        for i in range(1, n + 1):
            t = i / n
            fx = cx + side * span * (0.08 + 0.92 * t) * spread
            fy = cy - span * 0.62 * math.sin(t * math.pi * 0.92) * spread + span * 0.05
            pts.append((fx, fy))
        for i in range(n, 0, -1):
            t = i / n
            fx = cx + side * span * (0.05 + 0.8 * t) * spread
            fy = cy - span * 0.4 * math.sin(t * math.pi * 0.85) * spread + span * 0.16
            pts.append((fx, fy))
        d.polygon(pts, fill=color)
        # penas (linhas mais claras por cima, sutil)
    return


# ---------- cenas por capítulo ----------

def scene_throne(d, w, h, horizon_y, color, glow_color):
    cx = w / 2
    base_y = horizon_y - h * 0.02
    # trono: base + encosto
    seat_w, seat_h = w * 0.12, h * 0.05
    back_w, back_h = w * 0.09, h * 0.22
    d.polygon([(cx - seat_w, base_y), (cx + seat_w, base_y),
               (cx + seat_w * 0.85, base_y - seat_h), (cx - seat_w * 0.85, base_y - seat_h)], fill=color)
    back_top = base_y - seat_h - back_h
    d.polygon([(cx - back_w, base_y - seat_h), (cx + back_w, base_y - seat_h),
               (cx + back_w * 0.7, back_top), (cx - back_w * 0.7, back_top)], fill=color)
    # arcos laterais do trono
    for side in (-1, 1):
        d.polygon([
            (cx + side * back_w, base_y - seat_h),
            (cx + side * (back_w + w * 0.015), base_y - seat_h - back_h * 0.6),
            (cx + side * back_w * 0.7, back_top),
        ], fill=color)
    # coroa flutuando acima, dourada e luminosa
    crown_cy = back_top - h * 0.09
    crown_w, crown_h = w * 0.055, h * 0.05
    n_spikes = 5
    xs = np.linspace(cx - crown_w, cx + crown_w, n_spikes * 2 + 1)
    pts = [(xs[0], crown_cy + crown_h * 0.4)]
    for i in range(n_spikes):
        peak = crown_h * (0.9 if i % 2 == 0 else 0.6)
        pts.append((xs[2 * i + 1], crown_cy - peak))
        pts.append((xs[2 * i + 2], crown_cy + crown_h * 0.4))
    pts.append((xs[-1], crown_cy + crown_h))
    pts.append((xs[0], crown_cy + crown_h))
    d.polygon(pts, fill=glow_color)


def scene_sunrise_eye(img, d, w, h, horizon_y, sun_color, lid_color):
    cx, cy = w / 2, horizon_y
    r = h * 0.16
    add_sun(img, cx, cy, r, sun_color, glow_r=r * 3.6)
    lid_w, lid_h = r * 2.6, r * 1.55
    d.arc([cx - lid_w, cy - lid_h, cx + lid_w, cy + lid_h], 200, 340, fill=lid_color, width=int(h * 0.012))
    d.arc([cx - lid_w, cy - lid_h * 0.4, cx + lid_w, cy + lid_h * 1.5], 20, 160, fill=lid_color, width=int(h * 0.012))


def scene_kneeling(d, w, h, horizon_y, color):
    cx = w / 2
    draw_figure_kneeling(d, cx, horizon_y, h * 0.5, color)


def scene_wings_figure(d, w, h, horizon_y, color):
    cx = w / 2
    foot_y = horizon_y + h * 0.02
    total_h = h * 0.34
    info = draw_figure_standing(d, cx, foot_y, total_h, color, arms="raised")
    draw_wings(d, cx, info["shoulder_y"] + total_h * 0.04, h * 0.46, color, spread=1.0)
    # cabeca e ombros por cima das asas, pra leitura de figura alada, nao só asas
    head_r = info["head_r"]
    hc = info["head_cy"]
    d.ellipse([cx - head_r, hc - head_r, cx + head_r, hc + head_r], fill=color)


def scene_fracture(img, d, w, h, horizon_y, crack_color, beam_color):
    """Um raio (zigue-zague nitido, poucos segmentos) rompendo o ceu escuro
    e caindo sobre uma fenda equivalente no chao -- verdade cortando a
    mentira, luz reta contra a escuridao irregular."""
    rnd = random.Random(11)
    cx = w / 2

    # feixe reto principal, de canto a canto, largo e translucido
    x_top, y_top = cx - w * 0.16, h * 0.04
    x_bot, y_bot = cx + w * 0.14, horizon_y * 0.99
    beam_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam_overlay)
    bd.line([x_top, y_top, x_bot, y_bot], fill=beam_color + (150,), width=int(h * 0.05))
    beam_overlay = beam_overlay.filter(ImageFilter.GaussianBlur(h * 0.012))
    img.paste(Image.alpha_composite(img.convert("RGBA"), beam_overlay).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    d.line([x_top, y_top, x_bot, y_bot], fill=beam_color, width=int(h * 0.016))

    # fenda no chao, bem no ponto onde o feixe toca o horizonte -- terra
    # rachada (a mentira) cortada pela luz reta (a verdade), sem tentar
    # desenhar um raio solto no ceu (lia como pernas de inseto)
    gx, gy = x_bot, y_bot
    pts = [(gx, gy)]
    x, y = gx, gy
    for i in range(5):
        x += rnd.uniform(-w * 0.05, w * 0.03) - w * 0.02
        y += rnd.uniform(h * 0.012, h * 0.03)
        pts.append((x, y))
    d.line(pts, fill=crack_color, width=int(h * 0.01), joint="curve")
    for p in pts[1:-1]:
        bx = p[0] + rnd.uniform(-w * 0.04, w * 0.06)
        by = p[1] + rnd.uniform(h * 0.01, h * 0.025)
        d.line([p, (bx, by)], fill=crack_color, width=int(h * 0.005))


def scene_house(d, w, h, horizon_y, color, glow_color):
    cx = w / 2
    base_y = horizon_y
    hw, hh = w * 0.11, h * 0.13
    roof_h = h * 0.09
    d.polygon([(cx - hw, base_y), (cx + hw, base_y), (cx + hw, base_y - hh), (cx - hw, base_y - hh)], fill=color)
    d.polygon([(cx - hw * 1.15, base_y - hh), (cx + hw * 1.15, base_y - hh), (cx, base_y - hh - roof_h)], fill=color)
    dw, dh = hw * 0.32, hh * 0.62
    d.rectangle([cx - dw / 2, base_y - dh, cx + dw / 2, base_y], fill=glow_color)
    for side in (-1, 1):
        wx = cx + side * hw * 0.55
        wy = base_y - hh * 0.62
        ww = hw * 0.26
        d.rectangle([wx - ww / 2, wy - ww / 2, wx + ww / 2, wy + ww / 2], fill=glow_color)


def scene_standing_firm(d, w, h, horizon_y, color):
    cx = w / 2
    rock_w, rock_h = w * 0.16, h * 0.05
    d.polygon([(cx - rock_w, horizon_y), (cx + rock_w, horizon_y),
               (cx + rock_w * 0.6, horizon_y - rock_h), (cx - rock_w * 0.6, horizon_y - rock_h)], fill=color)
    draw_figure_standing(d, cx, horizon_y - rock_h, h * 0.42, color, arms="down")


def scene_submission_arc(d, w, h, horizon_y, color):
    # capitulo 3: figura curvada, quase deitada em reverencia -- uso a mesma
    # pose ajoelhada mas com a cabeca mais baixa (submissao mais profunda)
    cx = w / 2
    draw_figure_kneeling(d, cx, horizon_y, h * 0.42, color)


SCENES = {
    "throne": scene_throne,
    "sunrise_eye": scene_sunrise_eye,
    "submission": scene_submission_arc,
    "wings": scene_wings_figure,
    "fracture": scene_fracture,
    "house": scene_house,
    "standing": scene_standing_firm,
}


def make_chapter_art(path, w, h, sky_top, sky_mid, sky_glow, hill_colors, scene, seed=0,
                      silhouette_color=(10, 9, 14), rim_color=None, sun_color=None):
    horizon_y = h * 0.62
    arr = sky_gradient(w, h, _hex(sky_top), _hex(sky_mid), _hex(sky_glow), horizon_y)
    img = Image.fromarray(arr).convert("RGB")

    img = add_stars(img, n=90, seed=seed + 1, y_max=horizon_y * 0.7)
    img = add_clouds(img, horizon_y, _hex(sky_mid), n=7, seed=seed + 2)
    img = add_god_rays(img, w / 2, horizon_y, tuple(min(255, c + 20) for c in _hex(sky_glow)),
                        n=16, max_len=h * 0.85, spread=95, alpha=26, seed=seed + 3)

    img = add_hills(img, horizon_y, [_hex(c) for c in hill_colors], seed=seed + 4)

    draw = ImageDraw.Draw(img)
    if scene == "sunrise_eye":
        scene_sunrise_eye(img, draw, w, h, horizon_y, _hex(sun_color or sky_glow), silhouette_color)
    elif scene == "fracture":
        scene_fracture(img, draw, w, h, horizon_y, silhouette_color, _hex(rim_color or sky_glow))
    elif scene == "throne":
        scene_throne(draw, w, h, horizon_y, silhouette_color, _hex(rim_color or sky_glow))
    elif scene == "house":
        scene_house(draw, w, h, horizon_y, silhouette_color, _hex(rim_color or sky_glow))
    else:
        SCENES[scene](draw, w, h, horizon_y, silhouette_color)

    img = add_stars(img, n=40, seed=seed + 5, y_max=horizon_y * 0.4)
    img = vignette_soft(img, strength=0.22)
    img = add_grain(img, amount=6, seed=seed + 6)
    img = img.filter(ImageFilter.GaussianBlur(0.25))
    img.save(path, "JPEG", quality=91)
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


def make_cover(path, w, h, title, subtitle, author, seed=99):
    sky_top = "#05060d"
    sky_mid = "#1b1f3a"
    sky_glow = "#e8c27a"
    horizon_y = h * 0.5
    arr = sky_gradient(w, h, _hex(sky_top), _hex(sky_mid), _hex(sky_glow), horizon_y)
    img = Image.fromarray(arr).convert("RGB")
    img = add_stars(img, n=170, seed=seed + 1, y_max=horizon_y * 0.75)
    img = add_clouds(img, horizon_y, _hex(sky_mid), n=6, seed=seed + 2, alpha_range=(14, 30))
    img = add_god_rays(img, w / 2, horizon_y, (245, 214, 150), n=22, max_len=h * 0.62,
                        spread=100, alpha=38, seed=seed + 3)
    img = add_sun(img, w / 2, horizon_y, h * 0.05, (255, 236, 190), glow_r=h * 0.24)
    img = add_hills(img, horizon_y, [(20, 16, 24), (13, 10, 16), (7, 6, 10)], seed=seed + 4)

    # trono/coroa discreta na linha do horizonte, como assinatura visual da serie
    draw = ImageDraw.Draw(img)
    scene_throne(draw, w, h, horizon_y, (8, 7, 11), (255, 232, 178))

    # veu escuro na metade inferior pra sustentar o texto
    veil = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(veil)
    for y in range(h):
        t = max(0, (y - h * 0.5) / (h * 0.5))
        vd.line([(0, y), (w, y)], fill=int(190 * min(1, t ** 0.8)))
    dark = Image.new("RGB", (w, h), (4, 4, 8))
    img = Image.composite(dark, img, veil)

    img = vignette_soft(img, strength=0.24)
    img = add_grain(img, amount=6, seed=seed + 5)

    draw = ImageDraw.Draw(img)
    cream = (238, 227, 202)
    gold = (223, 186, 122)

    kicker = "SÉRIE DECLARAÇÕES PROFÉTICAS"
    f_kicker = ImageFont.truetype(F_LABEL, int(w * 0.024))
    letter_gap = w * 0.014
    char_widths = [draw.textbbox((0, 0), ch, font=f_kicker)[2] for ch in kicker]
    total_w = sum(char_widths) + letter_gap * (len(kicker) - 1)
    ky = h * 0.555
    xk = (w - total_w) / 2
    for ch, cw in zip(kicker, char_widths):
        draw.text((xk, ky), ch, font=f_kicker, fill=gold)
        xk += cw + letter_gap
    draw.line([(w * 0.5 - w * 0.09, ky + h * 0.028), (w * 0.5 + w * 0.09, ky + h * 0.028)], fill=gold, width=2)

    words = title.upper().split(" ")
    f_title = ImageFont.truetype(F_TITLE, int(w * 0.135))
    lines = _wrap_lines(draw, words, f_title, w * 0.86)
    while True:
        total_h = 0
        for ln in lines:
            b = draw.textbbox((0, 0), ln, font=f_title)
            total_h += (b[3] - b[1]) * 1.06
        if total_h <= h * 0.29 or f_title.size <= 40:
            break
        f_title = ImageFont.truetype(F_TITLE, f_title.size - 4)
        lines = _wrap_lines(draw, words, f_title, w * 0.86)

    ty = h * 0.61
    for ln in lines:
        b = draw.textbbox((0, 0), ln, font=f_title)
        lw = b[2] - b[0]
        lh = b[3] - b[1]
        draw.text(((w - lw) / 2, ty), ln, font=f_title, fill=cream)
        ty += lh * 1.1

    f_sub = ImageFont.truetype(F_SUBTITLE, int(w * 0.032))
    sub_lines = _wrap_lines(draw, subtitle.split(" "), f_sub, w * 0.7)
    ty += h * 0.02
    for ln in sub_lines:
        b = draw.textbbox((0, 0), ln, font=f_sub)
        lw = b[2] - b[0]
        draw.text(((w - lw) / 2, ty), ln, font=f_sub, fill=(214, 205, 184))
        ty += (b[3] - b[1]) * 1.35

    ly = h * 0.935
    draw.line([(w * 0.5 - w * 0.1, ly), (w * 0.5 + w * 0.1, ly)], fill=gold, width=2)
    f_auth = ImageFont.truetype(F_AUTHOR, int(w * 0.028))
    ab = draw.textbbox((0, 0), author, font=f_auth)
    draw.text(((w - (ab[2] - ab[0])) / 2, ly + h * 0.015), author, font=f_auth, fill=cream)

    img.save(path, "JPEG", quality=93)
    return path
