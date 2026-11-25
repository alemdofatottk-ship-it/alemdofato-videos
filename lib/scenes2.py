"""Cenas novas (26/11/2026): celular com Pix, golpe de loja falsa, QR trocado, dinheiro pulverizado,
quadro de investigação, câmbio, plenário, tarifa na fronteira, embaixada e bandeiras. Mesmo estilo noir.
Conteúdo principal à esquerda/centro (x < 700) para o personagem ficar do lado direito."""
import math, random
from PIL import Image, ImageDraw, ImageFilter
from core import *
import scenes
from scenes import base_night, stamp, plane

S = 2


# ---------------------------------------------------------------- celular
def _phone_body(d, x0, y0, x1, y1):
    d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], 60 * S, fill=(12, 13, 17), outline=(70, 76, 90), width=8 * S)
    d.rounded_rectangle([(x0 + 22) * S, (y0 + 70) * S, (x1 - 22) * S, (y1 - 50) * S], 26 * S, fill=(236, 238, 242))
    d.rounded_rectangle([((x0 + x1) / 2 - 60) * S, (y0 + 28) * S, ((x0 + x1) / 2 + 60) * S, (y0 + 46) * S], 9 * S,
                        fill=(40, 42, 50))


PX0, PY0, PX1, PY1 = 110, 300, 640, 1300  # celular grande à esquerda
SX0, SY0, SX1 = PX0 + 22, PY0 + 70, PX1 - 22


def _bank_header(d, title, col=(30, 120, 95)):
    d.rounded_rectangle([SX0 * S, SY0 * S, SX1 * S, (SY0 + 120) * S], 26 * S, fill=col)
    d.rectangle([SX0 * S, (SY0 + 60) * S, SX1 * S, (SY0 + 120) * S], fill=col)
    d.text(((SX0 + SX1) / 2 * S, (SY0 + 62) * S), title, font=font("anton", 56 * S), fill=WHITE, anchor="mm")


