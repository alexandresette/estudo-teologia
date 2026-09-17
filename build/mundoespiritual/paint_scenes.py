#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Segunda geração das artes de "Anjos, Demônios e o Mundo Espiritual".

A primeira geração (art_gen.py) era silhueta geométrica plana sobre
gradiente -- o próprio Xande apontou que ficou abstrata demais e mandou
referências: pinturas épicas, céu dramático, nuvens pesadas, feixes de luz
物 quebrando a escuridão, e uma figura humana minúscula contra uma escala
monumental. Essas referências são pintura de IA (Gemini/Midjourney-like);
sem crédito de API disponível, a aproximação mais próxima possível por
código é o "paint" skill (paintkit, aquarela procedural sobre OpenCV):
washes graduados, nuvens texturizadas em camadas, spray de luz, pinceladas
com textura -- muito mais "pintado" do que geometria plana.

Cada cena mantém a composição de "referência de escala": um céu tempestuoso
se abrindo, um facho ou brilho central, e uma figura humana pequena para dar
a sensação de vastidão. Tudo centrado no eixo horizontal por construção
(mesma razão da primeira versão: o corte automático object-fit:cover do
site nunca deve cortar o assunto principal).
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, "/mnt/skills/examples/paint")
from paintkit import Canvas, hex_rgb  # noqa: E402


# ---------------------------------------------------------------- céu/nuvem

def storm_sky(cv, w, h, top, mid, glow, horizon=0.62, mottling=0.5):
    cv.wash(0, int(h), hex_rgb(top), hex_rgb(mid), alpha=0.95, glazes=3,
            mottling=mottling, wobble=w * 0.018, softness=h * 0.06)
    cv.wash(int(h * horizon * 0.45), int(h), hex_rgb(mid), hex_rgb(glow), alpha=0.82,
            glazes=3, mottling=mottling * 0.85, wobble=w * 0.014, softness=h * 0.06)


def cloud_mass(cv, cx, cy, w_, h_, shadow, warm, base, rng, puffs=4, warm_side=1,
               body_alpha=0.16):
    # ventre escuro -- a massa da nuvem eh mais sombra que luz, pra dar peso
    for i in range(4):
        px = cx + rng.uniform(-w_ * 0.38, w_ * 0.38)
        py = cy + h_ * 0.32 + rng.uniform(-h_ * 0.05, h_ * 0.12)
        pts = cv.ellipse_points(px, py, w_ * rng.uniform(0.32, 0.48),
                                 h_ * rng.uniform(0.28, 0.4), n=12, jitter=0.1)
        cv.watercolor_blob(pts, shadow, layers=3, alpha=0.22, softness=h_ * 0.05,
                            granulation=0.5, edge=0.25)
    # borda quente fina, do lado que pega luz
    pts = cv.ellipse_points(cx + warm_side * w_ * 0.28, cy - h_ * 0.02,
                             w_ * 0.22, h_ * 0.22, n=12, jitter=0.1)
    cv.watercolor_blob(pts, warm, layers=2, alpha=0.09, softness=h_ * 0.04,
                        granulation=0.4, edge=0.15)
    # poucos volumes claros no topo, contidos -- nao um veu branco geral
    for i in range(puffs):
        px = cx + rng.uniform(-w_ * 0.3, w_ * 0.3)
        py = cy + rng.uniform(-h_ * 0.3, -h_ * 0.02)
        pts = cv.ellipse_points(px, py, w_ * rng.uniform(0.16, 0.24),
                                 h_ * rng.uniform(0.2, 0.3), n=12, jitter=0.1)
        cv.watercolor_blob(pts, base, layers=2, alpha=body_alpha, softness=h_ * 0.05,
                            depth=3, variance=0.12, granulation=0.35, edge=0.15,
                            mode="over")


