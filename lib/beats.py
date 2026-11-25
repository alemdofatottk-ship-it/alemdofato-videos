"""Tipos de batida do curto: txt, sp, map, dos, type, poll, follow, intro (capa)."""
import math, random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
from core import *
import scenes, mapa
from people import person, place


# ======================= TXT (tela cinza sincronizada) =======================
def layout_txt(words, maxw=930, maxlines=4):
    """words: lista de (texto, destaque?). Retorna fonte, posições."""
    for size in range(170, 60, -6):
        f = font("anton", size)
        sp = size * 0.28
        lines, cur, curw = [], [], 0
        for w, hl in words:
            ww = text_size(w, f)[0] + (36 if hl else 0)
            if cur and curw + sp + ww > maxw:
                lines.append((cur, curw))
                cur, curw = [], 0
            cur.append((w, hl, ww))
            curw += (sp if len(cur) > 1 else 0) + ww
        if cur:
            lines.append((cur, curw))
        if len(lines) <= maxlines:
            break
    lh = size * 1.22
    top = 1000 - lh * len(lines) / 2 + lh / 2
    pos = []
    for i, (ln, lw) in enumerate(lines):
        x = 540 - lw / 2
        for w, hl, ww in ln:
            pos.append((w, hl, x + ww / 2, top + i * lh))
            x += ww + sp
    return f, pos


def render_txt(b, t):
    img = gray_bg().convert("RGBA")
    f, pos = b["_layout"]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for (w, hl, cx, cy), wt in zip(pos, b["_wt"]):
        k = (t - wt) / 0.16
        if k < 0:
            continue
        sc = 1 + 0.28 * (1 - ease_out(k))
        tw, th, bb = text_size(w, f)
        if hl:
            pw, ph = (tw + 36) * sc / 2, (f.size * 0.62) * sc
            d.rectangle([cx - pw, cy - ph, cx + pw, cy + ph], fill=RED)
        if sc > 1.01:
            fs = font("anton", int(f.size * sc))
            d.text((cx + 4, cy + 6), w, font=fs, fill=(0, 0, 0, 120), anchor="mm")
            d.text((cx, cy), w, font=fs, fill=WHITE, anchor="mm")
        else:
            d.text((cx + 4, cy + 6), w, font=f, fill=(0, 0, 0, 120), anchor="mm")
            d.text((cx, cy), w, font=f, fill=WHITE, anchor="mm")
    img.alpha_composite(lay)
    img.alpha_composite(vignette_layer(0.4))
    return img


# ======================= cartões do dossiê =======================
def card_fact(title, sub, w=840):
    f1, f2 = font("anton", 150), font("oswald", 52, 600)
    subl = wrap(sub.upper(), f2, w - 120)
    h = 60 + 170 + len(subl) * 66 + 50
    s = 2
    lay = ss_layer(w, h)
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 0, w * s, h * s], fill=PAPER)
    d.rectangle([0, 0, 18 * s, h * s], fill=RED)
    im = down(lay)
    d = ImageDraw.Draw(im)
    d.text((60, 60 + 80), title, font=f1, fill=INK, anchor="lm")
    for i, l in enumerate(subl):
        d.text((60, 60 + 170 + 33 + i * 66), l, font=f2, fill=(70, 70, 76), anchor="lm")
    return im


def card_num(num, label, w=840):
    f1, f2 = font("anton", 190), font("oswald", 54, 700)
    ll = wrap(label.upper(), f2, w - 100)
    h = 260 + len(ll) * 68 + 40
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h], fill=(16, 16, 20))
    d.rectangle([0, 0, w, 14], fill=RED)
    d.text((w / 2, 150), num, font=f1, fill=RED, anchor="mm")
    for i, l in enumerate(ll):
        d.text((w / 2, 270 + i * 68), l, font=f2, fill=WHITE, anchor="mm")
    return im