def phone(t, dur, mode="pix_burst", count=600, block_at=None, amount="R$ 8,5 MI", stamp_txt="GOLPE", stamp_at=1.6,
          url="lojas-oficlal.com", bad=(10, 11), price_old="R$ 2.999", price_new="R$ 399", payee="J S COMERCIO LTDA",
          restore_at=None, title="BANCO"):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    _phone_body(d, PX0, PY0, PX1, PY1)
    cx = (SX0 + SX1) / 2
    if mode == "pix_burst":
        _bank_header(d, "PIX ENVIADOS")
        n = int(count * ease_io(clamp(t / max(0.8, dur * 0.7))))
        if block_at is not None:
            n = count  # a rajada já aconteceu: mostra o total e bloqueia
        d.text((cx * S, (SY0 + 190) * S), f"{n}", font=font("anton", 120 * S), fill=RED, anchor="mm")
        d.text((cx * S, (SY0 + 270) * S), "TRANSFERÊNCIAS", font=font("oswald", 38 * S, 700), fill=(60, 64, 74), anchor="mm")
        rng = random.Random(9)
        off = (t * 260) % 110 if (block_at is None or t < block_at) else (block_at * 260) % 110
        for i in range(8):
            y = SY0 + 330 + i * 110 - off
            if y < SY0 + 310 or y > PY1 - 160:
                continue
            v = rng.randint(3, 40) * 1000 + rng.randint(0, 9) * 100
            d.rounded_rectangle([(SX0 + 24) * S, y * S, (SX1 - 24) * S, (y + 92) * S], 18 * S, fill=WHITE,
                                outline=(210, 212, 218), width=3 * S)
            d.ellipse([(SX0 + 44) * S, (y + 22) * S, (SX0 + 92) * S, (y + 70) * S], fill=(30, 120, 95))
            d.text(((SX0 + 110) * S, (y + 30) * S), "Pix enviado", font=font("oswald", 30 * S, 700), fill=INK, anchor="lm")
            d.text(((SX0 + 110) * S, (y + 64) * S), f"conta {rng.randint(1, 25):02d} de outro banco",
                   font=font("oswald", 24 * S, 500), fill=(110, 112, 120), anchor="lm")
            d.text(((SX1 - 44) * S, (y + 46) * S), f"-R$ {v:,}".replace(",", "."), font=font("oswald", 30 * S, 700),
                   fill=RED, anchor="rm")
    elif mode == "shop":
        d.rounded_rectangle([(SX0 + 20) * S, (SY0 + 20) * S, (SX1 - 20) * S, (SY0 + 90) * S], 30 * S, fill=(220, 222, 228))
        f = font("oswald", 34 * S, 600)
        tx = SX0 + 50
        for k, ch in enumerate(url):
            col = RED if k in bad and t > 0.9 else (60, 64, 74)
            d.text((tx * S, (SY0 + 55) * S), ch, font=f, fill=col, anchor="lm")
            tx += text_size(ch, font("oswald", 34, 600))[0] + 2
        if t > 0.9:
            bx = SX0 + 50 + sum(text_size(c, font("oswald", 34, 600))[0] + 2 for c in url[:bad[0]])
            bw = sum(text_size(c, font("oswald", 34, 600))[0] + 2 for c in url[bad[0]:bad[-1] + 1])
            d.ellipse([(bx - 14) * S, (SY0 + 22) * S, (bx + bw + 14) * S, (SY0 + 92) * S], outline=RED, width=5 * S)
        d.rounded_rectangle([(SX0 + 40) * S, (SY0 + 130) * S, (SX1 - 40) * S, (SY0 + 470) * S], 20 * S, fill=(40, 44, 56))
        # produto genérico (TV)
        d.rounded_rectangle([(cx - 150) * S, (SY0 + 190) * S, (cx + 150) * S, (SY0 + 370) * S], 10 * S, fill=(14, 16, 22),
                            outline=(160, 166, 180), width=6 * S)
        d.rectangle([(cx - 20) * S, (SY0 + 370) * S, (cx + 20) * S, (SY0 + 410) * S], fill=(160, 166, 180))
        d.rectangle([(cx - 80) * S, (SY0 + 405) * S, (cx + 80) * S, (SY0 + 420) * S], fill=(160, 166, 180))
        po = font("oswald", 44 * S, 600)
        d.text((cx * S, (SY0 + 530) * S), price_old, font=po, fill=(130, 132, 140), anchor="mm")
        tw = text_size(price_old, font("oswald", 44, 600))[0]
        d.line([(cx - tw / 2 - 10) * S, (SY0 + 532) * S, (cx + tw / 2 + 10) * S, (SY0 + 528) * S], fill=RED, width=6 * S)
        pk = back_out(clamp((t - 0.3) / 0.4))
        fz = max(10, int(110 * pk))
        d.text((cx * S, (SY0 + 640) * S), price_new, font=font("anton", fz * S), fill=(20, 150, 90), anchor="mm")
        d.rounded_rectangle([(cx - 140) * S, (SY0 + 730) * S, (cx + 140) * S, (SY0 + 810) * S], 40 * S, fill=RED)
        d.text((cx * S, (SY0 + 770) * S), "SÓ NO PIX", font=font("anton", 50 * S), fill=WHITE, anchor="mm")
    elif mode == "qr":
        _bank_header(d, "PAGAR COM PIX")
        k = ease_io(clamp((t - 0.9) / 0.6))
        for q, (dx, col) in enumerate(((0, INK), (1, DRED))):
            if q == 1 and k <= 0:
                continue
            ox = cx - 170 + (SX1 - SX0) * (1 - k) * (q == 1)
            oy = SY0 + 230
            rng = random.Random(q + 5)
            d.rectangle([ox * S, oy * S, (ox + 340) * S, (oy + 340) * S], fill=WHITE)
            cell = 340 / 17
            for yy in range(17):
                for xx in range(17):
                    corner = (xx < 5 and yy < 5) or (xx > 11 and yy < 5) or (xx < 5 and yy > 11)
                    if corner:
                        on = xx in (0, 4, 12, 16) or yy in (0, 4, 12, 16) or (1 < xx % 12 < 3.5 and 1 < yy % 12 < 3.5)
                    else:
                        on = rng.random() < 0.48
                    if on:
                        d.rectangle([(ox + xx * cell) * S, (oy + yy * cell) * S, (ox + (xx + 1) * cell) * S,
                                     (oy + (yy + 1) * cell) * S], fill=col)
        lab = "CONTA DO GOLPISTA" if k > 0.6 else "LOJA"
        d.text((cx * S, (SY0 + 640) * S), "PAGANDO PARA:", font=font("oswald", 34 * S, 600), fill=(90, 94, 104), anchor="mm")
        d.text((cx * S, (SY0 + 710) * S), lab, font=font("anton", 64 * S), fill=RED if k > 0.6 else INK, anchor="mm")
    elif mode == "confirm":
        _bank_header(d, "CONFIRMAR PIX")
        d.text((cx * S, (SY0 + 210) * S), price_new, font=font("anton", 100 * S), fill=INK, anchor="mm")
        d.text((cx * S, (SY0 + 310) * S), "Você está pagando para", font=font("oswald", 32 * S, 500), fill=(90, 94, 104),
               anchor="mm")
        d.rounded_rectangle([(SX0 + 30) * S, (SY0 + 350) * S, (SX1 - 30) * S, (SY0 + 450) * S], 16 * S, fill=WHITE,
                            outline=(200, 202, 210), width=3 * S)
        d.text((cx * S, (SY0 + 400) * S), payee, font=font("oswald", 40 * S, 700), fill=INK, anchor="mm")
        k = ease_out(clamp((t - 0.6) / 0.5))
        if k > 0:
            r = 70 + 6 * math.sin(t * 5)
            mx, my = cx + 120, SY0 + 420
            d.ellipse([(mx - r) * S, (my - r) * S, (mx + r) * S, (my + r) * S], outline=AMBER, width=12 * S)
            d.line([(mx + r * 0.7) * S, (my + r * 0.7) * S, (mx + r * 0.7 + 90 * k) * S, (my + r * 0.7 + 90 * k) * S],
                   fill=AMBER, width=22 * S)
        d.rounded_rectangle([(SX0 + 40) * S, (SY0 + 760) * S, (SX1 - 40) * S, (SY0 + 850) * S], 45 * S,
                            fill=(160, 164, 172) if t > 1.2 else (30, 120, 95))
        d.text((cx * S, (SY0 + 805) * S), "CONFIRMAR", font=font("anton", 50 * S), fill=WHITE, anchor="mm")
    elif mode == "suspended":
        _bank_header(d, title)
        ok = restore_at is not None and t > restore_at
        col = (30, 150, 95) if ok else RED
        d.ellipse([(cx - 140) * S, (SY0 + 230) * S, (cx + 140) * S, (SY0 + 510) * S], outline=col, width=18 * S)
        if ok:
            d.line([((cx - 70) * S, (SY0 + 370) * S), ((cx - 15) * S, (SY0 + 430) * S), ((cx + 80) * S, (SY0 + 310) * S)],
                   fill=col, width=22 * S, joint="curve")
        else:
            a = t * 300
            d.arc([(cx - 140) * S, (SY0 + 230) * S, (cx + 140) * S, (SY0 + 510) * S], a, a + 70, fill=(40, 44, 54),
                  width=18 * S)
            d.line([(cx - 60) * S, (SY0 + 310) * S, (cx + 60) * S, (SY0 + 430) * S], fill=col, width=20 * S)
            d.line([(cx + 60) * S, (SY0 + 310) * S, (cx - 60) * S, (SY0 + 430) * S], fill=col, width=20 * S)
        d.text((cx * S, (SY0 + 600) * S), "PIX", font=font("anton", 90 * S), fill=INK, anchor="mm")
        d.text((cx * S, (SY0 + 700) * S), "VOLTANDO" if ok else "INDISPONÍVEL", font=font("anton", 70 * S), fill=col,
               anchor="mm")
    img.alpha_composite(down(lay))
    if mode == "pix_burst" and block_at is not None and t > block_at:
        k = clamp((t - block_at) / 0.35)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ov).rounded_rectangle([SX0, SY0, SX1, PY1 - 50], 26, fill=(120, 10, 10, int(120 * k)))
        img.alpha_composite(ov)
        paste_center(img, stamp("BLOQUEADO", 84), (PX0 + PX1) / 2, 820, scale=lerp(1.8, 1.0, back_out(k)), rot=-8,
                     alpha=clamp(k * 3))
    if mode == "shop" and t > stamp_at:
        k = clamp((t - stamp_at) / 0.35)
        paste_center(img, stamp(stamp_txt, 110), (PX0 + PX1) / 2, 700, scale=lerp(1.9, 1.0, back_out(k)), rot=-10,
                     alpha=clamp(k * 3))
    if mode == "confirm" and t > 1.2:
        k = clamp((t - 1.2) / 0.35)
        paste_center(img, stamp("NÃO É A LOJA? PARE.", 60), (PX0 + PX1) / 2, 1130, scale=lerp(1.6, 1.0, back_out(k)),
                     rot=-4, alpha=clamp(k * 3))
    return img


