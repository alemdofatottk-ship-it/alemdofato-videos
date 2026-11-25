"""Cenas noir em tela cheia (9:16), animadas. Cada cena: f(t, dur, **opts) -> RGBA 1080x1920 (sem personagem)."""
import math, random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
from core import *


def base_night():
    return night_bg().convert("RGBA")


# ---------------- relógio ----------------
def clock(t, dur, hour=15, minute=30, label="15H30", sub="WASHINGTON", elapsed=None, cy=640):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    s = 2
    cx, cyy, R = 540 * s, cy * s, 300 * s
    d.ellipse([cx - R - 26 * s, cyy - R - 26 * s, cx + R + 26 * s, cyy + R + 26 * s], fill=(10, 12, 16))
    d.ellipse([cx - R, cyy - R, cx + R, cyy + R], fill=PAPER)
    for i in range(60):
        a = i / 60 * 2 * math.pi
        r1 = R * (0.86 if i % 5 == 0 else 0.92)
        wdt = 9 * s if i % 5 == 0 else 3 * s
        d.line([cx + math.sin(a) * r1, cyy - math.cos(a) * r1, cx + math.sin(a) * R * 0.97, cyy - math.cos(a) * R * 0.97],
               fill=INK, width=wdt)
    if elapsed:  # (h0,m0,h1,m1): arco vermelho do intervalo
        h0, m0, h1, m1 = elapsed
        k = ease_io((t - 0.2) / max(0.5, dur - 0.9))
        tot = (h1 * 60 + m1) - (h0 * 60 + m0)
        cur = h0 * 60 + m0 + tot * k
        a0 = ((h0 % 12) * 60 + m0) / 720 * 360 - 90
        a1 = ((cur / 60 % 12) * 60) / 720 * 360 - 90 if False else ((cur % 720) / 720) * 360 - 90
        d.pieslice([cx - R * 0.8, cyy - R * 0.8, cx + R * 0.8, cyy + R * 0.8], a0, a0 + tot * k / 720 * 360,
                   fill=(206, 38, 38, 150))
        hh, mm = divmod(cur, 60)
        el = tot * k
        label = f"{int(el // 60)}H{int(el % 60):02d}"
    else:
        k = ease_out((t - 0.1) / 1.0)
        cur = (hour * 60 + minute) * k + (hour * 60 + minute - 180) * (1 - k)
        hh, mm = divmod(cur, 60)
    ah = ((hh % 12) + mm / 60) / 12 * 2 * math.pi
    am = mm / 60 * 2 * math.pi
    d.line([cx, cyy, cx + math.sin(ah) * R * 0.5, cyy - math.cos(ah) * R * 0.5], fill=INK, width=22 * s)
    d.line([cx, cyy, cx + math.sin(am) * R * 0.78, cyy - math.cos(am) * R * 0.78], fill=INK, width=12 * s)
    sa = (t * 6) % (2 * math.pi)
    d.line([cx, cyy, cx + math.sin(sa) * R * 0.84, cyy - math.cos(sa) * R * 0.84], fill=RED, width=4 * s)
    d.ellipse([cx - 18 * s, cyy - 18 * s, cx + 18 * s, cyy + 18 * s], fill=RED)
    img.alpha_composite(down(lay))
    d = ImageDraw.Draw(img)
    f = font("anton", 120)
    k2 = ease_out((t - 0.3) / 0.4)
    if k2 > 0:
        y = cy + 300 + 120
        tw = text_size(label, f)[0]
        d.rectangle([540 - tw / 2 - 30, y - 80, 540 + tw / 2 + 30, y + 80], fill=RED)
        d.text((540, y), label, font=f, fill=WHITE, anchor="mm")
        if sub:
            d.text((540, y + 130), sub, font=font("oswald", 52, 600), fill=FOG, anchor="mm")
    return img