def parting_clouds(cv, w, h, rng, shadow, warm, base, gap_frac=0.30, band=(0.03, 0.5),
                    n_side=2, seed_shift=0):
    """Massas de nuvem nas laterais, deixando um vão central aberto por onde a
    luz escapa -- a composição de 'céu se abrindo' das referências."""
    gap = w * gap_frac
    for side in (-1, 1):
        for i in range(n_side):
            cx = w / 2 + side * (gap / 2 + rng.uniform(w * 0.12, w * 0.34))
            cy = h * rng.uniform(*band)
            cw = rng.uniform(w * 0.3, w * 0.48)
            ch_ = cw * rng.uniform(0.4, 0.58)
            cloud_mass(cv, cx, cy, cw, ch_, shadow, warm, base, rng,
                       puffs=rng.integers(3, 5), warm_side=-side, body_alpha=0.16)
    # véu fino de nuvem alta, bem discreto
    for i in range(2):
        cx = rng.uniform(w * 0.1, w * 0.9)
        cy = h * rng.uniform(0.02, 0.1)
        cw = rng.uniform(w * 0.28, w * 0.45)
        cloud_mass(cv, cx, cy, cw, cw * 0.18, shadow, warm, base, rng, puffs=2,
                   warm_side=1, body_alpha=0.08)


def light_shaft(cv, w, h, cx, top_y, bot_y, width, color, alpha=0.5, softness=None,
                 flare_r=None, rng=None):
    """Facho de luz vertical/quase-vertical, com um brilho aberto no topo (o
    'rasgo' no céu) e um leve alargamento na base."""
    rng = rng if rng is not None else np.random.default_rng(7)
    softness = softness if softness is not None else width * 0.35
    pts = np.array([
        [cx - width * 0.22, top_y], [cx + width * 0.22, top_y],
        [cx + width * 0.55, bot_y], [cx - width * 0.55, bot_y],
    ])
    cv.watercolor_blob(pts, color, layers=5, alpha=alpha, softness=softness,
                        depth=2, variance=0.05, granulation=0.15, edge=0.0,
                        mode="over")
    flare_r = flare_r if flare_r is not None else width * 1.8
    cv.spray(cx, top_y, flare_r, flare_r * 0.6, color, count=9000, dot=flare_r * 0.02,
              alpha=0.5, falloff=1.3, softness=flare_r * 0.12, mode="over")
    # poeira de luz flutuando no facho -- pontinhos claros espalhados ao
    # longo do feixe, textura que quebra o gradiente liso
    n_mot = 90
    ts = np.sort(rng.uniform(0, 1, n_mot))
    mx = cx + rng.uniform(-width * 0.4, width * 0.4, n_mot) * (0.3 + 0.7 * ts)
    my = top_y + ts * (bot_y - top_y)
    mr = rng.uniform(width * 0.006, width * 0.018, n_mot)
    cv.scatter(mx, my, mr, color, alpha=0.55, softness=0.8, mode="over")


def rays_fan(cv, w, h, cx, cy, color, n, length, spread_deg, alpha, rng, base_ang=-90,
             width_range=(0.01, 0.03)):
    for i in range(n):
        ang = math.radians(base_ang + rng.uniform(-spread_deg, spread_deg))
        ln = length * rng.uniform(0.5, 1.0)
        x2 = cx + ln * math.cos(ang)
        y2 = cy + ln * math.sin(ang)
        wdt = w * rng.uniform(*width_range)
        cv.stroke([(cx, cy), (x2, y2)], color, width=wdt, taper=(0.1, 1.0, 0.0),
                   alpha=alpha * rng.uniform(0.6, 1.0), softness=wdt * 0.6, wobble=0.4,
                   texture=0.1, mode="over")


def distant_hills(cv, w, h, horizon_y, colors, rng):
    n = len(colors)
    for i, col in enumerate(colors):
        base_y = horizon_y + i * h * 0.045
        amp = h * 0.045 * (n - i) / n + h * 0.01
        xs = np.linspace(-w * 0.05, w * 1.05, 9 + i)
        ys = base_y - amp * (0.4 + 0.6 * np.sin(xs / (w * (0.28 + 0.08 * i)) + i * 1.3))
        ys = ys + rng.normal(0, h * 0.006, xs.shape)
        top = list(zip(xs, ys))
        pts = top + [(w * 1.05, h * 1.05), (-w * 0.05, h * 1.05)]
        cv.watercolor_blob(pts, hex_rgb(col), layers=4, alpha=0.9, softness=h * 0.01,
                            depth=3, variance=0.03, granulation=0.45, edge=0.4)