# ---------------------------------------------------------------- dinheiro pulverizado
def spread(t, dur, n=25, center="CONTA DO GOVERNO", label="25 INSTITUIÇÕES"):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    cx, cy = 360, 800
    rng = random.Random(3)
    pts = []
    for i in range(n):
        a = -math.pi / 2 + i * 2 * math.pi / n + rng.uniform(-0.08, 0.08)
        r = rng.uniform(270, 320)
        pts.append((cx + math.cos(a) * r * 1.0, cy + math.sin(a) * r * 1.35))
    for i, (x, y) in enumerate(pts):
        st = 0.15 + i * min(0.06, max(0.02, (dur * 0.5) / n))
        k = ease_out(clamp((t - st) / 0.35))
        if k <= 0:
            continue
        ex, ey = lerp(cx, x, k), lerp(cy, y, k)
        d.line([cx * S, cy * S, ex * S, ey * S], fill=(120, 200, 140, 200), width=5 * S)
        ph = (t * 1.4 + i * 0.13) % 1
        bx, by = lerp(cx, x, ph * k), lerp(cy, y, ph * k)
        d.rectangle([(bx - 16) * S, (by - 9) * S, (bx + 16) * S, (by + 9) * S], fill=(80, 150, 90))
        if k > 0.95:
            d.rounded_rectangle([(x - 30) * S, (y - 30) * S, (x + 30) * S, (y + 30) * S], 10 * S, fill=(60, 66, 82),
                                outline=(200, 204, 214), width=3 * S)
            d.text((x * S, y * S), f"{i + 1}", font=font("anton", 30 * S), fill=WHITE, anchor="mm")
    d.rounded_rectangle([(cx - 170) * S, (cy - 80) * S, (cx + 170) * S, (cy + 80) * S], 24 * S, fill=RED,
                        outline=WHITE, width=6 * S)
    f = font("anton", 50 * S)
    for j, l in enumerate(wrap(center, font("anton", 50), 300)[:2]):
        d.text((cx * S, (cy - 28 + j * 58) * S), l, font=f, fill=WHITE, anchor="mm")
    img.alpha_composite(down(lay))
    if label and t > 0.8:
        ImageDraw.Draw(img).text((360, 300), label, font=font("anton", 70), fill=AMBER, anchor="mm")
    return img