# ---------------- avião ----------------
def plane(scale=1.0, color=(226, 228, 232), tail=RED, flip=False):
    s = 2
    w, h = int(760 * scale), int(260 * scale)
    lay = ss_layer(w, h)
    d = ImageDraw.Draw(lay)
    U = scale * s
    # fuselagem
    d.rounded_rectangle([40 * U, 110 * U, 700 * U, 180 * U], 34 * U, fill=color)
    d.pieslice([640 * U, 110 * U, 750 * U, 180 * U], 270, 90, fill=color)
    d.polygon([(40 * U, 112 * U), (110 * U, 112 * U), (90 * U, 20 * U), (40 * U, 20 * U)], fill=tail)
    d.polygon([(330 * U, 160 * U), (470 * U, 160 * U), (360 * U, 250 * U), (300 * U, 250 * U)], fill=(170, 174, 182))
    d.rounded_rectangle([360 * U, 182 * U, 450 * U, 220 * U], 18 * U, fill=(120, 124, 132))
    for i in range(16):
        x = 140 * U + i * 30 * U
        d.ellipse([x, 128 * U, x + 14 * U, 142 * U], fill=(40, 50, 66))
    d.polygon([(660 * U, 124 * U), (712 * U, 124 * U), (720 * U, 140 * U), (668 * U, 140 * U)], fill=(40, 50, 66))
    # trem de pouso
    for x in (200, 560):
        d.line([x * U, 180 * U, x * U, 230 * U], fill=INK, width=int(8 * U))
        d.ellipse([(x - 16) * U, 222 * U, (x + 16) * U, 254 * U], fill=INK)
    im = down(lay)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im


@lru_cache(None)
def _tower():
    s = 2
    lay = ss_layer(260, 900)
    d = ImageDraw.Draw(lay)
    d.polygon([(100 * s, 900 * s), (160 * s, 900 * s), (150 * s, 260 * s), (110 * s, 260 * s)], fill=(30, 36, 48))
    d.polygon([(30 * s, 260 * s), (230 * s, 260 * s), (200 * s, 140 * s), (60 * s, 140 * s)], fill=(36, 44, 58))
    d.polygon([(48 * s, 240 * s), (212 * s, 240 * s), (190 * s, 160 * s), (70 * s, 160 * s)], fill=(90, 120, 150))
    d.rectangle([60 * s, 110 * s, 200 * s, 140 * s], fill=(30, 36, 48))
    d.line([130 * s, 110 * s, 130 * s, 20 * s], fill=(30, 36, 48), width=6 * s)
    return down(lay)


def grounded(t, dur, sky=((24, 30, 48), (92, 62, 70))):
    img = Image.new("RGBA", (W, H))
    y = 0
    d = ImageDraw.Draw(img)
    for i in range(1150):
        k = i / 1150
        c = tuple(int(lerp(sky[0][j], sky[1][j], k)) for j in range(3))
        d.line([(0, i), (W, i)], fill=c)
    d.rectangle([0, 1150, W, H], fill=(46, 50, 58))
    for i in range(8):
        d.line([(i * 160 - 60, 1150), (i * 230 - 480, H)], fill=(60, 64, 72), width=4)
    d.rectangle([0, 1150, W, 1162], fill=(70, 74, 82))
    img.alpha_composite(_tower(), (40, 1150 - 900))
    # aviões parados
    for sc, x, yb, fl in ((0.55, 560, 1210, True), (0.8, -120, 1330, False), (1.0, 300, 1520, True)):
        p = plane(sc, flip=fl)
        img.alpha_composite(p, (x, yb - p.height))
    # luzes de pare piscando
    on = int(t * 2.5) % 2 == 0
    for x in (120, 960):
        d.ellipse([x - 26, 1110 - 26, x + 26, 1110 + 26], fill=RED if on else (70, 20, 20))
        d.rectangle([x - 4, 1136, x + 4, 1160], fill=(20, 20, 20))
    # carimbo
    k = back_out((t - 0.45) / 0.35)
    if k > 0:
        st = stamp("TODOS NO CHÃO", 64)
        paste_center(img, st, 540, 470, scale=0.6 + 0.4 * k, rot=-6, alpha=min(1, k))
    return img