def card_doc(title, lines_n=7, stamp_txt=None, w=840):
    h = 420
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h], fill=(244, 240, 228), outline=(180, 170, 150), width=3)
    d.text((40, 60), title.upper(), font=font("oswald", 50, 700), fill=INK, anchor="lm")
    d.line([40, 100, w - 40, 100], fill=INK, width=3)
    rng = random.Random(title)
    for i in range(lines_n):
        y = 140 + i * 36
        d.rectangle([40, y, 40 + rng.uniform(0.5, 0.95) * (w - 80), y + 12], fill=(150, 150, 156))
    if stamp_txt:
        st = scenes.stamp(stamp_txt, 90)
        paste_center(im, st, w * 0.62, h * 0.6, rot=-12)
    return im


def card_stamp(text, sub=None):
    return scenes.stamp(text, 110, sub=sub)


# ======================= DOS (pasta) =======================
SLOTS = [(540, 640), (540, 1040)]
BOX = (840, 360)


@lru_cache(None)
def folder(title):
    img = night_bg().convert("RGBA")
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 90, 320, 990, 1410
    d.rounded_rectangle([x0 + 14, y0 + 18, x1 + 14, y1 + 18], 18, fill=(0, 0, 0, 120))
    fs = 64
    while fs > 40 and text_size(title, font("anton", fs))[0] > 450:
        fs -= 2
    tabw = max(380, text_size(title, font("anton", fs))[0] + 70)
    d.rounded_rectangle([x0, y0 - 60, x0 + tabw, y0 + 30], 18, fill=(196, 168, 116))
    d.rounded_rectangle([x0, y0, x1, y1], 18, fill=MANILA)
    d.rectangle([x0 + 30, y0 + 40, x1 - 30, y1 - 30], fill=(240, 236, 224))
    for y in range(y0 + 120, y1 - 40, 46):
        d.line([x0 + 50, y, x1 - 50, y], fill=(200, 210, 226), width=2)
    d.line([x0 + 120, y0 + 40, x0 + 120, y1 - 30], fill=(230, 150, 150), width=3)
    d.text((x0 + 30, y0 - 16), title, font=font("anton", fs), fill=INK, anchor="lm")
    st = scenes.stamp("CONFIDENCIAL", 50)
    paste_center(img, st, x1 - 175, y0 - 10, rot=6)
    img.alpha_composite(vignette_layer(0.45))
    return img


def item_state(T, ti, img, slot, rot):
    """Retorna (cx, cy, escala, rot, alpha, dim) do item no tempo absoluto T."""
    big = min(1.0, 940 / img.width, 1100 / img.height)
    small = min(1.0, BOX[0] / img.width, BOX[1] / img.height)
    dt = T - ti
    if dt < 0:
        return None
    if dt < 0.3:
        k = back_out(dt / 0.3)
        return (540, 900, big * (0.4 + 0.6 * k), 0, clamp(dt / 0.12), clamp(dt / 0.2))
    if dt < 1.15:
        return (540, 900, big, 0, 1, 1)
    if dt < 1.6:
        k = ease_out((dt - 1.15) / 0.45)
        sx, sy = SLOTS[slot]
        return (lerp(540, sx, k), lerp(900, sy, k), lerp(big, small, k), rot * k, 1, 1 - k)
    sx, sy = SLOTS[slot]
    return (sx, sy, small, rot, 1, 0)


def render_dos(b, t, T):
    img = folder(b.get("title", "CASO")).copy()
    active = None
    for it in b["_items"]:
        st = item_state(T, it["t"], it["img"], it["slot"], it["rot"])
        if st is None:
            continue
        if st[5] > 0:
            active = (it, st)
            continue
        paste_center(img, it["img"], st[0], st[1], st[2], st[3], st[4])
    if active:
        it, st = active
        dim = Image.new("RGBA", (W, H), (0, 0, 0, int(150 * st[5])))
        img.alpha_composite(dim)
        paste_center(img, it["img"], st[0], st[1], st[2], st[3], st[4])
    return img


