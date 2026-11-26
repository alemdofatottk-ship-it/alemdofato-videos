"""Monta a linha do tempo de um curto a partir do spec, renderiza (2 processos) e mixa o áudio."""
import json, math, os, subprocess, sys, time, random
import numpy as np
from PIL import Image
from core import *
import beats, scenes, cover
from align import Words, norm

SR = 48000


def dur_of(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                          "csv=p=0", path]).decode())


# ------------------------------------------------------------------ timeline
# abertura curta (lições de 25/11: gancho falado já no 1º segundo)
PRE, GAP, OUTD = 0.12, 0.08, 0.55


def build(spec, d):
    words = json.load(open(os.path.join(d, "words.json")))
    Wd = Words(words)
    tw = json.load(open(os.path.join(d, "titulo_words.json")))
    tdur = dur_of(os.path.join(d, "titulo.wav"))
    voice_dur = dur_of(os.path.join(d, "voz.wav"))
    D0 = PRE + tdur + GAP + OUTD
    # destaques das linhas do título
    hl, i = [], 0
    for line in spec["title_lines_spoken"]:
        n = len(norm(line))
        seg = tw[i:i + n] or tw[-1:]
        hl.append((PRE + seg[0]["s"], PRE + seg[-1]["e"]))
        i += n
    bl = []
    prev, last = 0.0, -10.0
    for b in spec["beats"]:
        b = dict(b)
        found, _ = Wd.find(b["trigger"], prev)
        t = max(last + 1.2, found - 0.08) if bl else 0.0
        prev = found + 0.3
        last = t
        b["t0"] = t
        bl.append(b)
    end = voice_dur + 1.4
    for i, b in enumerate(bl):
        b["t1"] = bl[i + 1]["t0"] if i + 1 < len(bl) else end
    # resolve palavras da tela cinza e itens do dossiê
    group, slot = [], 0
    for b in bl:
        if b["type"] == "txt":
            toks = [(w, norm(w)[0] in [norm(h)[0] for h in b.get("hl", [])] if norm(w) else False) for w in b["text"].split()]
            b["_layout"] = beats.layout_txt(toks)
            cand = Wd.words_between(b["t0"] - 0.1, b["t1"])
            times, j = [], 0
            for w, _ in toks:
                nw = norm(w)
                hit = None
                for k in range(j, min(j + 6, len(cand))):
                    if nw and (norm(cand[k]["w"]) or [""])[0] == nw[0]:
                        hit = k
                        break
                if hit is not None:
                    times.append(cand[hit]["s"] - b["t0"])
                    j = hit + 1
                else:
                    times.append((times[-1] + 0.18) if times else 0.0)
            times[0] = min(times[0], 0.05)
            b["_wt"] = [max(0.0, x - 0.04) for x in times]
        if b["type"] == "dos":
            idx = bl.index(b)
            if b.get("fresh") or idx == 0 or bl[idx - 1]["type"] != "dos":
                items, slot = [], 0
            else:
                items = list(bl[idx - 1]["_items"])
            lastt = -9
            for it in b["items"]:
                ti, _ = Wd.find(it["at"], b["t0"] - 0.2)
                ti = max(ti, lastt + 0.9, b["t0"] + 0.1)
                lastt = ti
                if slot >= len(beats.SLOTS):
                    items = []
                    slot = 0
                kind, args = it["card"][0], it["card"][1:]
                img = {"fact": beats.card_fact, "num": beats.card_num, "doc": beats.card_doc,
                       "stamp": beats.card_stamp, "logo": beats.card_logo, "photo": beats.card_photo}[kind](*args)
                items.append({"t": ti, "img": img, "slot": slot, "rot": random.Random(ti).choice([-2, 2])})
                slot += 1
            b["_items"] = items
    # desloca tudo pela abertura
    for b in bl:
        b["t0"] += D0
        b["t1"] += D0
        if b["type"] == "dos":
            for it in b["_items"]:
                if not it.get("_shift"):
                    it["t"] += D0
                    it["_shift"] = True
    intro = {"type": "intro", "t0": 0.0, "t1": D0, "hl": hl, "tout": PRE + tdur + GAP}
    return [intro] + bl, D0, tdur, voice_dur


# ------------------------------------------------------------------ frames
NO_OVER = {"txt", "ppl", "poll", "follow", "intro"}


def frame(b, t, spec, cinfo):
    T = b["t0"] + t
    if b["type"] == "intro":
        img = cover.cover_frame(cinfo, t, out=max(0.0, t - b["tout"]))
    elif b["type"] == "dos":
        b.setdefault("title", spec["case_tag"])
        img = beats.render_dos(b, t, T)
    else:
        img = beats.RENDER[b["type"]](b, t)
    if b["type"] not in NO_OVER:
        tag(img, spec["case_tag"], t)
        caption(img, b.get("cap", ""), t)
    if b["type"] != "intro":
        red_cut(img, t)
    return finish(img)