def stamp(text, size=70, color=RED, sub=None):
    f = font("anton", size)
    tw, th, _ = text_size(text, f)
    w, h = tw + 80, th + 70 + (size * 0.7 if sub else 0)
    s = 2
    lay = ss_layer(int(w), int(h))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([6 * s, 6 * s, (w - 6) * s, (h - 6) * s], 14 * s, outline=color, width=9 * s)
    d.text((w / 2 * s, (35 + th / 2 + 4) * s), text, font=font("anton", size * s), fill=color, anchor="mm")
    if sub:
        d.text((w / 2 * s, (h - 40) * s), sub, font=font("oswald", int(size * 0.45) * s, 600), fill=color, anchor="mm")
    im = down(lay)
    # textura gasta
    a = im.split()[3]
    rng = random.Random(len(text))
    dd = ImageDraw.Draw(a)
    for _ in range(int(w * h / 900)):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        dd.ellipse([x, y, x + rng.uniform(1, 4), y + rng.uniform(1, 4)], fill=0)
    im.putalpha(a)
    return im


# ---------------- rede de controle ----------------
NODES = [(170, 380), (520, 300), (880, 420), (300, 700), (720, 650), (150, 1000), (540, 980), (930, 900)]
EDGES = [(0, 1), (1, 2), (0, 3), (1, 3), (1, 4), (2, 4), (3, 4), (3, 5), (3, 6), (4, 6), (4, 7), (5, 6), (6, 7), (2, 7)]


def _node_icon(d, x, y, state):
    col = (180, 200, 220) if state == 0 else (120, 40, 40) if state == 2 else RED
    d.rectangle([x - 44, y - 30, x + 44, y + 40], fill=(30, 38, 52), outline=col, width=5)
    for i in range(3):
        for j in range(2):
            c = (255, 220, 120) if state == 0 else (60, 20, 20) if state == 2 else (255, 80, 80)
            d.rectangle([x - 32 + i * 24, y - 18 + j * 24, x - 18 + i * 24, y - 6 + j * 24], fill=c)
    d.line([x, y - 30, x, y - 70], fill=col, width=5)
    d.arc([x - 26, y - 96, x + 26, y - 44], 220, 320, fill=col, width=4)


def network(t, dur, fail_at=0.35):
    img = base_night()
    d = ImageDraw.Draw(img)
    tf = dur * fail_at
    for i, (a, b) in enumerate(EDGES):
        (x1, y1), (x2, y2) = NODES[a], NODES[b]
        dead = t > tf + 0.25 * i % 1.2 + 0.4
        col = (90, 30, 30) if dead else (RED if t > tf else (70, 110, 150))
        d.line([x1, y1, x2, y2], fill=col, width=6)
        if not dead:
            n = 2 if t < tf else 7
            for k in range(n):
                p = ((t * (0.6 if t < tf else 1.8) + k / n + i * 0.13) % 1)
                x, y = lerp(x1, x2, p), lerp(y1, y2, p)
                r = 8 if t < tf else 11
                d.ellipse([x - r, y - r, x + r, y + r], fill=(150, 220, 255) if t < tf else (255, 170, 60))
    for i, (x, y) in enumerate(NODES):
        st = 0 if t < tf else (1 if t < tf + 0.3 + i * 0.18 else 2)
        if st == 1 and int(t * 10) % 2:
            st = 2
        _node_icon(d, x, y, st)
        if st == 2:
            d.line([x - 30, y - 20, x + 30, y + 30], fill=RED, width=8)
            d.line([x + 30, y - 20, x - 30, y + 30], fill=RED, width=8)
    if t > tf:
        k = back_out((t - tf - 0.1) / 0.3)
        if k > 0:
            paste_center(img, stamp("PANE NA REDE", 66), 540, 160, scale=0.6 + 0.4 * k, rot=4, alpha=min(1, k))
    return img