# ======================= TYPE (máquina de escrever) =======================
def render_type(b, t):
    img = night_bg().convert("RGBA")
    d = ImageDraw.Draw(img)
    dur = b["t1"] - b["t0"]
    fly = clamp((t - (dur - 0.55)) / 0.5)
    text = b["text"]
    k = clamp((t - 0.15) / max(0.5, dur - 0.9))
    n = int(len(text) * k)
    # papel
    f = font("elite", 58)
    lines = wrap(text[:n] if n else "", f, 600)
    full_lines = wrap(text, f, 600)
    ph = 140 + len(full_lines) * 80
    paper = Image.new("RGBA", (720, ph + 120), (246, 242, 230, 255))
    pd = ImageDraw.Draw(paper)
    for i, l in enumerate(lines):
        pd.text((60, 90 + i * 80), l, font=f, fill=(30, 30, 34), anchor="lm")
    if n < len(text) and int(t * 4) % 2 == 0:
        last = lines[-1] if lines else ""
        cx = 60 + text_size(last, f)[0] + 6
        pd.rectangle([cx, 90 + max(0, len(lines) - 1) * 80 - 28, cx + 4, 90 + max(0, len(lines) - 1) * 80 + 28], fill=RED)
    base_y = 1240  # máquina 420 px abaixo do centro do desenho original
    py = base_y - 140 - paper.height + 120 + (len(full_lines) - len(lines)) * 0
    if fly > 0:
        paste_center(img, paper, 540, lerp(py + paper.height / 2, 520, ease_in(fly)), scale=lerp(1, 0.35, fly),
                     rot=lerp(0, 8, fly), alpha=1 - fly * 0.8)
    else:
        img.alpha_composite(paper, (180, int(py)))
    # máquina
    s = 2
    lay = ss_layer(W, H)
    dd = ImageDraw.Draw(lay)
    jit = (math.sin(t * 60) * 2 if fly == 0 and n < len(text) else 0) * s
    dd.rounded_rectangle([140 * s, (base_y - 150) * s + jit, 940 * s, (base_y - 70) * s + jit], 30 * s, fill=(20, 22, 26))
    dd.polygon([(120 * s, (base_y - 80) * s), (960 * s, (base_y - 80) * s), (1010 * s, (base_y + 210) * s),
                (70 * s, (base_y + 210) * s)], fill=(34, 36, 42))
    for r in range(4):
        for c in range(11 - (r % 2)):
            x = (170 + c * 70 + (r % 2) * 35) * s
            y = (base_y - 20 + r * 58) * s
            press = (int(t * 14) + c * 3 + r) % 17 == 0 and n < len(text)
            dd.ellipse([x, y + (6 * s if press else 0), x + 46 * s, y + 46 * s + (6 * s if press else 0)],
                       fill=(230, 226, 214), outline=(10, 10, 10), width=3 * s)
    dd.rectangle([110 * s, (base_y - 175) * s, 970 * s, (base_y - 150) * s], fill=(70, 74, 82))
    img.alpha_composite(down(lay))
    return img