# ---------------------------------------------------------------- quadro de investigação
def board_inv(t, dur, title="INVESTIGAÇÃO", notes=("CONTA DA SEFA", "600 PIX", "25 BANCOS", "QUEM?")):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    d.rectangle([60 * S, 300 * S, 760 * S, 1260 * S], fill=(150, 112, 72), outline=(90, 62, 36), width=16 * S)
    rng = random.Random(11)
    spots = [(220, 470), (560, 450), (230, 860), (560, 900), (400, 1120)]
    for i, (x, y) in enumerate(spots[:len(notes)]):
        k = ease_out(clamp((t - 0.2 - i * 0.35) / 0.3))
        if k <= 0:
            continue
        w_, h_ = 270, 190
        d.rectangle([(x - w_ / 2) * S, (y - h_ / 2) * S, (x + w_ / 2) * S, (y + h_ / 2) * S],
                    fill=PAPER if i != len(notes) - 1 else (240, 220, 120))
        for j, l in enumerate(wrap(notes[i], font("anton", 44), 240)[:2]):
            d.text((x * S, (y - 22 + j * 50) * S), l, font=font("anton", 44 * S), fill=INK, anchor="mm")
        d.ellipse([(x - 12) * S, (y - h_ / 2 - 4) * S, (x + 12) * S, (y - h_ / 2 + 20) * S], fill=RED)
    # barbantes vermelhos
    kk = clamp((t - 0.4) / max(0.6, len(notes) * 0.35))
    for a, b in ((0, 1), (0, 2), (1, 3), (2, 4), (3, 4)):
        if a >= len(notes) or b >= len(notes):
            continue
        (ax, ay), (bx, by) = spots[a], spots[b]
        ay -= 95
        by -= 95
        e = clamp(kk * 5 - a)
        if e > 0:
            d.line([ax * S, ay * S, lerp(ax, bx, e) * S, lerp(ay, by, e) * S], fill=(200, 30, 30), width=5 * S)
    img.alpha_composite(down(lay))
    ImageDraw.Draw(img).text((410, 240), title, font=font("anton", 66), fill=WHITE, anchor="mm")
    return img


# ---------------------------------------------------------------- câmbio
def exchange(t, dur, start=5.50, end=6.00, label="DÓLAR COMERCIAL", flash=True, down_to=None):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([70 * S, 360 * S, 760 * S, 1120 * S], 30 * S, fill=(10, 11, 14), outline=(70, 76, 90), width=10 * S)
    d.text((415 * S, 450 * S), "CÂMBIO", font=font("anton", 80 * S), fill=AMBER, anchor="mm")
    d.text((415 * S, 560 * S), "US$ 1 =", font=font("oswald", 60 * S, 700), fill=(200, 204, 214), anchor="mm")
    k = ease_io(clamp(t / max(0.8, dur * 0.55)))
    v = lerp(start, end, k)
    if down_to is not None and t > dur * 0.6:
        v = lerp(end, down_to, ease_io(clamp((t - dur * 0.6) / max(0.4, dur * 0.3))))
    txt = f"R$ {v:.2f}".replace(".", ",")
    hit = v >= 5.995
    col = RED if (hit and flash and int(t * 6) % 2 == 0) else ((255, 90, 80) if hit else (90, 230, 140))
    if down_to is not None:
        col = (90, 230, 140)
    d.text((415 * S, 780 * S), txt, font=font("anton", 190 * S), fill=col, anchor="mm")
    up = down_to is None
    ax, ay = 415, 980
    tri = [(ax - 50, ay + 35), (ax + 50, ay + 35), (ax, ay - 40)] if up else [(ax - 50, ay - 35), (ax + 50, ay - 35),
                                                                            (ax, ay + 40)]
    d.polygon([(x * S, y * S) for x, y in tri], fill=(255, 90, 80) if up else (90, 230, 140))
    img.alpha_composite(down(lay))
    ImageDraw.Draw(img).text((415, 1190), label, font=font("oswald", 46, 700), fill=FOG, anchor="mm")
    return img


# ---------------------------------------------------------------- plenário / votação
def vote_panel(t, dur, yes=353, no=128, title="CÂMARA DOS DEPUTADOS", result="APROVADO"):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    # bancadas em arco
    for row in range(5):
        r = 230 + row * 70
        for j in range(13 + row * 3):
            a = math.pi + (j + 0.5) * math.pi / (13 + row * 3)
            x, y = 420 + math.cos(a) * r, 1190 + math.sin(a) * r * 0.55
            on = random.Random(row * 100 + j).random() < 0.73
            k = clamp((t - 0.2 - (row * 0.1 + j * 0.02)) / 0.2)
            col = (60, 66, 82) if k <= 0 else ((70, 200, 120) if on else (220, 60, 60))
            d.ellipse([(x - 13) * S, (y - 13) * S, (x + 13) * S, (y + 13) * S], fill=col)
    d.rounded_rectangle([90 * S, 330 * S, 750 * S, 760 * S], 26 * S, fill=(10, 11, 14), outline=(70, 76, 90), width=8 * S)
    k = ease_out(clamp((t - 0.3) / max(0.6, dur * 0.4)))
    if k > 0.97:
        k = 1.0
    d.text((240 * S, 460 * S), "SIM", font=font("anton", 70 * S), fill=(90, 230, 140), anchor="mm")
    d.text((600 * S, 460 * S), "NÃO", font=font("anton", 70 * S), fill=(255, 90, 80), anchor="mm")
    d.text((240 * S, 600 * S), f"{int(yes * k)}", font=font("anton", 140 * S), fill=WHITE, anchor="mm")
    d.text((600 * S, 600 * S), f"{int(no * k)}", font=font("anton", 140 * S), fill=WHITE, anchor="mm")
    img.alpha_composite(down(lay))
    ImageDraw.Draw(img).text((420, 270), title, font=font("anton", 52), fill=WHITE, anchor="mm")
    if result and k >= 0.99:
        kk = clamp((t - 0.3 - max(0.6, dur * 0.4)) / 0.3)
        paste_center(img, stamp(result, 80, color=(70, 200, 120)), 420, 860, scale=lerp(1.7, 1.0, back_out(kk)), rot=-6,
                     alpha=clamp(kk * 3))
    return img