def ground_wash(cv, w, h, y0, colors):
    cv.wash(int(y0), int(h), hex_rgb(colors[0]), hex_rgb(colors[1]), alpha=0.9, glazes=3,
            mottling=0.5, wobble=w * 0.012, softness=h * 0.02)


def rock_outcrop(cv, cx, base_y, w, h, color, rng):
    pts = [
        (cx - w * 0.55, base_y), (cx - w * 0.42, base_y - h * 0.35),
        (cx - w * 0.12, base_y - h * 0.7), (cx + w * 0.08, base_y - h * 0.86),
        (cx + w * 0.3, base_y - h * 0.55), (cx + w * 0.5, base_y - h * 0.2),
        (cx + w * 0.58, base_y),
    ]
    base = cv.deform_polygon(np.array(pts), depth=3, variance=0.05)
    cv.watercolor_blob(base, color, layers=3, alpha=0.92, softness=min(h * 0.012, 5.0),
                        depth=2, variance=0.04, granulation=0.4, edge=0.55)
    return base


def birds(cv, w, h, rng, color, n=5, y_range=(0.06, 0.3), x_range=(0.15, 0.85)):
    marks = []
    for _ in range(n):
        bx = rng.uniform(w * x_range[0], w * x_range[1])
        by = rng.uniform(h * y_range[0], h * y_range[1])
        s = rng.uniform(w * 0.008, w * 0.016)
        marks.append([(bx - s, by + s * 0.45), (bx, by), (bx + s, by + s * 0.5)])
    cv.strokes(marks, color, width=max(1.5, w * 0.0015), taper=(0.5, 1.0, 0.5),
               alpha=0.6, softness=1.0, wobble=0.8)


# ------------------------------------------------------------- figura humana

def tiny_figure(cv, cx, y, scale, color, pose="standing", coat=None, shadow=None):
    """Figura minúscula (referência de escala): casaco/manto, cabeça, pernas.
    pose: standing | arms_up | kneeling | prostrate | walking"""
    coat = coat or color
    shadow = shadow or (0.15, 0.13, 0.18)
    s = scale
    if pose == "prostrate":
        cv.stroke([(cx - s * 1.6, y + s * 0.3), (cx + s * 2.0, y + s * 0.5)],
                   shadow, width=s * 0.9, taper=(1, 0.3), alpha=0.22, softness=s * 0.3)
        body = [(cx - s * 1.4, y), (cx - s * 0.5, y - s * 0.55), (cx + s * 0.3, y - s * 0.35),
                (cx + s * 1.5, y - s * 0.05), (cx + s * 1.6, y + s * 0.15), (cx - s * 1.5, y + s * 0.2)]
        cv.flat_shape(body, coat, alpha=0.95, granulation=0.2, edge=0.45, softness=s * 0.035)
        hr = s * 0.32
        cv.flat_shape(cv.ellipse_points(cx - s * 0.55, y - s * 0.62, hr, hr * 0.9, n=14),
                      shadow, alpha=0.95, granulation=0.15, edge=0.4, softness=s * 0.03)
        return
    if pose == "kneeling":
        cv.stroke([(cx - s * 0.9, y + s * 0.15), (cx + s * 1.1, y + s * 0.25)],
                   shadow, width=s * 0.7, taper=(1, 0.3), alpha=0.28, softness=s * 0.25)
        body = [(cx - s * 0.55, y), (cx - s * 0.4, y - s * 0.75), (cx + s * 0.15, y - s * 1.05),
                (cx + s * 0.5, y - s * 0.5), (cx + s * 0.35, y)]
        cv.flat_shape(body, coat, alpha=0.95, granulation=0.2, edge=0.45, softness=s * 0.035)
        hr = s * 0.3
        cv.flat_shape(cv.ellipse_points(cx + s * 0.1, y - s * 1.15, hr, hr * 0.92, n=14),
                      shadow, alpha=0.95, granulation=0.15, edge=0.4, softness=s * 0.03)
        return
    # standing / arms_up / walking: casaco em leque + pernas + cabeça
    cv.stroke([(cx - s * 0.3, y + s * 0.1), (cx + s * 0.55, y + s * 0.16)],
               shadow, width=s * 0.55, taper=(1, 0.3), alpha=0.22, softness=s * 0.22)
    legs = [(cx - s * 0.16, y - s * 0.5), (cx - s * 0.28, y),
            (cx - s * 0.05, y), (cx - s * 0.02, y - s * 0.45),
            (cx + s * 0.02, y - s * 0.45), (cx + s * 0.05, y),
            (cx + s * 0.28, y), (cx + s * 0.16, y - s * 0.5)]
    cv.flat_shape(legs, coat, alpha=0.92, granulation=0.18, edge=0.4, softness=s * 0.03)
    coat_pts = [(cx - s * 0.34, y - s * 0.4), (cx - s * 0.4, y - s * 1.35),
                (cx + s * 0.4, y - s * 1.35), (cx + s * 0.34, y - s * 0.4)]
    cv.flat_shape(coat_pts, coat, alpha=0.95, granulation=0.2, edge=0.45, softness=s * 0.035)
    hr2 = s * 0.32
    cv.flat_shape(cv.ellipse_points(cx, y - s * 1.5, hr2, hr2 * 0.92, n=14), shadow,
                  alpha=0.95, granulation=0.15, edge=0.4, softness=s * 0.03)
    if pose == "arms_up":
        cv.strokes([
            [(cx - s * 0.3, y - s * 1.1), (cx - s * 0.75, y - s * 1.9)],
            [(cx + s * 0.3, y - s * 1.1), (cx + s * 0.75, y - s * 1.9)],
        ], coat, width=s * 0.22, taper=(1, 0.4), alpha=0.85, softness=s * 0.1, wobble=0.3)
    elif pose == "walking":
        cv.strokes([[(cx - s * 0.3, y - s * 1.0), (cx + s * 0.15, y - s * 0.55)]],
                   coat, width=s * 0.22, taper=(1, 0.4), alpha=0.85, softness=s * 0.1)