# ======================= POLL =======================
def render_poll(b, t):
    img = gray_bg().convert("RGBA")
    d = ImageDraw.Draw(img)
    k = back_out(t / 0.35)
    q = b["question"]
    f = font("anton", 96)
    ql = wrap(q.upper(), f, 760)
    bh = 120 + len(ql) * 112
    by0 = 360
    s = max(0.01, k)
    bal = Image.new("RGBA", (900, bh + 80), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bal)
    bd.rounded_rectangle([0, 0, 900, bh], 50, fill=WHITE)
    bd.polygon([(160, bh - 4), (260, bh - 4), (140, bh + 76)], fill=WHITE)
    for i, l in enumerate(ql):
        bd.text((450, 60 + 56 + i * 112), l, font=f, fill=INK, anchor="mm")
    paste_center(img, bal, 540, by0 + bal.height / 2, scale=s, alpha=clamp(t / 0.15))
    opts = b["options"]
    tap = b.get("tap", 0)
    tt = t if t < 1.2 else 1.2 + (t - 1.2) % 2.6
    by0 = 360 + 10 * math.sin(t * 2.4)
    for i, o in enumerate(opts):
        kk = back_out((t - 0.5 - i * 0.18) / 0.3)
        if kk <= 0:
            continue
        x = 540 + (i - (len(opts) - 1) / 2) * 420
        y = by0 + bh + 260
        pressed = 1.6 < tt < 2.1 and i == tap
        col = RED if i == 0 else (24, 26, 32)
        bw, bh2 = 380 * kk, 170 * kk
        if pressed:
            bw, bh2 = bw * 0.95, bh2 * 0.95
        d.rounded_rectangle([x - bw / 2, y - bh2 / 2, x + bw / 2, y + bh2 / 2], 40, fill=col, outline=WHITE, width=6)
        d.text((x, y), o, font=font("anton", max(8, int(96 * kk))), fill=WHITE, anchor="mm")
        if i == tap and 1.2 < tt < 2.2:
            cx, cy = x + 90, y + 60 - 30 * ease_io(clamp((tt - 1.2) / 0.4))
            rr = 36 + (20 * clamp((tt - 1.6) / 0.3) if tt > 1.6 else 0)
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=WHITE, width=6)
            d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(255, 255, 255))
    kk = ease_out((t - 1.0) / 0.4)
    if kk > 0:
        fl = wrap(b["post"].upper(), font("oswald", 54, 700), 900)
        y = by0 + bh + 520
        for i, l in enumerate(fl):
            d.text((540 + (1 - kk) * 60, y + i * 70), l, font=font("oswald", 54, 700), fill=(255, 255, 255, int(255 * kk)),
                   anchor="mm")
    img.alpha_composite(vignette_layer(0.4))
    return img


# ======================= FOLLOW =======================
def render_follow(b, t):
    img = night_bg().convert("RGBA")
    d = ImageDraw.Draw(img)
    cx, cy = 540, 760
    for i in range(3):
        ph = (t * 0.8 + i / 3) % 1
        r = 290 + ph * 260
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(206, 38, 38, int(230 * (1 - ph))), width=10)
    k = back_out(t / 0.4)
    paste_center(img, logo(560), cx, cy, scale=max(0.01, k) * (1 + 0.03 * math.sin(t * 5)))
    kk = ease_out((t - 0.3) / 0.4)
    if kk > 0:
        d.text((540, 1140), "ALÉM DO FATO", font=font("anton", 120), fill=WHITE, anchor="mm")
    kb = back_out((t - 0.5) / 0.3)
    if kb > 0:
        done = t > 1.3
        bw, bh = 460 * kb, 130 * kb
        y = 1330
        d.rounded_rectangle([540 - bw / 2, y - bh / 2, 540 + bw / 2, y + bh / 2], 65,
                            fill=(60, 62, 70) if done else RED)
        d.text((540 - (28 if done else 0), y), "SEGUINDO" if done else "SEGUIR", font=font("anton", max(8, int(74 * kb))),
               fill=WHITE, anchor="mm")
        if done:
            d.line([(680, y), (700, y + 22), (735, y - 24)], fill=WHITE, width=12, joint="curve")
        if 0.9 < t < 1.7:
            px, py = 640, 1380 - 30 * ease_io(clamp((t - 0.9) / 0.35))
            rr = 34 + (24 * clamp((t - 1.25) / 0.3) if t > 1.25 else 0)
            d.ellipse([px - rr, py - rr, px + rr, py + rr], outline=WHITE, width=6)
            d.ellipse([px - 20, py - 20, px + 20, py + 20], fill=WHITE)
    return img


# ======================= SP / MAP =======================
def render_sp(b, t):
    img = scenes.SCENES[b["scene"]](t, b["t1"] - b["t0"], **b.get("opts", {}))
    pr = b.get("person")
    if pr:
        pr = dict(pr)
        x = pr.pop("x", 800)
        p = person(t=t, **pr)
        place(img, p, x_center=x, feet_y=1480)
    return img


def render_map(b, t):
    return mapa.zoom_map(t, b["t1"] - b["t0"], **b["opts"])


RENDER = {"txt": render_txt, "sp": render_sp, "map": render_map, "type": render_type, "poll": render_poll,
          "follow": render_follow}