# ---------------------------------------------------------------- tarifa na fronteira
def _sugar_sack(scale=1.0):
    s = 2
    w, h = int(240 * scale), int(260 * scale)
    lay = ss_layer(w, h)
    d = ImageDraw.Draw(lay)
    U = scale * s
    d.rounded_rectangle([14 * U, 40 * U, 226 * U, 250 * U], int(40 * U), fill=(228, 220, 196), outline=(150, 136, 100),
                        width=int(6 * U))
    d.polygon([(60 * U, 44 * U), (180 * U, 44 * U), (150 * U, 10 * U), (90 * U, 10 * U)], fill=(210, 200, 170))
    d.text((120 * U, 150 * U), "AÇÚCAR", font=font("anton", int(48 * U)), fill=(120, 60, 40), anchor="mm")
    return down(lay)


def tariff(t, dur, item="plane", pct="+10%", left="BRASIL", right="EUA"):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    gy = 980
    d.rectangle([0, gy * S, W * S, (gy + 16) * S], fill=(70, 76, 90))
    # cancela
    gx = 400
    d.rectangle([(gx - 18) * S, (gy - 330) * S, (gx + 18) * S, gy * S], fill=(200, 204, 214))
    k = ease_out(clamp((t - 0.2) / 0.5))
    ang = math.radians(lerp(80, 0, k))
    ex, ey = gx + math.cos(ang) * 300, gy - 300 - math.sin(ang) * 300
    for j in range(8):
        a0 = j / 8
        a1 = (j + 1) / 8
        d.line([lerp(gx, ex, a0) * S, lerp(gy - 300, ey, a0) * S, lerp(gx, ex, a1) * S, lerp(gy - 300, ey, a1) * S],
               fill=RED if j % 2 == 0 else WHITE, width=26 * S)
    img.alpha_composite(down(lay))
    dd = ImageDraw.Draw(img)
    dd.text((160, gy + 100), left, font=font("anton", 64), fill=(90, 210, 120), anchor="mm")
    dd.text((570, gy + 100), right, font=font("anton", 64), fill=(120, 160, 230), anchor="mm")
    # objeto vindo da esquerda e parando na cancela
    mv = ease_out(clamp(t / 1.0))
    x = lerp(-200, 230, mv) + math.sin(t * 3) * 4
    if item == "plane":
        p = plane(0.62)
        paste_center(img, p, x, gy - 420 + math.sin(t * 2) * 10)
    else:
        sk = _sugar_sack(1.0)
        for j in range(3):
            paste_center(img, sk, x - 60 + j * 60, gy - 130 - (j % 2) * 150, rot=(-6 + j * 6))
    if t > 0.7:
        kk = clamp((t - 0.7) / 0.35)
        tagim = stamp(pct, 120)
        paste_center(img, tagim, 430, 470, scale=lerp(1.8, 1.0, back_out(kk)), rot=-8, alpha=clamp(kk * 3))
    return img


# ---------------------------------------------------------------- bandeiras
def _flag_br(w=300):
    h = int(w * 0.7)
    lay = ss_layer(w, h)
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 0, w * S, h * S], fill=(0, 146, 63))
    d.polygon([(w * 0.08 * S, h / 2 * S), (w / 2 * S, h * 0.1 * S), (w * 0.92 * S, h / 2 * S), (w / 2 * S, h * 0.9 * S)],
              fill=(254, 221, 0))
    r = h * 0.25
    d.ellipse([(w / 2 - r) * S, (h / 2 - r) * S, (w / 2 + r) * S, (h / 2 + r) * S], fill=(0, 39, 118))
    d.arc([(w / 2 - r * 1.3) * S, (h / 2 - r * 0.6) * S, (w / 2 + r * 1.1) * S, (h / 2 + r * 1.9) * S], 215, 320,
          fill=WHITE, width=int(h * 0.04 * S))
    return down(lay)