# ------------------------------------------------------------------- output

def render_chapter(w, h, seed, sky_top, sky_mid, sky_glow, hill_colors, scene,
                    accent=None, gap_frac=0.34, horizon=0.60):
    cv = Canvas(w, h, seed=seed, paper="#efe6d2")
    rng = cv.rng
    accent_rgb = hex_rgb(accent) if accent else hex_rgb(sky_glow)
    shadow = hex_rgb("#241f33")
    warm = hex_rgb(sky_glow)

    storm_sky(cv, w, h, sky_top, sky_mid, sky_glow, horizon=horizon, mottling=0.5)
    parting_clouds(cv, w, h, rng, shadow, warm, hex_rgb("#f2e6cf"), gap_frac=gap_frac,
                    band=(0.02, 0.5))
    horizon_y = h * horizon

    # colinas primeiro (plano de fundo do chao) -- a cena (rocha, figura,
    # facho) desenha por cima, senao as colinas cobrem tudo que a cena pos
    distant_hills(cv, w, h, horizon_y, hill_colors, rng)
    # chao com gradiente sutil (nunca preto liso) ate a base do quadro
    cv.wash(int(horizon_y + h * 0.01), int(h), hex_rgb(hill_colors[-1]), hex_rgb("#04040a"),
            alpha=0.45, glazes=2, mottling=0.4, wobble=w * 0.01, softness=h * 0.025)

    scene(cv, w, h, horizon_y, rng, accent_rgb, shadow)

    cv.paper_texture(strength=0.04)
    return cv.to_uint8()


# --- cenas por capítulo (assinatura: cv, w, h, horizon_y, rng, accent, shadow) ---