# ---------------- cabos e roteador ----------------
def cables(t, dur):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    s = 2
    over = clamp((t - 0.6) / 1.2)
    shake = math.sin(t * 50) * 6 * over
    # cabo de cobre (esquerda)
    for i in range(7):
        y = (560 + i * 22) * s
        d.line([0, y, 330 * s, y + (i - 3) * 6 * s], fill=(196, 110, 50) if i % 2 else (230, 140, 70), width=16 * s)
    d.rounded_rectangle([-40 * s, 530 * s, 120 * s, 740 * s], 30 * s, fill=(30, 30, 34))
    # fibra (direita)
    for i in range(5):
        y = (580 + i * 34) * s
        glow = 160 + int(90 * math.sin(t * 6 + i))
        d.line([760 * s, y, W * s, y + (i - 2) * 10 * s], fill=(80, glow, 255), width=6 * s)
    # roteador
    rx, ry = (540 + shake) * s, 640 * s
    d.rounded_rectangle([rx - 230 * s, ry - 110 * s, rx + 230 * s, ry + 110 * s], 26 * s, fill=(36, 40, 50),
                        outline=(120, 130, 150), width=6 * s)
    for i in range(8):
        on = (int(t * 12 + i * 3) % 3) != 0
        c = (90, 230, 120) if over < 0.3 else RED
        if not on:
            c = (40, 40, 40)
        d.ellipse([rx - 180 * s + i * 50 * s, ry - 20 * s, rx - 150 * s + i * 50 * s, ry + 10 * s], fill=c)
    for i in range(3):
        d.line([rx - 140 * s + i * 140 * s, ry - 110 * s, rx - 170 * s + i * 160 * s, ry - 240 * s], fill=(120, 130, 150),
               width=8 * s)
    # pacotes de dados entrando
    n = int(4 + 40 * over)
    for k in range(n):
        p = (t * (0.7 + over) + k / max(1, n)) % 1
        y = (520 + (k * 37) % 260) * s
        x = lerp(0, rx - 230 * s, p)
        d.rectangle([x, y, x + 22 * s, y + 14 * s], fill=(255, 190, 70) if over > 0.3 else (150, 220, 255))
    # faíscas
    if over > 0.5:
        rng = random.Random(int(t * 15))
        for _ in range(14):
            a = rng.uniform(0, 2 * math.pi)
            r0 = 240 * s
            r1 = r0 + rng.uniform(30, 120) * s
            d.line([rx + math.cos(a) * r0, ry + math.sin(a) * r0 * 0.5, rx + math.cos(a) * r1, ry + math.sin(a) * r1 * 0.5],
                   fill=(255, 230, 120), width=5 * s)
    img.alpha_composite(down(lay))
    dd = ImageDraw.Draw(img)
    f = font("oswald", 46, 700)
    dd.text((170, 420), "COBRE", font=f, fill=(230, 140, 70), anchor="mm")
    dd.text((920, 420), "FIBRA", font=f, fill=(120, 200, 255), anchor="mm")
    if over > 0.4:
        k = back_out((over - 0.4) / 0.3)
        paste_center(img, stamp("SOBRECARGA", 70), 540, 230, scale=0.6 + 0.4 * k, rot=-4, alpha=min(1, k))
    return img


# ---------------- painel de partidas ----------------
FLIGHTS = [("NOVA YORK", "15:40"), ("CHICAGO", "15:55"), ("ATLANTA", "16:05"), ("DALLAS", "16:20"),
           ("DENVER", "16:35"), ("MIAMI", "16:50"), ("SEATTLE", "17:10"), ("BOSTON", "17:25")]