def _flag_ar(w=300):
    h = int(w * 0.63)
    lay = ss_layer(w, h)
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 0, w * S, h * S], fill=(116, 172, 223))
    d.rectangle([0, h / 3 * S, w * S, 2 * h / 3 * S], fill=WHITE)
    r = h * 0.11
    cx, cy = w / 2, h / 2
    for i in range(16):
        a = i * math.pi / 8
        d.line([(cx + math.cos(a) * r) * S, (cy + math.sin(a) * r) * S, (cx + math.cos(a) * r * 1.6) * S,
                (cy + math.sin(a) * r * 1.6) * S], fill=(246, 180, 14), width=int(3 * S))
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=(246, 180, 14))
    return down(lay)


def _flag_us(w=300):
    h = int(w * 0.53)
    lay = ss_layer(w, h)
    d = ImageDraw.Draw(lay)
    for i in range(13):
        d.rectangle([0, i * h / 13 * S, w * S, (i + 1) * h / 13 * S], fill=(178, 34, 52) if i % 2 == 0 else WHITE)
    d.rectangle([0, 0, w * 0.4 * S, h * 7 / 13 * S], fill=(60, 59, 110))
    for yy in range(5):
        for xx in range(6):
            x, y = (xx + 0.5) * w * 0.4 / 6, (yy + 0.5) * h * 7 / 13 / 5
            d.ellipse([(x - 3) * S, (y - 3) * S, (x + 3) * S, (y + 3) * S], fill=WHITE)
    return down(lay)


def _wave(flag, t, amp=6):
    arr = flag.copy()
    out = Image.new("RGBA", (flag.width, flag.height + amp * 2 + 2), (0, 0, 0, 0))
    for x in range(0, flag.width, 4):
        dy = int(math.sin(t * 4 + x / 40) * amp * (x / flag.width))
        out.alpha_composite(arr.crop((x, 0, min(x + 4, flag.width), flag.height)), (x, amp + dy))
    return out


def flags(t, dur, crack_at=1.0, label="RELAÇÃO REBAIXADA", pair=("br", "ar")):
    img = base_night()
    mk = {"br": _flag_br, "ar": _flag_ar, "us": _flag_us}
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    for px in (170, 670):
        d.rectangle([(px - 8) * S, 360 * S, (px + 8) * S, 1250 * S], fill=(190, 194, 204))
        d.ellipse([(px - 18) * S, 340 * S, (px + 18) * S, 376 * S], fill=AMBER)
    # corda entre os mastros
    k = clamp((t - crack_at) / 0.5)
    y = 800
    if k <= 0:
        d.line([178 * S, y * S, 662 * S, y * S], fill=(220, 200, 150), width=8 * S)
    else:
        sag = 120 * ease_in(k)
        d.line([178 * S, y * S, (400 - 10 * k) * S, (y + sag) * S], fill=(220, 200, 150), width=8 * S)
        d.line([662 * S, y * S, (440 + 10 * k) * S, (y + sag) * S], fill=(220, 200, 150), width=8 * S)
    img.alpha_composite(down(lay))
    for px, key in ((170, pair[0]), (670, pair[1])):
        f = mk[key](300)
        paste_center(img, _wave(f, t), px + 150 + 4, 470)
    if label and k > 0:
        paste_center(img, stamp(label, 64), 420, 1010, scale=lerp(1.6, 1.0, back_out(clamp(k * 1.4))), rot=-5,
                     alpha=clamp(k * 3))
    return img


# ---------------------------------------------------------------- embaixada
def embassy(t, dur, flag="br", sign="EMBAIXADA DO BRASIL", lower_at=None, plaque="SEM EMBAIXADOR"):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 1240 * S, W * S, H * S], fill=(24, 26, 32))
    d.rectangle([80 * S, 560 * S, 760 * S, 1240 * S], fill=(70, 76, 90))
    d.polygon([(60 * S, 560 * S), (780 * S, 560 * S), (420 * S, 430 * S)], fill=(84, 90, 104))
    for i in range(5):
        x = 120 + i * 130
        d.rectangle([x * S, 640 * S, (x + 60) * S, 1180 * S], fill=(96, 102, 118))
    d.rectangle([60 * S, 1180 * S, 780 * S, 1240 * S], fill=(84, 90, 104))
    d.rounded_rectangle([150 * S, 590 * S, 690 * S, 640 * S], 8 * S, fill=(20, 22, 28))
    d.text((420 * S, 615 * S), sign, font=font("oswald", 34 * S, 700), fill=AMBER, anchor="mm")
    # mastro
    d.rectangle([892 * S, 300 * S, 904 * S, 1240 * S], fill=(190, 194, 204))
    img.alpha_composite(down(lay))
    fy = 360
    if lower_at is not None and t > lower_at:
        fy = lerp(360, 900, ease_io(clamp((t - lower_at) / 1.2)))
    f = {"br": _flag_br, "ar": _flag_ar}[flag](220)
    paste_center(img, _wave(f, t, 5), 898 - 110 - 6, fy + 80)
    if plaque and t > 0.6:
        kk = clamp((t - 0.6) / 0.35)
        st = stamp(plaque, 60, color=(255, 96, 86))
        bg = Image.new("RGBA", (st.width + 30, st.height + 30), (0, 0, 0, 0))
        ImageDraw.Draw(bg).rounded_rectangle([0, 0, bg.width - 1, bg.height - 1], 20, fill=(12, 13, 17, 235))
        bg.alpha_composite(st, (15, 15))
        paste_center(img, bg, 420, 900, scale=lerp(1.6, 1.0, back_out(kk)), rot=-5, alpha=clamp(kk * 3))
    return img