def scene_ch1_throne(cv, w, h, horizon_y, rng, accent, shadow):
    cx = w / 2
    light_shaft(cv, w, h, cx, h * 0.03, horizon_y * 0.85, w * 0.30, accent, alpha=0.30, rng=rng)
    # trono distante e pequeno, no vao de luz, recortado contra o brilho
    ty = horizon_y * 0.42
    seat = [(cx - w * 0.045, ty + h * 0.05), (cx + w * 0.045, ty + h * 0.05),
            (cx + w * 0.033, ty - h * 0.02), (cx - w * 0.033, ty - h * 0.02)]
    cv.flat_shape(seat, shadow, alpha=0.85, granulation=0.3, edge=0.4, softness=h * 0.01)
    back = [(cx - w * 0.03, ty - h * 0.02), (cx + w * 0.03, ty - h * 0.02),
            (cx + w * 0.022, ty - h * 0.13), (cx - w * 0.022, ty - h * 0.13)]
    cv.flat_shape(back, shadow, alpha=0.85, granulation=0.3, edge=0.4, softness=h * 0.01)
    # pequeno adorno/coroa no topo do encosto -- assinatura de trono, nao caixa
    finial_y = ty - h * 0.13
    cv.flat_shape(cv.ellipse_points(cx, finial_y - h * 0.012, w * 0.008, w * 0.008, n=10),
                  accent, alpha=0.9, granulation=0.1, edge=0.0, softness=h * 0.004, mode="over")
    for side in (-1, 1):
        cv.flat_shape([(cx + side * w * 0.022, finial_y), (cx + side * w * 0.03, finial_y - h * 0.03),
                       (cx + side * w * 0.014, finial_y)], shadow, alpha=0.85, granulation=0.2,
                      edge=0.3, softness=h * 0.006)
    rays_fan(cv, w, h, cx, ty - h * 0.02, accent, 14, h * 0.4, 45, 0.16, rng, base_ang=-90)
    birds(cv, w, h, rng, shadow, n=4, y_range=(0.5, 0.58))
    tiny_figure(cv, cx + w * 0.12, horizon_y * 0.98, h * 0.05, shadow, pose="kneeling")


def scene_ch2_sunrise(cv, w, h, horizon_y, rng, accent, shadow):
    cx, cy = w / 2, horizon_y * 0.62
    r = h * 0.11
    cv.spray(cx, cy, r * 5.2, r * 5.2, accent, count=16000, dot=r * 0.05, alpha=0.4,
              falloff=1.3, softness=r * 0.5, mode="over")
    cv.spray(cx, cy, r * 2.4, r * 2.4, hex_rgb("#fff3d6"), count=9000, dot=r * 0.04,
              alpha=0.55, falloff=1.4, softness=r * 0.2, mode="over")
    pts = cv.ellipse_points(cx, cy, r, r, n=24, jitter=0.02)
    cv.flat_shape(pts, hex_rgb("#fff6e0"), alpha=0.95, granulation=0.1, edge=0.0, softness=r * 0.05)
    rays_fan(cv, w, h, cx, cy, accent, 18, h * 0.5, 170, 0.14, rng, base_ang=0)
    birds(cv, w, h, rng, shadow, n=5, y_range=(0.1, 0.32))
    tiny_figure(cv, cx - w * 0.16, horizon_y * 0.99, h * 0.05, shadow, pose="standing")


def scene_ch3_submission(cv, w, h, horizon_y, rng, accent, shadow):
    cx = w / 2
    light_shaft(cv, w, h, cx, h * 0.0, h * 0.94, w * 0.46, accent, alpha=0.46,
                flare_r=w * 0.28, rng=rng)
    rays_fan(cv, w, h, cx, h * 0.05, accent, 14, h * 0.65, 32, 0.2, rng, base_ang=90)
    # rocha em primeiro plano, moderada, ocupando a base do quadro -- perto o
    # bastante pra ler como silhueta nitida, longe do exagero que vira blob
    rock_base_y, rock_h = h * 0.94, h * 0.22
    rock_outcrop(cv, cx, rock_base_y, w * 0.36, rock_h, hex_rgb("#0d090f"), rng)
    peak_y = rock_base_y - rock_h * 0.86
    tiny_figure(cv, cx + w * 0.02, peak_y, rock_h * 0.42, shadow, pose="prostrate")