def board(t, dur, counter=None):
    img = base_night()
    d = ImageDraw.Draw(img)
    x0, y0, x1 = 50, 330, 1030
    d.rectangle([x0 - 14, y0 - 120, x1 + 14, y0 + 8 * 96 + 30], fill=(8, 9, 12), outline=(60, 64, 72), width=6)
    d.text((x0 + 10, y0 - 62), "PARTIDAS", font=font("oswald", 56, 700), fill=AMBER, anchor="lm")
    fm = font("courier", 44)
    for i, (city, hr) in enumerate(FLIGHTS):
        y = y0 + 20 + i * 96
        d.rectangle([x0, y, x1, y + 80], fill=(18, 20, 26))
        d.text((x0 + 20, y + 40), hr, font=fm, fill=AMBER, anchor="lm")
        d.text((x0 + 200, y + 40), city, font=fm, fill=WHITE, anchor="lm")
        tf = 0.25 + i * 0.22
        if t < tf:
            st, col = "NO HORÁRIO", (110, 220, 130)
        elif t < tf + 0.18:
            st, col = random.Random(int(t * 40) + i).choice(["#$%&@!", "ATRAS.", "??????"]), WHITE
        else:
            st, col = "CANCELADO", (255, 70, 70)
        d.text((x1 - 20, y + 40), st, font=fm, fill=col, anchor="rm")
    if counter:
        k = ease_out((t - 0.3) / max(0.8, dur * 0.6))
        val = int(counter * k)
        txt = f"{val:,}".replace(",", ".")
        f = font("anton", 130)
        cx, y = 300, 1190
        d.rectangle([cx - 230, y - 85, cx + 230, y + 85], fill=RED)
        d.text((cx, y), txt, font=f, fill=WHITE, anchor="mm")
        d.rectangle([cx - 230, y + 85, cx + 230, y + 150], fill=(8, 8, 10))
        d.text((cx, y + 118), "VOOS CANCELADOS", font=font("oswald", 44, 700), fill=WHITE, anchor="mm")
    return img


SCENES = {"clock": clock, "grounded": grounded, "network": network, "cables": cables, "board": board}


# ---------------- gráfico ao vivo ----------------
def chart(t, dur, trend="down", label="", value=""):
    img = base_night()
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 80, 300, 1000, 1150
    d.rectangle([x0, y0, x1, y1], fill=(12, 15, 22), outline=(60, 68, 84), width=4)
    for i in range(1, 6):
        y = y0 + i * (y1 - y0) / 6
        d.line([x0, y, x1, y], fill=(30, 36, 48), width=2)
    rng = random.Random(7 if trend == "down" else 3)
    pts, v = [], (0.8 if trend == "down" else 0.2)
    for i in range(60):
        v += rng.uniform(-0.035, 0.035) + (-0.01 if trend == "down" else 0.01)
        v = clamp(v, 0.05, 0.95)
        pts.append(v)
    k = clamp(t / max(0.8, dur * 0.75))
    n = max(2, int(len(pts) * k))
    col = (230, 60, 60) if trend == "down" else (70, 210, 120)
    xy = [(x0 + 30 + i * (x1 - x0 - 60) / 59, y1 - 40 - p * (y1 - y0 - 80)) for i, p in enumerate(pts[:n])]
    d.polygon(xy + [(xy[-1][0], y1), (xy[0][0], y1)], fill=col[:3] + (50,))
    d.line(xy, fill=col, width=10, joint="curve")
    lx, ly = xy[-1]
    r = 16 + 6 * math.sin(t * 8)
    d.ellipse([lx - r, ly - r, lx + r, ly + r], fill=col)
    if label:
        d.text((x0 + 30, y0 - 50), label.upper(), font=font("oswald", 52, 700), fill=WHITE, anchor="lm")
    if value:
        f = font("anton", 110)
        tw = text_size(value, f)[0]
        d.rectangle([x1 - tw - 60, y0 + 30, x1 - 20, y0 + 170], fill=col)
        d.text((x1 - 40 - tw / 2, y0 + 100), value, font=f, fill=WHITE, anchor="mm")
        ax, ay = x1 - 40 - tw / 2, y0 + 215
        tri = [(ax - 30, ay - 22), (ax + 30, ay - 22), (ax, ay + 26)] if trend == "down" else \
              [(ax - 30, ay + 22), (ax + 30, ay + 22), (ax, ay - 26)]
        d.polygon(tri, fill=col)
    return img