# ---------------------------------------------------------------- vitrine de importados (dólar caro)
def imports(t, dur, items=(("CELULAR", "phone"), ("VIAGEM", "plane"), ("VIDEOGAME", "game"))):
    img = base_night()
    lay = ss_layer(W, H)
    d = ImageDraw.Draw(lay)
    for row, y in enumerate((620, 1060)):
        d.rectangle([60 * S, y * S, 780 * S, (y + 24) * S], fill=(110, 80, 50))
    spots = [(230, 500), (590, 500), (410, 940)]
    for i, ((name, kind), (x, y)) in enumerate(zip(items, spots)):
        if kind == "phone":
            d.rounded_rectangle([(x - 60) * S, (y - 110) * S, (x + 60) * S, (y + 110) * S], 20 * S, fill=(14, 16, 22),
                                outline=(160, 166, 180), width=5 * S)
            d.rectangle([(x - 45) * S, (y - 85) * S, (x + 45) * S, (y + 85) * S], fill=(60, 110, 170))
        elif kind == "plane":
            d.rounded_rectangle([(x - 120) * S, (y - 60) * S, (x + 120) * S, (y + 60) * S], 12 * S, fill=PAPER)
            d.text((x * S, y * S), "PASSAGEM", font=font("anton", 40 * S), fill=INK, anchor="mm")
        else:
            d.rounded_rectangle([(x - 120) * S, (y - 50) * S, (x + 120) * S, (y + 50) * S], 40 * S, fill=(40, 44, 56))
            d.ellipse([(x - 90) * S, (y - 20) * S, (x - 50) * S, (y + 20) * S], fill=(200, 204, 214))
            d.ellipse([(x + 50) * S, (y - 20) * S, (x + 90) * S, (y + 20) * S], fill=RED)
        k = clamp((t - 0.3 - i * 0.45) / 0.3)
        tx, ty = x, y + 160
        d.rounded_rectangle([(tx - 110) * S, (ty - 40) * S, (tx + 110) * S, (ty + 40) * S], 10 * S, fill=AMBER)
        tag = "MAIS CARO" if k > 0.5 else "R$"
        d.text((tx * S, ty * S), tag, font=font("anton", 40 * S), fill=RED if k > 0.5 else INK, anchor="mm")
        d.text((x * S, (y - 150) * S), name, font=font("oswald", 34 * S, 700), fill=FOG, anchor="mm")
    img.alpha_composite(down(lay))
    return img


scenes.SCENES.update({"phone": phone, "spread": spread, "board_inv": board_inv, "exchange": exchange,
                      "vote_panel": vote_panel, "tariff": tariff, "flags": flags, "embassy": embassy,
                      "imports": imports})


