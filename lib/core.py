"""Base do estilo Dossiê curto (1080x1920): paleta, fontes, fundos, tarjas, marca d'água, transição."""
import math, os
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")

# paleta noir
INK = (14, 17, 24)
NAVY = (27, 34, 48)
SLATE = (44, 53, 70)
STEEL = (78, 90, 110)
FOG = (138, 147, 163)
PAPER = (232, 228, 218)
MANILA = (214, 186, 132)
RED = (206, 38, 38)
DRED = (140, 22, 22)
AMBER = (245, 197, 66)
WHITE = (245, 245, 240)
SKIN = (214, 170, 140)


@lru_cache(None)
def font(name, size, weight=None):
    path = {"anton": "Anton-Regular.ttf", "oswald": "Oswald.ttf", "elite": "SpecialElite-Regular.ttf",
            "courier": "CourierPrime-Regular.ttf"}[name]
    f = ImageFont.truetype(os.path.join(A, "fonts", path), size)
    if name == "oswald":
        try:
            f.set_variation_by_axes([weight or 600])
        except Exception:
            pass
    return f


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = clamp(x)
    return x ** 3


def ease_io(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def back_out(x, s=1.70158):
    x = clamp(x) - 1
    return x * x * ((s + 1) * x + s) + 1


def lerp(a, b, t):
    return a + (b - a) * t


# ---------- fundos ----------
@lru_cache(None)
def gray_bg():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W * 0.75)) ** 2 + ((y - H * 0.46) / (H * 0.62)) ** 2)
    base = 104 - 62 * np.clip(d, 0, 1.25) ** 1.5 - 10 * (y / H)
    rng = np.random.default_rng(3)
    base = base + rng.normal(0, 2.2, base.shape)
    arr = np.stack([base * 0.97, base * 0.99, base * 1.04], -1)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


@lru_cache(None)
def night_bg(top=(16, 20, 30), bottom=(40, 48, 64)):
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    arr = np.zeros((H, W, 3), np.float32)
    for c in range(3):
        arr[..., c] = top[c] + (bottom[c] - top[c]) * y
    xx = np.linspace(-1, 1, W, dtype=np.float32)[None, :]
    v = 1 - 0.35 * xx ** 2
    arr *= v[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


@lru_cache(None)
def vignette_layer(strength=0.55):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.6)) ** 2)
    a = np.clip((d - 0.65) / 0.7, 0, 1) ** 1.4 * 255 * strength
    img = np.zeros((H, W, 4), np.uint8)
    img[..., 3] = a.astype(np.uint8)
    return Image.fromarray(img, "RGBA")


# ---------- texto ----------
def text_size(txt, f):
    b = f.getbbox(txt)
    return b[2] - b[0], b[3] - b[1], b


def draw_text_center(d, cx, cy, txt, f, fill, anchor="mm", stroke=0, stroke_fill=None):
    d.text((cx, cy), txt, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)


def wrap(txt, f, maxw):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_size(t, f)[0] <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------- logo ----------
@lru_cache(None)
def logo(size):
    im = Image.open(os.path.join(A, "logo.png")).convert("RGBA").resize((size * 2, size * 2), Image.LANCZOS)
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse((4, 4, size * 2 - 4, size * 2 - 4), fill=255)
    im.putalpha(m)
    return im.resize((size, size), Image.LANCZOS)


# ---------- overlays comuns ----------
def rounded(d, box, r, fill, outline=None, width=1):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


@lru_cache(None)
def watermark():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = font("oswald", 30, 600)
    tw = text_size("ALÉM DO FATO", f)[0]
    lw = 52
    pw = lw + 14 + tw + 40
    x0, y0 = W // 2 - pw // 2, 1560 - 34
    rounded(d, (x0, y0, x0 + pw, y0 + 68), 34, (10, 10, 14, 150))
    lay.alpha_composite(logo(lw), (x0 + 10, y0 + 8))
    d.text((x0 + 10 + lw + 14, 1560), "ALÉM DO FATO", font=f, fill=(240, 240, 240, 215), anchor="lm")
    return lay