def scene_ch4_wings(cv, w, h, horizon_y, rng, accent, shadow):
    cx, cy = w / 2, horizon_y * 0.4
    cv.spray(cx, cy, w * 0.26, h * 0.22, accent, count=14000, dot=w * 0.004, alpha=0.4,
              falloff=1.3, softness=h * 0.06, mode="over")
    span = w * 0.24
    for side in (-1, 1):
        pts = []
        n = 8
        for i in range(n + 1):
            t = i / n
            fx = cx + side * span * (0.05 + 0.95 * t)
            fy = cy - span * 0.55 * math.sin(t * math.pi * 0.95) + span * 0.05
            pts.append((fx, fy))
        for i in range(n, -1, -1):
            t = i / n
            fx = cx + side * span * (0.03 + 0.82 * t)
            fy = cy - span * 0.32 * math.sin(t * math.pi * 0.9) + span * 0.16
            pts.append((fx, fy))
        wing = cv.deform_polygon(np.array(pts), depth=3, variance=0.03)
        cv.flat_shape(wing, shadow, alpha=0.9, granulation=0.3, edge=0.4, softness=h * 0.008)
    hr = h * 0.028
    cv.flat_shape(cv.ellipse_points(cx, cy + span * 0.1, hr, hr, n=16), shadow,
                  alpha=0.9, granulation=0.2, edge=0.3, softness=hr * 0.15)
    birds(cv, w, h, rng, shadow, n=4, y_range=(0.55, 0.62))
    tiny_figure(cv, cx - w * 0.14, horizon_y * 0.99, h * 0.05, shadow, pose="arms_up")


def scene_ch5_fracture(cv, w, h, horizon_y, rng, accent, shadow):
    cx = w / 2
    x_top, y_top = cx - w * 0.16, h * 0.02
    x_bot, y_bot = cx + w * 0.13, horizon_y * 0.99
    n = 9
    xs = np.linspace(x_top, x_bot, n)
    ys = np.linspace(y_top, y_bot, n)
    jitter = np.array([rng.uniform(-w * 0.012, w * 0.012) for _ in range(n)])
    jitter[0] = jitter[-1] = 0
    pts = np.stack([xs + jitter, ys], axis=1)
    cv.stroke(pts, hex_rgb("#f4f7ff"), width=w * 0.03, taper=(0.15, 1.0, 0.15), alpha=0.4,
               softness=w * 0.02, wobble=2, texture=0.1, mode="over")
    cv.stroke(pts, hex_rgb("#ffffff"), width=w * 0.009, taper=(0.1, 1.0, 0.1), alpha=0.85,
               softness=w * 0.006, wobble=1, texture=0.15, mode="over")
    cv.spray(x_bot, y_bot, w * 0.09, h * 0.05, hex_rgb("#eaf1ff"), count=9000, dot=w * 0.004,
              alpha=0.5, falloff=1.3, softness=h * 0.03, mode="over")
    # fenda no chao no ponto de impacto
    gx, gy = x_bot, y_bot
    cpts = [(gx, gy)]
    x, y = gx, gy
    for i in range(5):
        x += rng.uniform(-w * 0.04, w * 0.025) - w * 0.015
        y += rng.uniform(h * 0.012, h * 0.03)
        cpts.append((x, y))
    cv.stroke(cpts, shadow, width=w * 0.006, taper=(1, 0.7, 0.5, 0.3), alpha=0.85,
               softness=w * 0.003, wobble=1.5)
    tiny_figure(cv, cx - w * 0.22, horizon_y * 0.99, h * 0.05, shadow, pose="walking")


def scene_ch6_house(cv, w, h, horizon_y, rng, accent, shadow):
    cx = w / 2
    rays_fan(cv, w, h, cx, h * 0.05, accent, 12, h * 0.6, 60, 0.12, rng, base_ang=90)
    base_y = horizon_y * 1.0
    hw, hh = w * 0.085, h * 0.11
    body = [(cx - hw, base_y), (cx + hw, base_y), (cx + hw, base_y - hh), (cx - hw, base_y - hh)]
    cv.flat_shape(body, shadow, alpha=0.9, granulation=0.3, edge=0.4, softness=h * 0.008)
    roof = [(cx - hw * 1.18, base_y - hh), (cx + hw * 1.18, base_y - hh), (cx, base_y - hh - h * 0.075)]
    cv.flat_shape(roof, shadow, alpha=0.9, granulation=0.3, edge=0.4, softness=h * 0.008)
    dw, dh = hw * 0.3, hh * 0.6
    cv.flat_shape([(cx - dw / 2, base_y - dh), (cx + dw / 2, base_y - dh),
                   (cx + dw / 2, base_y), (cx - dw / 2, base_y)],
                  accent, alpha=0.85, granulation=0.15, edge=0.0, softness=h * 0.006, mode="over")
    cv.spray(cx, base_y - dh * 0.5, dw * 1.6, dh * 1.1, accent, count=4000, dot=w * 0.003,
              alpha=0.4, falloff=1.4, softness=h * 0.015, mode="over")
    for side in (-1, 1):
        wx = cx + side * hw * 0.55
        wy = base_y - hh * 0.6
        ww = hw * 0.24
        cv.flat_shape([(wx - ww / 2, wy - ww / 2), (wx + ww / 2, wy - ww / 2),
                       (wx + ww / 2, wy + ww / 2), (wx - ww / 2, wy + ww / 2)],
                      accent, alpha=0.85, granulation=0.15, edge=0.0, mode="over")
    birds(cv, w, h, rng, shadow, n=3, y_range=(0.08, 0.28))
    tiny_figure(cv, cx - w * 0.2, horizon_y * 1.0, h * 0.05, shadow, pose="walking")


