"""Mapa Natural Earth equiretangular com zoom, país em foco preenchido, estados em vermelho, pins com ondas."""
import math, os
from functools import lru_cache
import shapefile
from PIL import Image, ImageDraw
from core import *

LAT0 = 0.0


@lru_cache(None)
def _load(kind):
    r = shapefile.Reader(os.path.join(A, "ne", kind), encoding="utf-8")
    flds = [f[0] for f in r.fields[1:]]
    out = []
    for sr in r.iterShapeRecords():
        rec = dict(zip(flds, sr.record))
        sh = sr.shape
        parts = list(sh.parts) + [len(sh.points)]
        polys = [sh.points[parts[i]:parts[i + 1]] for i in range(len(parts) - 1)]
        out.append((rec, sh.bbox, polys))
    return out


def countries():
    return _load("countries")


def states():
    return _load("states")


def view_box(cx, cy, lon_span):
    """Caixa (lon0,lat0,lon1,lat1) vertical 9:16 centrada em (cx,cy) com correção cos(lat)."""
    k = math.cos(math.radians(cy))
    lat_span = lon_span * (H / W) * k
    return (cx - lon_span / 2, cy - lat_span / 2, cx + lon_span / 2, cy + lat_span / 2)


def draw_map(view, focus_iso=None, red_states=(), pins=(), t=0.0, labels=True, dots=(), dot_t0=0.0):
    lon0, lat0, lon1, lat1 = view
    sx = W / (lon1 - lon0)
    sy = H / (lat1 - lat0)

    def P(lon, lat):
        return ((lon - lon0) * sx, (lat1 - lat) * sy)

    img = Image.new("RGBA", (W, H), (18, 26, 38, 255))
    d = ImageDraw.Draw(img)
    # grade sutil
    for g in range(-180, 181, 10):
        x = (g - lon0) * sx
        if 0 <= x <= W:
            d.line([x, 0, x, H], fill=(24, 34, 48), width=2)
    for g in range(-90, 91, 10):
        y = (lat1 - g) * sy
        if 0 <= y <= H:
            d.line([0, y, W, y], fill=(24, 34, 48), width=2)
    for rec, bb, polys in countries():
        if bb[2] < lon0 - 5 or bb[0] > lon1 + 5 or bb[3] < lat0 - 5 or bb[1] > lat1 + 5:
            continue
        iso = rec.get("ADM0_A3") or rec.get("ISO_A3")
        fill = (78, 88, 104) if iso == focus_iso else (44, 52, 64)
        for poly in polys:
            if len(poly) < 3:
                continue
            d.polygon([P(*p) for p in poly], fill=fill, outline=(20, 26, 34))
    if focus_iso:
        for rec, bb, polys in states():
            if rec.get("adm0_a3") != focus_iso:
                continue
            name = rec.get("name")
            red = name in red_states
            for poly in polys:
                if len(poly) < 3:
                    continue
                d.polygon([P(*p) for p in poly], fill=RED if red else None, outline=(110, 120, 136) if not red else (255, 120, 120))
    # pontos (aeroportos) acendendo
    for i, (lon, lat) in enumerate(dots):
        x, y = P(lon, lat)
        k = clamp((t - dot_t0 - i * 0.05) / 0.2)
        if k <= 0:
            continue
        r = 9 + 4 * math.sin(t * 8 + i)
        d.ellipse([x - r, y - r, x + r, y + r], fill=RED, outline=WHITE, width=2)
    for i, pin in enumerate(pins):
        lon, lat, lab = pin[:3]
        side = pin[3] if len(pin) > 3 else (1 if P(lon, lat)[0] < W * 0.6 else -1)
        x, y = P(lon, lat)
        k = back_out(clamp((t - 0.6 - i * 0.35) / 0.35))
        if k <= 0:
            continue
        for w_ in range(3):
            ph = ((t * 0.9 + w_ / 3) % 1)
            rr = 20 + ph * 90
            d.ellipse([x - rr, y - rr * 0.45, x + rr, y + rr * 0.45], outline=(255, 90, 90, int(255 * (1 - ph))), width=4)
        hgt = 90 * k
        d.ellipse([x - 26 * k, y - hgt - 26 * k, x + 26 * k, y - hgt + 26 * k], fill=RED, outline=WHITE, width=4)
        d.polygon([(x - 18 * k, y - hgt + 14 * k), (x + 18 * k, y - hgt + 14 * k), (x, y)], fill=RED)
        d.ellipse([x - 9 * k, y - hgt - 9 * k, x + 9 * k, y - hgt + 9 * k], fill=WHITE)
        if labels and lab:
            f = font("oswald", 46, 700)
            tw = text_size(lab, f)[0]
            lx = x + 40 if side > 0 else x - tw - 70
            d.rectangle([lx, y - hgt - 34, lx + tw + 30, y - hgt + 34], fill=(8, 8, 10))
            d.text((lx + 15, y - hgt), lab, font=f, fill=WHITE, anchor="lm")
    img.alpha_composite(vignette_layer(0.5))
    return img


def zoom_map(t, dur, start, end, zt=1.3, **kw):
    """start/end = (lon,lat,lon_span). Zoom log-interpolado."""
    k = ease_io(t / zt)
    cx = lerp(start[0], end[0], k)
    cy = lerp(start[1], end[1], k)
    span = math.exp(lerp(math.log(start[2]), math.log(end[2]), k))
    return draw_map(view_box(cx, cy, span), t=t, **kw)