def tag(img, text, t):
    """Etiqueta do caso no canto de cima à esquerda (entra deslizando)."""
    d = ImageDraw.Draw(img)
    f = font("oswald", 34, 700)
    tw = text_size(text, f)[0]
    k = ease_out(t / 0.35)
    x = int(lerp(-tw - 80, 48, k))
    rounded(d, (x, 120, x + tw + 44, 176), 8, RED)
    d.text((x + 22, 148), text, font=f, fill=WHITE, anchor="lm")


def caption(img, text, t, base=1344):
    """Legenda curta numa barra preta, canto de baixo à esquerda."""
    if not text:
        return
    d = ImageDraw.Draw(img)
    f = font("oswald", 44, 600)
    lines = wrap(text.upper(), f, 760)
    lh = 60
    hgt = lh * len(lines) + 28
    w = max(text_size(l, f)[0] for l in lines) + 56
    k = ease_out((t - 0.15) / 0.4)
    if k <= 0:
        return
    x = int(lerp(-w - 20, 40, k))
    y0 = base - hgt
    d.rectangle((x, y0, x + w, base), fill=(8, 8, 10))
    d.rectangle((x, y0, x + 10, base), fill=RED)
    for i, l in enumerate(lines):
        d.text((x + 34, y0 + 14 + lh * i + lh // 2), l, font=f, fill=WHITE, anchor="lm")


def red_cut(img, t, dur=0.18):
    """Faixa vermelha diagonal cortando a tela (transição)."""
    if t < 0 or t > dur:
        return
    k = t / dur
    d = ImageDraw.Draw(img)
    band = 520
    cx = lerp(-band - 600, W + band + 600, k)
    sk = 700
    pts = [(cx - band / 2 + sk, 0), (cx + band / 2 + sk, 0), (cx + band / 2 - sk, H), (cx - band / 2 - sk, H)]
    d.polygon(pts, fill=RED)
    d.line([(cx + band / 2 + sk, 0), (cx + band / 2 - sk, H)], fill=(255, 90, 90), width=10)


def finish(img):
    """Marca d'água em todo quadro."""
    img = img.convert("RGBA")
    img.alpha_composite(watermark())
    return img.convert("RGB")


# ---------- utilidades de desenho ----------
def ss_layer(w, h, s=2):
    """Camada supersampled para desenhos com borda suave."""
    return Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))


def down(layer, s=2):
    return layer.resize((layer.width // s, layer.height // s), Image.LANCZOS)


def sticker(im, border=10, shadow=True):
    """Contorno branco + sombra (estilo adesivo)."""
    a = im.split()[3]
    big = a.filter(ImageFilter.MaxFilter(border * 2 + 1))
    pad = border + 20
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
        m = Image.new("L", out.size, 0)
        m.paste(big, (pad + 8, pad + 12))
        sh.putalpha(m.point(lambda v: v * 0.55).filter(ImageFilter.GaussianBlur(8)))
        out.alpha_composite(sh)
    wl = Image.new("RGBA", im.size, (255, 255, 255, 255))
    wl.putalpha(big)
    out.alpha_composite(wl, (pad, pad))
    out.alpha_composite(im, (pad, pad))
    return out


def paste_center(base, im, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    w, h = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    im2 = im.resize((w, h), Image.BICUBIC)
    if rot:
        im2 = im2.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 1:
        a = im2.split()[3].point(lambda v: int(v * alpha))
        im2.putalpha(a)
    x, y = int(cx - im2.width / 2), int(cy - im2.height / 2)
    # recorte seguro (itens fora da tela)
    if x >= base.width or y >= base.height or x + im2.width <= 0 or y + im2.height <= 0:
        return
    sx, sy = max(0, -x), max(0, -y)
    crop = im2.crop((sx, sy, min(im2.width, base.width - x), min(im2.height, base.height - y)))
    base.alpha_composite(crop, (x + sx, y + sy))
