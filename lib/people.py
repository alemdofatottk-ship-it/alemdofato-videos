"""Personagens genéricos flat noir (terno, gravata, olhos que piscam, poses e expressões)."""
import math
from PIL import Image, ImageDraw
from core import ss_layer, down, RED, WHITE, INK, font

SUITS = [(38, 44, 58), (58, 52, 48), (30, 36, 52), (70, 74, 82)]
HAIRS = [(28, 22, 20), (70, 50, 34), (110, 110, 112), (20, 20, 24)]
SKINS = [(214, 170, 140), (176, 128, 96), (232, 196, 168), (128, 88, 64)]

# pontos dos braços: (cotovelo, mão) relativos ao ombro, lado esquerdo da tela; o direito é espelhado
POSES = {
    "stand": [((-14, 60), (-12, 118)), ((14, 60), (12, 118))],
    "panic": [((-58, -24), (-36, -66)), ((58, -24), (36, -66))],
    "point": [((-70, 10), (-150, -4)), ((14, 60), (12, 118))],
    "phone": [((-14, 60), (-12, 118)), ((44, 40), (12, -40))],
    "shrug": [((-62, 58), (-104, 18)), ((62, 58), (104, 18))],
    "think": [((-14, 60), (-12, 118)), ((40, 56), (4, -14))],
    "cheer": [((-48, -40), (-70, -110)), ((48, -40), (70, -110))],
    "suitcase": [((-14, 60), (-18, 116)), ((22, 58), (30, 112))],
    "watch": [((-40, 50), (8, 40)), ((14, 60), (12, 118))],
}