def cover_info(spec):
    sc = spec["cover_bg"]
    bg = scenes.SCENES[sc[0]](sc[2] if len(sc) > 2 else 3.0, 3.0, **sc[1])
    return {"bg": bg, "title_lines": spec["title_lines"], "tag": spec["cover_tag"], "icons": spec["icons"]}


def render_beat(i, b, spec, cinfo, d):
    n0, n1 = round(b["t0"] * FPS), round(b["t1"] * FPS)
    out = os.path.join(d, "beats", f"b{i:03d}.mp4")
    if os.path.exists(out):
        return out
    part = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                          "-pix_fmt", "yuv420p", part], stdin=subprocess.PIPE)
    for n in range(n0, n1):
        img = frame(b, n / FPS - b["t0"], spec, cinfo)
        p.stdin.write(img.tobytes())
    p.stdin.close()
    p.wait()
    os.rename(part, out)
    return out


def render_all(bl, spec, d, workers=2):
    os.makedirs(os.path.join(d, "beats"), exist_ok=True)
    cinfo = cover_info(spec)
    cinfo["hl"] = bl[0]["hl"]
    pids = []
    for w in range(workers):
        pid = os.fork()
        if pid == 0:
            code = 0
            try:
                for i, b in enumerate(bl):
                    if i % workers == w:
                        render_beat(i, b, spec, cinfo, d)
            except Exception:
                import traceback
                traceback.print_exc()
                code = 1
            finally:
                os._exit(code)
        pids.append(pid)
    for pid in pids:
        _, st = os.waitpid(pid, 0)
        if st != 0:
            raise RuntimeError("falha no render de uma batida")
    lst = os.path.join(d, "beats", "list.txt")
    with open(lst, "w") as f:
        for i in range(len(bl)):
            f.write(f"file 'b{i:03d}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    os.path.join(d, "video.mp4")], check=True)
    # capa = 1º quadro
    cv = cover.cover_frame(dict(cinfo, hl=None), 0.0)
    finish(cv).save(os.path.join(d, "capa.jpg"), quality=92)


# ------------------------------------------------------------------ áudio
def read_wav(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def _noise(n, seed=0):
    return np.random.default_rng(seed).standard_normal(n).astype(np.float32)


def _lp(x, a):
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def sfx_whoosh(dur=0.45, seed=1):
    n = int(SR * dur)
    t = np.linspace(0, 1, n, dtype=np.float32)
    x = _noise(n, seed)
    # passa-banda varrendo (diferença de dois passa-baixas com corte variável aproximado)
    from scipy.signal import butter, sosfilt
    lo = sosfilt(butter(2, 3500, "low", fs=SR, output="sos"), x)
    hi = sosfilt(butter(2, 400, "high", fs=SR, output="sos"), lo)
    env = np.sin(np.pi * t) ** 2 * (0.4 + 0.6 * t)
    return (hi * env * 0.5).astype(np.float32)


def sfx_boom(dur=1.6):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = 52 * np.exp(-t * 1.2) + 30
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 2.6) * 0.9
    from scipy.signal import butter, sosfilt
    x += sosfilt(butter(2, 300, "low", fs=SR, output="sos"), _noise(n, 5)) * np.exp(-t * 14) * 0.8
    return x.astype(np.float32)


def sfx_riser(dur=1.4):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = 200 + 900 * (t / dur) ** 2
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15
    from scipy.signal import butter, sosfilt
    x += sosfilt(butter(2, [800, 6000], "band", fs=SR, output="sos"), _noise(n, 7)) * 0.35
    return (x * (t / dur) ** 2).astype(np.float32)


def sfx_type(dur, seed=3):
    n = int(SR * dur)
    x = np.zeros(n, np.float32)
    rng = np.random.default_rng(seed)
    t = 0.0
    from scipy.signal import butter, sosfilt
    click = sosfilt(butter(2, 1800, "high", fs=SR, output="sos"), _noise(int(SR * 0.025), 9)) * np.exp(
        -np.arange(int(SR * 0.025)) / SR * 220)
    while t < dur - 0.05:
        i = int(t * SR)
        x[i:i + len(click)] += click[: n - i] * rng.uniform(0.25, 0.45)
        t += rng.uniform(0.07, 0.14)
    return x


def sfx_pop():
    n = int(SR * 0.12)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (600 - 2500 * t) * t) * np.exp(-t * 40) * 0.35).astype(np.float32)