# ---------------------------------------------------------------- ícones novos da capa
def icon_draw(name, ICON=260):
    U = 2
    lay = ss_layer(ICON, ICON)
    d = ImageDraw.Draw(lay)
    c = ICON * U / 2
    if name == "celular":
        d.rounded_rectangle([75 * U, 15 * U, 185 * U, 245 * U], 22 * U, fill=(14, 16, 22))
        d.rectangle([88 * U, 45 * U, 172 * U, 215 * U], fill=(60, 110, 170))
    elif name == "pix":
        d.rounded_rectangle([20 * U, 70 * U, 240 * U, 190 * U], 30 * U, fill=(30, 150, 120))
        d.text((c, c), "PIX", font=font("anton", 90 * U), fill=WHITE, anchor="mm")
    elif name == "cadeado":
        d.arc([70 * U, 20 * U, 190 * U, 150 * U], 180, 360, fill=(170, 176, 190), width=22 * U)
        d.rectangle([70 * U, 80 * U, 190 * U, 90 * U], fill=(170, 176, 190))
        d.rounded_rectangle([45 * U, 90 * U, 215 * U, 240 * U], 20 * U, fill=AMBER)
        d.ellipse([115 * U, 140 * U, 145 * U, 170 * U], fill=INK)
        d.rectangle([124 * U, 160 * U, 136 * U, 200 * U], fill=INK)
    elif name == "hacker":
        d.pieslice([50 * U, 20 * U, 210 * U, 200 * U], 180, 360, fill=(20, 22, 28))
        d.rectangle([50 * U, 110 * U, 210 * U, 200 * U], fill=(20, 22, 28))
        d.ellipse([85 * U, 60 * U, 175 * U, 160 * U], fill=(6, 6, 8))
        d.ellipse([100 * U, 100 * U, 118 * U, 112 * U], fill=RED)
        d.ellipse([142 * U, 100 * U, 160 * U, 112 * U], fill=RED)
        d.rounded_rectangle([30 * U, 195 * U, 230 * U, 245 * U], 10 * U, fill=(60, 66, 82))
    elif name == "qrcode":
        d.rectangle([30 * U, 30 * U, 230 * U, 230 * U], fill=WHITE)
        rng = random.Random(2)
        cell = 200 / 10
        for yy in range(10):
            for xx in range(10):
                corner = (xx < 3 and yy < 3) or (xx > 6 and yy < 3) or (xx < 3 and yy > 6)
                if (corner and (xx in (0, 2, 7, 9) or yy in (0, 2, 7, 9) or (xx % 7 == 1 and yy % 7 == 1))) or \
                        (not corner and rng.random() < 0.5):
                    d.rectangle([(30 + xx * cell) * U, (30 + yy * cell) * U, (30 + (xx + 1) * cell) * U,
                                 (30 + (yy + 1) * cell) * U], fill=INK)
    elif name == "carrinho":
        d.line([20 * U, 50 * U, 60 * U, 50 * U, 90 * U, 180 * U, 210 * U, 180 * U], fill=(200, 204, 214), width=14 * U,
               joint="curve")
        d.polygon([(70 * U, 80 * U), (235 * U, 80 * U), (210 * U, 160 * U), (88 * U, 160 * U)], fill=RED)
        for x in (105, 195):
            d.ellipse([(x - 20) * U, 195 * U, (x + 20) * U, 235 * U], fill=(200, 204, 214))
    elif name == "desconto":
        d.polygon([(20 * U, 130 * U), (90 * U, 40 * U), (240 * U, 40 * U), (240 * U, 220 * U), (90 * U, 220 * U)],
                  fill=AMBER)
        d.ellipse([50 * U, 115 * U, 80 * U, 145 * U], fill=INK)
        d.text((165 * U, c), "-90%", font=font("anton", 70 * U), fill=RED, anchor="mm")
    elif name == "acucar":
        im = _sugar_sack(1.0)
        lay2 = Image.new("RGBA", (ICON, ICON), (0, 0, 0, 0))
        lay2.alpha_composite(im, ((ICON - im.width) // 2, (ICON - im.height) // 2))
        return lay2
    elif name in ("bandeira_br", "bandeira_ar", "bandeira_us"):
        f = {"bandeira_br": _flag_br, "bandeira_ar": _flag_ar, "bandeira_us": _flag_us}[name](230)
        lay2 = Image.new("RGBA", (ICON, ICON), (0, 0, 0, 0))
        lay2.alpha_composite(f, ((ICON - f.width) // 2, (ICON - f.height) // 2))
        return lay2
    elif name == "dolar":
        d.ellipse([20 * U, 20 * U, 240 * U, 240 * U], fill=(70, 160, 90), outline=INK, width=10 * U)
        d.text((c, c + 6 * U), "US$", font=font("anton", 84 * U), fill=WHITE, anchor="mm")
    elif name == "seis":
        d.rounded_rectangle([15 * U, 60 * U, 245 * U, 200 * U], 16 * U, fill=(10, 11, 14))
        d.text((c, c), "R$ 6,00", font=font("anton", 70 * U), fill=(255, 90, 80), anchor="mm")
    elif name == "tarifa":
        d.rounded_rectangle([20 * U, 60 * U, 240 * U, 200 * U], 20 * U, fill=RED)
        d.text((c, c), "+10%", font=font("anton", 90 * U), fill=WHITE, anchor="mm")
    elif name == "embaixada":
        d.polygon([(30 * U, 100 * U), (230 * U, 100 * U), (130 * U, 40 * U)], fill=(150, 156, 170))
        for i in range(4):
            x = 50 + i * 48
            d.rectangle([x * U, 110 * U, (x + 26) * U, 210 * U], fill=(190, 194, 204))
        d.rectangle([25 * U, 210 * U, 235 * U, 235 * U], fill=(150, 156, 170))
    elif name == "aperto":
        d.rounded_rectangle([10 * U, 100 * U, 120 * U, 160 * U], 24 * U, fill=SKIN)
        d.rounded_rectangle([140 * U, 100 * U, 250 * U, 160 * U], 24 * U, fill=(170, 120, 90))
        d.line([128 * U, 70 * U, 120 * U, 130 * U, 136 * U, 190 * U], fill=RED, width=10 * U)
    elif name == "banco":
        d.polygon([(30 * U, 95 * U), (230 * U, 95 * U), (130 * U, 30 * U)], fill=(150, 156, 170))
        for i in range(4):
            x = 50 + i * 48
            d.rectangle([x * U, 105 * U, (x + 26) * U, 200 * U], fill=(190, 194, 204))
        d.rectangle([25 * U, 200 * U, 235 * U, 230 * U], fill=(150, 156, 170))
        d.text((c, 75 * U), "$", font=font("anton", 40 * U), fill=INK, anchor="mm")
    elif name == "votacao":
        d.rounded_rectangle([20 * U, 50 * U, 240 * U, 210 * U], 16 * U, fill=(10, 11, 14))
        d.text((80 * U, 100 * U), "SIM", font=font("anton", 40 * U), fill=(90, 230, 140), anchor="mm")
        d.text((180 * U, 100 * U), "NÃO", font=font("anton", 40 * U), fill=(255, 90, 80), anchor="mm")
        d.text((80 * U, 160 * U), "353", font=font("anton", 50 * U), fill=WHITE, anchor="mm")
        d.text((180 * U, 160 * U), "128", font=font("anton", 50 * U), fill=WHITE, anchor="mm")
    else:
        return None
    return down(lay)