def scene_ch7_standing(cv, w, h, horizon_y, rng, accent, shadow):
    cx = w / 2
    light_shaft(cv, w, h, cx, h * 0.02, horizon_y * 0.7, w * 0.34, accent, alpha=0.26, rng=rng)
    rays_fan(cv, w, h, cx, h * 0.04, accent, 16, h * 0.6, 80, 0.13, rng, base_ang=90)
    base_y, rock_h = horizon_y * 1.0, h * 0.18
    rock_outcrop(cv, cx, base_y, w * 0.24, rock_h, hex_rgb("#141018"), rng)
    peak_y = base_y - rock_h * 0.84
    tiny_figure(cv, cx + rock_h * 0.06, peak_y, rock_h * 0.42, shadow, pose="standing")


SCENES = {
    "throne": scene_ch1_throne,
    "sunrise_eye": scene_ch2_sunrise,
    "submission": scene_ch3_submission,
    "wings": scene_ch4_wings,
    "fracture": scene_ch5_fracture,
    "house": scene_ch6_house,
    "standing": scene_ch7_standing,
}


def render_cover(w, h, title, subtitle, author, seed=99):
    from PIL import Image, ImageDraw, ImageFont

    cv = Canvas(w, h, seed=seed, paper="#e9dfc6")
    rng = cv.rng
    sky_top, sky_mid, sky_glow = "#0a0a16", "#241f3d", "#e8b768"
    accent = hex_rgb("#f3cf8e")
    shadow = hex_rgb("#100c18")
    horizon = 0.56
    horizon_y = h * horizon

    storm_sky(cv, w, h, sky_top, sky_mid, sky_glow, horizon=horizon, mottling=0.55)
    parting_clouds(cv, w, h, rng, shadow, hex_rgb(sky_glow), hex_rgb("#f2e6cf"),
                    gap_frac=0.30, band=(0.02, 0.48))
    cx = w / 2
    light_shaft(cv, w, h, cx, h * 0.0, horizon_y * 0.85, w * 0.30, accent, alpha=0.32,
                flare_r=w * 0.24, rng=rng)
    # trono/coroa discreta no vao de luz -- assinatura da serie
    ty = horizon_y * 0.42
    seat = [(cx - w * 0.05, ty + h * 0.045), (cx + w * 0.05, ty + h * 0.045),
            (cx + w * 0.037, ty - h * 0.02), (cx - w * 0.037, ty - h * 0.02)]
    cv.flat_shape(seat, shadow, alpha=0.88, granulation=0.3, edge=0.4, softness=h * 0.01)
    back = [(cx - w * 0.034, ty - h * 0.02), (cx + w * 0.034, ty - h * 0.02),
            (cx + w * 0.024, ty - h * 0.12), (cx - w * 0.024, ty - h * 0.12)]
    cv.flat_shape(back, shadow, alpha=0.88, granulation=0.3, edge=0.4, softness=h * 0.01)
    rays_fan(cv, w, h, cx, ty - h * 0.02, accent, 16, h * 0.35, 50, 0.15, rng, base_ang=-90)
    birds(cv, w, h, rng, shadow, n=4, y_range=(0.5, 0.56))
    tiny_figure(cv, cx + w * 0.14, horizon_y * 0.98, h * 0.02, shadow, pose="walking")

    distant_hills(cv, w, h, horizon_y, ["#181322", "#100d18", "#0a0910"], rng)
    cv.wash(int(horizon_y), int(h), hex_rgb("#0a0910"), hex_rgb("#050408"), alpha=0.6, glazes=2,
            mottling=0.4, wobble=w * 0.01, softness=h * 0.02)
    cv.paper_texture(strength=0.035)
    arr = cv.to_uint8()

    img = Image.fromarray(arr).convert("RGB")
    # veu escuro na metade inferior pra sustentar o texto
    veil = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(veil)
    for y in range(h):
        t = max(0, (y - h * 0.52) / (h * 0.48))
        vd.line([(0, y), (w, y)], fill=int(205 * min(1, t ** 0.85)))
    dark = Image.new("RGB", (w, h), (4, 4, 8))
    img = Image.composite(dark, img, veil)

    draw = ImageDraw.Draw(img)
    cream = (238, 227, 202)
    gold = (223, 186, 122)
    FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"
    F_TITLE = os.path.join(FONT_DIR, "BigShoulders-Bold.ttf")
    F_SUBTITLE = os.path.join(FONT_DIR, "IBMPlexSerif-Italic.ttf")
    F_LABEL = os.path.join(FONT_DIR, "WorkSans-Bold.ttf")
    F_AUTHOR = os.path.join(FONT_DIR, "IBMPlexSerif-Regular.ttf")

    kicker = "SÉRIE DECLARAÇÕES PROFÉTICAS"
    f_kicker = ImageFont.truetype(F_LABEL, int(w * 0.024))
    letter_gap = w * 0.014
    char_widths = [draw.textbbox((0, 0), ch, font=f_kicker)[2] for ch in kicker]
    total_w = sum(char_widths) + letter_gap * (len(kicker) - 1)
    ky = h * 0.575
    xk = (w - total_w) / 2
    for ch, cw in zip(kicker, char_widths):
        draw.text((xk, ky), ch, font=f_kicker, fill=gold)
        xk += cw + letter_gap
    draw.line([(w * 0.5 - w * 0.09, ky + h * 0.028), (w * 0.5 + w * 0.09, ky + h * 0.028)],
              fill=gold, width=2)

    def _wrap_lines(words, font, max_width):
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

    words = title.upper().split(" ")
    f_title = ImageFont.truetype(F_TITLE, int(w * 0.135))
    lines = _wrap_lines(words, f_title, w * 0.86)
    while True:
        total_h = 0
        for ln in lines:
            b = draw.textbbox((0, 0), ln, font=f_title)
            total_h += (b[3] - b[1]) * 1.06
        if total_h <= h * 0.29 or f_title.size <= 40:
            break
        f_title = ImageFont.truetype(F_TITLE, f_title.size - 4)
        lines = _wrap_lines(words, f_title, w * 0.86)

    ty2 = h * 0.625
    for ln in lines:
        b = draw.textbbox((0, 0), ln, font=f_title)
        lw = b[2] - b[0]
        lh = b[3] - b[1]
        draw.text(((w - lw) / 2, ty2), ln, font=f_title, fill=cream)
        ty2 += lh * 1.1

    f_sub = ImageFont.truetype(F_SUBTITLE, int(w * 0.032))
    sub_lines = _wrap_lines(subtitle.split(" "), f_sub, w * 0.7)
    ty2 += h * 0.02
    for ln in sub_lines:
        b = draw.textbbox((0, 0), ln, font=f_sub)
        lw = b[2] - b[0]
        draw.text(((w - lw) / 2, ty2), ln, font=f_sub, fill=(214, 205, 184))
        ty2 += (b[3] - b[1]) * 1.35

    ly = h * 0.935
    draw.line([(w * 0.5 - w * 0.1, ly), (w * 0.5 + w * 0.1, ly)], fill=gold, width=2)
    f_auth = ImageFont.truetype(F_AUTHOR, int(w * 0.028))
    ab = draw.textbbox((0, 0), author, font=f_auth)
    draw.text(((w - (ab[2] - ab[0])) / 2, ly + h * 0.015), author, font=f_auth, fill=cream)

    return np.array(img)