def music(total, seed=0):
    """Trilha sintetizada: pad menor + sub + pulso."""
    n = int(SR * total)
    t = np.arange(n) / SR
    chords = [(110, 130.81, 164.81), (87.31, 110, 130.81), (98, 123.47, 146.83), (82.41, 103.83, 123.47)]
    x = np.zeros(n, np.float32)
    seg = 4.0
    for ci in range(int(total / seg) + 1):
        a, b = int(ci * seg * SR), min(n, int((ci + 1) * seg * SR) + int(0.5 * SR))
        if a >= n:
            break
        tt = t[a:b] - ci * seg
        env = np.clip(tt / 0.8, 0, 1) * np.clip((seg + 0.5 - tt) / 0.8, 0, 1)
        for f in chords[ci % 4]:
            for det in (-0.6, 0.6):
                x[a:b] += (np.sin(2 * np.pi * (f + det) * tt) * 0.05 + np.sin(2 * np.pi * 2 * (f + det) * tt) * 0.015) * env
        x[a:b] += np.sin(2 * np.pi * chords[ci % 4][0] / 2 * tt) * 0.09 * env
    # pulso
    beat = 0.5
    for k in range(int(total / beat)):
        i = int(k * beat * SR)
        m = min(n - i, int(0.18 * SR))
        tt = np.arange(m) / SR
        x[i:i + m] += np.sin(2 * np.pi * (70 - 120 * tt) * tt) * np.exp(-tt * 22) * (0.22 if k % 2 == 0 else 0.1)
    return x


def mix(bl, d, D0, total):
    n = int(SR * (total + 0.5))
    voice = np.zeros(n, np.float32)
    v = read_wav(os.path.join(d, "voz.wav"))
    a = int(D0 * SR)
    voice[a:a + len(v)] += v[: n - a]
    tv = read_wav(os.path.join(d, "titulo.wav"))
    a = int(PRE * SR)
    voice[a:a + len(tv)] += tv[: n - a] * 0.95
    fx = np.zeros(n, np.float32)

    def add(x, t, g=1.0):
        i = int(t * SR)
        if i < 0 or i >= n:
            return
        m = min(len(x), n - i)
        fx[i:i + m] += x[:m] * g

    add(sfx_boom(), 0.0, 0.9)
    tout = bl[0]["tout"]
    add(sfx_riser(0.9), tout - 0.6, 0.6)
    add(sfx_whoosh(0.6, 11), tout, 0.9)
    for i, b in enumerate(bl[1:]):
        if b["type"] != "txt":
            add(sfx_whoosh(0.4, i), b["t0"] - 0.05, 0.7)
        if b["type"] == "type":
            add(sfx_type(b["t1"] - b["t0"] - 0.8), b["t0"] + 0.15, 0.9)
        if b["type"] == "dos":
            for it in b["_items"]:
                if b["t0"] <= it["t"] < b["t1"]:
                    add(sfx_pop(), it["t"], 0.8)
        if b.get("riser"):
            add(sfx_riser(), b["t0"] - 1.4, 0.7)
        if b.get("boom"):
            add(sfx_boom(), b["t0"], 0.6)
    mu = music(total + 0.5)[:n]
    # ducking pela envoltória da voz
    env = np.abs(voice)
    k = int(0.15 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    duck = np.where(env > 0.02, 0.45, 1.0).astype(np.float32)
    duck = np.convolve(duck, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    fade = np.clip((total + 0.3 - np.arange(n) / SR) / 1.2, 0, 1)
    out = voice + fx * 0.6 + mu * duck * 0.55 * fade
    raw = os.path.join(d, "mix.f32")
    out.astype(np.float32).tofile(raw)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", raw,
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", os.path.join(d, "mix.wav")],
                   check=True)
    os.remove(raw)


def final(d, total, name):
    out = os.path.join(d, name)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(d, "video.mp4"), "-i",
                    os.path.join(d, "mix.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast",
                    "-b:v", "9000k", "-maxrate", "9000k", "-bufsize", "18000k", "-c:a", "aac", "-b:a", "192k",
                    "-t", f"{total:.3f}", "-movflags", "+faststart", out], check=True)
    return out


def run(spec, d, only_test=False):
    bl, D0, tdur, vdur = build(spec, d)
    total = bl[-1]["t1"]
    print(f"abertura {D0:.2f}s  voz {vdur:.2f}s  total {total:.2f}s  batidas {len(bl)}")
    for b in bl:
        print(f"  {b['t0']:6.2f}-{b['t1']:6.2f} {b['type']:6s} {b.get('cap', b.get('text', ''))[:50]}")
    if only_test:
        return bl
    t0 = time.time()
    render_all(bl, spec, d)
    print("render", round(time.time() - t0), "s")
    mix(bl, d, D0, total)
    return final(d, total, spec["out"])
