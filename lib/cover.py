"""Capa curta (oval vazio central + vinheta de objetos) e abertura animada a partir da capa."""
import math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from core import *
import scenes

ICON = 260


def _icon(name):
    s = 2
    lay = ss_layer(ICON, ICON)
    d = ImageDraw.Draw(lay)
    U = s
    c = ICON * s / 2
    if name == "aviao":
        p = scenes.plane(0.33)
        lay2 = Image.new("RGBA", (ICON, ICON), (0, 0, 0, 0))
        lay2.alpha_composite(p, ((ICON - p.width) // 2, (ICON - p.height) // 2))
        return lay2
    if name == "torre":
        t = scenes._tower().resize((70, 242), Image.LANCZOS)
        lay2 = Image.new("RGBA", (ICON, ICON), (0, 0, 0, 0))
        lay2.alpha_composite(t, ((ICON - 70) // 2, 8))
        return lay2
    if name == "relogio":
        d.ellipse([20 * U, 20 * U, 240 * U, 240 * U], fill=PAPER, outline=INK, width=14 * U)
        d.line([c, c, c, 60 * U], fill=INK, width=12 * U)
        d.line([c, c, 190 * U, c], fill=RED, width=12 * U)
    elif name == "roteador":
        d.rounded_rectangle([20 * U, 120 * U, 240 * U, 210 * U], 18 * U, fill=(40, 44, 54))
        for i in range(5):
            d.ellipse([(50 + i * 36) * U, 155 * U, (70 + i * 36) * U, 175 * U], fill=RED)
        for x in (60, 130, 200):
            d.line([x * U, 120 * U, (x - 20) * U, 30 * U], fill=(40, 44, 54), width=12 * U)
    elif name == "mala":
        d.rounded_rectangle([40 * U, 80 * U, 220 * U, 230 * U], 22 * U, fill=(140, 44, 40))
        d.rectangle([40 * U, 145 * U, 220 * U, 160 * U], fill=(90, 26, 24))
        d.arc([90 * U, 30 * U, 170 * U, 110 * U], 180, 360, fill=INK, width=14 * U)
    elif name == "cancelado":
        d.rounded_rectangle([10 * U, 70 * U, 250 * U, 190 * U], 14 * U, fill=(14, 14, 18))
        d.text((c, 130 * U), "CANCELADO", font=font("anton", 44 * U), fill=(255, 70, 70), anchor="mm")
    elif name == "radar":
        d.ellipse([20 * U, 20 * U, 240 * U, 240 * U], fill=(20, 50, 40), outline=(90, 220, 130), width=8 * U)
        for r in (70, 40):
            d.ellipse([c - r * U, c - r * U, c + r * U, c + r * U], outline=(90, 220, 130), width=4 * U)
        d.pieslice([20 * U, 20 * U, 240 * U, 240 * U], -80, -30, fill=(90, 220, 130))
    elif name == "alerta":
        d.polygon([(c, 20 * U), (245 * U, 230 * U), (15 * U, 230 * U)], fill=AMBER)
        d.text((c, 160 * U), "!", font=font("anton", 150 * U), fill=INK, anchor="mm")
    elif name == "cabo":
        for i in range(5):
            d.line([30 * U, (80 + i * 22) * U, 230 * U, (120 + i * 22) * U], fill=(200, 110, 50) if i % 2 else (230, 150, 80),
                   width=14 * U)
    return down(lay)


@lru_cache(None)
def icon(name):
    return sticker(_icon(name), border=9)


def oval_mask(scale=1.0, feather=26):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    ax, ay = W * 0.40 * scale, H * 0.36 * scale * 0.9
    d = np.sqrt(((x - W / 2) / ax) ** 2 + ((y - H / 2) / ay) ** 2)
    a = np.clip((1.0 - d) * ax / feather + 0.5, 0, 1)
    return a


@lru_cache(None)
def oval_layer_cached(q):
    a = oval_mask(q / 100.0)
    img = np.zeros((H, W, 4), np.uint8)
    img[..., 0], img[..., 1], img[..., 2] = 12, 14, 18
    img[..., 3] = (a * 250).astype(np.uint8)
    im = Image.fromarray(img, "RGBA")
    if q == 100:
        d = ImageDraw.Draw(im)
        ax, ay = W * 0.40, H * 0.36 * 0.9
        d.ellipse([W / 2 - ax - 6, H / 2 - ay - 6, W / 2 + ax + 6, H / 2 + ay + 6], outline=(120, 124, 132, 200), width=3)
    return im


@lru_cache(None)
def side_dark():
    x = np.abs(np.linspace(-1, 1, W, dtype=np.float32))[None, :].repeat(H, 0)
    a = (0.35 + 0.4 * x ** 2) * 255
    img = np.zeros((H, W, 4), np.uint8)
    img[..., 3] = a.astype(np.uint8)
    return Image.fromarray(img, "RGBA")


def ring_positions():
    """12 no anel oval (simétricos: 5 de cada lado + topo + base) e 4 nos cantos."""
    pos = []
    ax, ay = W * 0.46, H * 0.36
    for side in (1, -1):
        for ang in (-60, -30, 0, 30, 60):
            a = math.radians(ang)
            pos.append((W / 2 + side * ax * math.cos(a) * 1.02, H / 2 + ay * math.sin(a) * 1.05, 0.74))
    pos.append((W / 2, H / 2 - ay * 1.1, 0.74))
    pos.append((W / 2, H / 2 + ay * 1.1, 0.74))
    for sx in (-1, 1):
        for sy in (-1, 1):
            pos.append((W / 2 + sx * W * 0.47, H / 2 + sy * H * 0.45, 1.05))
    return pos


def cover_frame(info, t=0.0, out=0.0):
    """info: title_lines, tag, icons, bg (RGBA sem personagens), hl (tempo de cada linha: (t0,t1))."""
    img = info["bg"].copy()
    img.alpha_composite(side_dark())
    # escurece laterais / fora do oval
    q = int(100 + 260 * ease_in(out))
    img.alpha_composite(oval_layer_cached(min(q, 400)))
    names = info["icons"]
    pos = ring_positions()
    for i, (x, y, sc) in enumerate(pos):
        im = icon(names[i % len(names)])
        ang = math.degrees(math.atan2(H / 2 - y, W / 2 - x))
        rot = -(ang % 360 - 90) * 0.12 + (6 if x < W / 2 else -6)
        fx = math.sin(t * 2.1 + i) * 8
        fy = math.cos(t * 1.7 + i * 1.3) * 8
        if out > 0:
            k = ease_in(clamp(out / 0.75))
            dx, dy = x - W / 2, y - H / 2
            x, y = x + dx * 1.6 * k, y + dy * 1.6 * k
            rot += 220 * k * (1 if i % 2 else -1)
        paste_center(img, im, x + fx, y + fy, scale=sc, rot=rot)
    fa = 1 - clamp(out / 0.45)
    if fa > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        lines = info["title_lines"]
        size = 150
        while size > 60:
            f = font("anton", size)
            if max(text_size(l, f)[0] for l in lines) <= W * 0.58 and len(lines) * size * 1.12 < 620:
                break
            size -= 4
        f = font("anton", size)
        lh = size * 1.12
        top = H / 2 - lh * (len(lines) - 1) / 2 + 40
        # etiqueta
        ft = font("oswald", 40, 700)
        tw = text_size(info["tag"], ft)[0]
        ty = top - lh / 2 - 60
        d.rounded_rectangle([W / 2 - tw / 2 - 26, ty - 32, W / 2 + tw / 2 + 26, ty + 32], 32, fill=RED + (int(255 * fa),))
        d.text((W / 2, ty), info["tag"], font=ft, fill=(255, 255, 255, int(255 * fa)), anchor="mm")
        for i, l in enumerate(lines):
            y = top + i * lh
            col = PAPER
            jump = 0
            if info.get("hl"):
                a0, a1 = info["hl"][i]
                if a0 <= t < a1 + 0.1:
                    col = AMBER
                    jump = -18 * math.sin(math.pi * clamp((t - a0) / 0.25))
            d.text((W / 2 + 5, y + 8 + jump), l, font=f, fill=(0, 0, 0, int(170 * fa)), anchor="mm")
            d.text((W / 2, y + jump), l, font=f, fill=col + (int(255 * fa),), anchor="mm")
        img.alpha_composite(lay)
    return img