def person(pose="stand", expr="neutral", t=0.0, scale=1.75, look=0, suit=0, hair=0, skin=0, balloon=None,
           bt=0.0, tie=RED, seed=0):
    s = 2
    U = scale * s
    Wb, Hb = int(460 * scale), int(470 * scale)
    lay = ss_layer(Wb, Hb, s)
    d = ImageDraw.Draw(lay)
    ox = Wb * s / 2
    feet = Hb * s - 6 * s
    shake = 0
    if pose == "panic":
        shake = math.sin(t * 46 + seed) * 3.2 * U
    breathe = math.sin(t * 2.2 + seed) * 1.6 * U

    def P(x, y):
        return (ox + x * U + shake, feet - (340 - y) * U + (breathe if y < 220 else 0))

    sc, hc, kc = SUITS[suit % 4], HAIRS[hair % 4], SKINS[skin % 4]
    dark = tuple(max(0, c - 16) for c in sc)
    # pernas
    for sx in (-1, 1):
        d.polygon([P(sx * 8, 210), P(sx * 46, 210), P(sx * 40, 332), P(sx * 14, 332)], fill=dark)
        x0, x1 = (sx * 27 - 24, sx * 27 + 14) if sx < 0 else (sx * 27 - 14, sx * 27 + 24)
        d.ellipse([P(x0, 324), P(x1, 344)], fill=INK)
    # tronco
    d.polygon([P(-56, 92), P(56, 92), P(48, 216), P(-48, 216)], fill=sc)
    d.polygon([P(-18, 92), P(18, 92), P(0, 150)], fill=(236, 236, 232))
    d.polygon([P(-6, 100), P(6, 100), P(9, 160), P(0, 172), P(-9, 160)], fill=tie)
    d.polygon([P(-18, 92), P(-4, 92), P(-24, 150)], fill=dark)
    d.polygon([P(18, 92), P(4, 92), P(24, 150)], fill=dark)
    # pescoço + cabeça
    d.rectangle([P(-12, 76), P(12, 96)], fill=kc)
    hx, hy = 0 + look * 4, 46
    R = 36
    cx, cy = P(hx, hy)
    r = R * U
    d.ellipse([cx - r, cy - r * 1.08, cx + r, cy + r * 1.08], fill=kc)
    # cabelo
    d.chord([cx - r * 1.04, cy - r * 1.18, cx + r * 1.04, cy + r * 0.5], 180, 360, fill=hc)
    d.rectangle([cx - r * 1.02, cy - r * 0.35, cx - r * 0.82, cy + r * 0.15], fill=hc)
    d.rectangle([cx + r * 0.82, cy - r * 0.35, cx + r * 1.02, cy + r * 0.15], fill=hc)
    # olhos (piscam)
    blink = (t + seed * 0.7) % 3.1 < 0.12
    ex = r * 0.36
    ey = cy + r * 0.05
    lx = look * r * 0.12
    big = expr in ("scared",)
    er = r * (0.12 if big else 0.09)
    for sx in (-1, 1):
        x = cx + sx * ex + lx
        if blink:
            d.line([x - er, ey, x + er, ey], fill=INK, width=int(3 * U))
        else:
            if big:
                d.ellipse([x - er * 1.5, ey - er * 1.5, x + er * 1.5, ey + er * 1.5], fill=WHITE)
            d.ellipse([x - er, ey - er, x + er, ey + er], fill=INK)
        # sobrancelhas
        by = ey - r * 0.3
        if expr in ("worried", "scared"):
            d.line([x - er * 2.2, by + sx * -r * 0.0 - (r * 0.08 if sx < 0 else 0), x + er * 2.2,
                    by - (0 if sx < 0 else r * 0.08)], fill=hc, width=int(4 * U))
        elif expr == "angry":
            d.line([x - er * 2.2, by - (r * 0.08 if sx > 0 else 0), x + er * 2.2, by - (r * 0.08 if sx < 0 else 0)],
                   fill=hc, width=int(4 * U))
        else:
            d.line([x - er * 2.2, by, x + er * 2.2, by], fill=hc, width=int(4 * U))
    # boca
    my = cy + r * 0.52
    mw = r * 0.32
    if expr == "happy":
        d.chord([cx - mw, my - mw * 0.9, cx + mw, my + mw * 0.6], 0, 180, fill=(90, 30, 30))
    elif expr == "scared":
        d.ellipse([cx - mw * 0.45, my - mw * 0.35, cx + mw * 0.45, my + mw * 0.75], fill=(60, 20, 20))
    elif expr == "worried":
        d.arc([cx - mw, my, cx + mw, my + mw * 1.2], 200, 340, fill=INK, width=int(3.5 * U))
    else:
        d.line([cx - mw * 0.7, my + mw * 0.2, cx + mw * 0.7, my + mw * 0.2], fill=INK, width=int(3.5 * U))
    # suor
    if pose == "panic" or expr == "scared":
        k = (t * 1.3 + seed) % 1
        sx_, sy_ = cx + r * 1.05, cy - r * 0.2 + k * r * 0.8
        d.ellipse([sx_ - 6 * U, sy_ - 9 * U, sx_ + 6 * U, sy_ + 9 * U], fill=(150, 200, 235))
    # braços
    arms = POSES.get(pose, POSES["stand"])
    wav = 0
    if pose in ("cheer",):
        wav = math.sin(t * 9) * 8
    for i, (el, ha) in enumerate(arms):
        side = -1 if i == 0 else 1
        sh = P(side * 54, 100)
        e = P(side * 54 + el[0], 100 + el[1] + wav)
        h = P(side * 54 + ha[0], 100 + ha[1] + wav)
        wdt = int(26 * U)
        d.line([sh, e], fill=sc, width=wdt, joint="curve")
        d.line([e, h], fill=sc, width=wdt, joint="curve")
        for pnt in (sh, e):
            d.ellipse([pnt[0] - wdt / 2, pnt[1] - wdt / 2, pnt[0] + wdt / 2, pnt[1] + wdt / 2], fill=sc)
        d.ellipse([h[0] - 13 * U, h[1] - 13 * U, h[0] + 13 * U, h[1] + 13 * U], fill=kc)
        if pose == "phone" and i == 1:
            d.rounded_rectangle([h[0] - 12 * U, h[1] - 30 * U, h[0] + 12 * U, h[1] + 8 * U], 4 * U, fill=INK)
            d.rectangle([h[0] - 8 * U, h[1] - 26 * U, h[0] + 8 * U, h[1] + 2 * U], fill=(120, 170, 220))
        if pose == "suitcase" and i == 1:
            bx, by_ = h[0], h[1] + 10 * U
            d.rounded_rectangle([bx - 50 * U, by_ + 8 * U, bx + 50 * U, by_ + 110 * U], 8 * U, fill=(120, 40, 36))
            d.rectangle([bx - 50 * U, by_ + 50 * U, bx + 50 * U, by_ + 58 * U], fill=(80, 26, 24))
            d.arc([bx - 18 * U, by_ - 4 * U, bx + 18 * U, by_ + 20 * U], 180, 360, fill=INK, width=int(5 * U))
        if pose == "watch" and i == 0:
            d.rectangle([h[0] - 14 * U, h[1] - 8 * U, h[0] + 2 * U, h[1] + 8 * U], fill=(200, 200, 200))
    # balão de reação
    if balloon:
        k = min(1, max(0, (t - bt) / 0.25))
        if k > 0:
            bx, by_ = cx + r * 1.3, cy - r * 1.6
            br = 34 * U * (0.6 + 0.4 * k) * (1 + 0.06 * math.sin(t * 8))
            d.ellipse([bx - br, by_ - br, bx + br, by_ + br], fill=WHITE, outline=INK, width=int(4 * U))
            d.polygon([(bx - br * 0.5, by_ + br * 0.7), (bx - br * 1.1, by_ + br * 1.5), (bx - br * 0.05, by_ + br * 0.9)],
                      fill=WHITE)
            d.text((bx, by_), balloon, font=font("anton", int(44 * U)), fill=RED if balloon == "!" else INK, anchor="mm")
    return down(lay, s)


def place(img, p, x_center=780, feet_y=1470):
    """Cola o personagem com os pés em feet_y (lado direito da tela)."""
    img.alpha_composite(p, (int(x_center - p.width / 2), int(feet_y - p.height)))