# ---------------- tribunal ----------------
def court(t, dur, label="TRIBUNAL"):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    s = 2
    # colunas e frontão
    d.polygon([(90 * s, 420 * s), (990 * s, 420 * s), (540 * s, 220 * s)], fill=(60, 66, 80))
    d.rectangle([90 * s, 420 * s, 990 * s, 460 * s], fill=(70, 76, 90))
    for i in range(6):
        x = (140 + i * 160) * s
        d.rectangle([x, 470 * s, x + 70 * s, 1000 * s], fill=(80, 86, 100))
    d.rectangle([60 * s, 1000 * s, 1020 * s, 1060 * s], fill=(70, 76, 90))
    # martelo batendo
    hit = (t * 1.3) % 1
    ang = -40 + 40 * ease_in(clamp(hit / 0.25)) if hit < 0.25 else -40 * ease_out(clamp((hit - 0.25) / 0.6))
    cx, cy = 600 * s, 1250 * s
    d.rounded_rectangle([cx - 240 * s, cy + 60 * s, cx + 160 * s, cy + 110 * s], 10 * s, fill=(110, 70, 40))
    a = math.radians(ang)
    px, py = cx + 120 * s, cy + 40 * s
    hx, hy = px - math.cos(a) * 260 * s, py + math.sin(a) * 260 * s
    d.line([px, py, hx, hy], fill=(150, 100, 60), width=26 * s)
    hd = [(hx + math.cos(a + math.pi / 2) * 70 * s * sx - math.cos(a) * 50 * s * sy,
           hy - math.sin(a + math.pi / 2) * 70 * s * sx + math.sin(a) * 50 * s * sy) for sx, sy in
          ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    d.polygon(hd, fill=(130, 84, 48))
    img.alpha_composite(down(lay))
    dd = ImageDraw.Draw(img)
    if hit < 0.35 and hit > 0.22:
        for i in range(6):
            aa = i * math.pi / 5 + math.pi
            dd.line([600 + math.cos(aa) * 60, 1300 + math.sin(aa) * 30, 600 + math.cos(aa) * 130, 1300 + math.sin(aa) * 70],
                    fill=AMBER, width=6)
    dd.text((540, 360), label.upper(), font=font("anton", 60), fill=WHITE, anchor="mm")
    return img


# ---------------- jornal girando ----------------
def newspaper(t, dur, headline="URGENTE", sub=""):
    img = base_night()
    k = ease_out(t / 0.8)
    paper = Image.new("RGBA", (860, 1100), (238, 234, 222, 255))
    d = ImageDraw.Draw(paper)
    d.text((430, 90), "O DIÁRIO", font=font("anton", 110), fill=INK, anchor="mm")
    d.line([40, 160, 820, 160], fill=INK, width=6)
    hl = wrap(headline.upper(), font("anton", 120), 780)
    for i, l in enumerate(hl[:3]):
        d.text((430, 260 + i * 130), l, font=font("anton", 120), fill=RED if i == 0 else INK, anchor="mm")
    y = 260 + len(hl[:3]) * 130
    if sub:
        for i, l in enumerate(wrap(sub, font("oswald", 44, 600), 780)[:2]):
            d.text((430, y + i * 56), l, font=font("oswald", 44, 600), fill=(60, 60, 64), anchor="mm")
    rng = random.Random(headline)
    for i in range(10):
        yy = y + 160 + i * 34
        if yy > 1060:
            break
        d.rectangle([40, yy, 40 + rng.uniform(0.6, 1) * 360, yy + 14], fill=(150, 150, 156))
        d.rectangle([450, yy, 450 + rng.uniform(0.6, 1) * 360, yy + 14], fill=(150, 150, 156))
    paste_center(img, paper, 540, 820, scale=lerp(0.1, 0.92, k), rot=lerp(720, -3, k))
    return img


# ---------------- dinheiro escorrendo ----------------
def money(t, dur, label="", out=True):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    s = 2
    d.polygon([(200 * s, 560 * s), (880 * s, 560 * s), (540 * s, 330 * s)], fill=(70, 76, 90))
    for i in range(4):
        x = (250 + i * 160) * s
        d.rectangle([x, 590 * s, x + 80 * s, 940 * s], fill=(84, 90, 104))
    d.rectangle([180 * s, 940 * s, 900 * s, 990 * s], fill=(70, 76, 90))
    d.text((540 * s, 500 * s), "BANCO", font=font("anton", 70 * s), fill=WHITE, anchor="mm")
    rng = random.Random(4)
    for k in range(26):
        ph = (t * 0.5 + rng.random()) % 1
        x0 = 540 + rng.uniform(-260, 260)
        y = (990 + ph * 520) if out else (1500 - ph * 520)
        x = x0 + math.sin(ph * 9 + k) * 50
        rot = math.sin(ph * 7 + k) * 0.6
        w_, h_ = 110 * s, 54 * s
        cx, cy = x * s, y * s
        pts = [(cx + math.cos(rot) * w_ / 2 * sx - math.sin(rot) * h_ / 2 * sy,
                cy + math.sin(rot) * w_ / 2 * sx + math.cos(rot) * h_ / 2 * sy) for sx, sy in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
        d.polygon(pts, fill=(80, 150, 90), outline=(40, 90, 50))
    img.alpha_composite(down(lay))
    if label:
        ImageDraw.Draw(img).text((540, 250), label.upper(), font=font("anton", 70), fill=WHITE, anchor="mm")
    return img


SCENES.update({"chart": chart, "court": court, "newspaper": newspaper, "money": money})


# ---------------- loja de varejo à noite (letreiro apagando) ----------------
def store(t, dur, sign="LOJA", off_at=None):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    s = 2
    d.rectangle([0, 1250 * s, W * s, H * s], fill=(24, 26, 32))
    d.rectangle([60 * s, 420 * s, 1020 * s, 1250 * s], fill=(58, 62, 74))
    on = off_at is None or t < off_at or (t - off_at < 0.5 and int((t - off_at) * 14) % 2 == 0)
    sc = (235, 60, 60) if on else (70, 40, 44)
    d.rounded_rectangle([140 * s, 470 * s, 940 * s, 640 * s], 18 * s, fill=(20, 22, 28))
    d.text((540 * s, 555 * s), sign, font=font("anton", 120 * s), fill=sc, anchor="mm")
    for i in range(8):
        x0 = 60 + i * 120
        d.polygon([(x0 * s, 680 * s), ((x0 + 120) * s, 680 * s), ((x0 + 120) * s, 760 * s), ((x0 + 60) * s, 790 * s),
                   (x0 * s, 760 * s)], fill=RED if i % 2 == 0 else (230, 228, 220))
    win = (250, 214, 140) if on else (34, 38, 48)
    for x0 in (110, 600):
        d.rectangle([x0 * s, 830 * s, (x0 + 370) * s, 1180 * s], fill=win, outline=(30, 32, 40), width=10 * s)
        if on:
            for k in range(3):
                d.rectangle([(x0 + 40 + k * 110) * s, 1060 * s, (x0 + 120 + k * 110) * s, 1180 * s],
                            fill=(180, 60, 50) if k % 2 else (70, 110, 160))
    d.rectangle([470 * s, 900 * s, 610 * s, 1250 * s], fill=(30, 32, 40))
    img.alpha_composite(down(lay))
    if on:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).rounded_rectangle([140, 470, 940, 640], 18, fill=(235, 60, 60, 90))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
    return img


# ---------------- risco sacado: loja, fornecedor e banco ----------------
def _node(d, cx, cy, title, col, s=2):
    d.rounded_rectangle([(cx - 190) * s, (cy - 85) * s, (cx + 190) * s, (cy + 85) * s], 22 * s, fill=col,
                        outline=(240, 240, 236), width=6 * s)
    d.text((cx * s, cy * s), title, font=font("anton", 66 * s), fill=WHITE, anchor="mm")


def _flow(d, a, b, k, col, label, s=2, lp=0.5, lab=None):
    if k <= 0:
        return
    (ax, ay), (bx, by) = a, b
    ex, ey = lerp(ax, bx, k), lerp(ay, by, k)
    d.line([ax * s, ay * s, ex * s, ey * s], fill=col, width=14 * s)
    ang = math.atan2(ey - ay, ex - ax)
    tip = [(ex * s + math.cos(ang) * 34 * s, ey * s + math.sin(ang) * 34 * s),
           (ex * s + math.cos(ang + 2.4) * 34 * s, ey * s + math.sin(ang + 2.4) * 34 * s),
           (ex * s + math.cos(ang - 2.4) * 34 * s, ey * s + math.sin(ang - 2.4) * 34 * s)]
    d.polygon(tip, fill=col)
    if k > 0.6 and label and lab is not None:
        mx, my = lerp(ax, bx, lp), lerp(ay, by, lp)
        f = font("oswald", 40 * s, 700)
        tw = text_size(label, f)[0]
        d.rounded_rectangle([mx * s - tw / 2 - 18 * s, (my - 34) * s, mx * s + tw / 2 + 18 * s, (my + 34) * s], 14 * s,
                            fill=(14, 14, 18))
        d.text((mx * s, my * s), label, font=f, fill=col, anchor="mm")
    if lab is None and label:
        return (a, b, k, col, label, lp)


def sacado(t, dur, steps=(0.2, 1.4, 2.8, 4.2)):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    F, L, B = (380, 420), (380, 790), (380, 1160)
    k = [clamp((t - st) / 0.7) for st in steps]
    labs = [_flow(d, (F[0] + 60, F[1] + 90), (L[0] + 60, L[1] - 95), ease_out(k[0]), (235, 235, 230), "MERCADORIA"),
            _flow(d, (150, B[1]), (150, F[1]), ease_out(k[1]), (90, 200, 120), "BANCO PAGA", lp=0.75),
            _flow(d, (L[0] + 150, L[1] + 90), (B[0] + 150, B[1] - 95), ease_out(k[2]), AMBER, "+ JUROS")]
    d.line([(150 * 2, B[1] * 2), ((B[0] - 190) * 2, B[1] * 2)], fill=(90, 200, 120), width=28) if k[1] > 0 else None
    d.line([(150 * 2, F[1] * 2), ((F[0] - 190) * 2, F[1] * 2)], fill=(90, 200, 120), width=28) if k[1] > 0.95 else None
    _node(d, *F, "FORNECEDOR", (60, 66, 82))
    _node(d, *L, "LOJA", RED)
    _node(d, *B, "BANCO", (40, 90, 70))
    for x in labs:
        if x:
            a, b, kk, col, label, lp = x
            _flow(d, a, b, 0.0001 if False else kk, col, label, lp=lp, lab=True) if kk > 0.6 else None
    img.alpha_composite(down(lay))
    if k[3] > 0:
        st = stamp("DÍVIDA ESCONDIDA", size=72)
        paste_center(img, st, 380, 1390, scale=lerp(1.8, 0.9, back_out(k[3])), rot=-6, alpha=clamp(k[3] * 3))
    return img


SCENES.update({"store": store, "sacado": sacado})
