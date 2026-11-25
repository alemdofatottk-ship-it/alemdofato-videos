"""Refaz o áudio de um curto pronto: nova narração (Gemini, do título ao fim) encaixada frase a frase
nos tempos da narração original, trilha e efeitos novos, e o final trocado pela animação de seguir.
Uso: revoice.py DIR   (DIR com orig.mp4, orig_words.json, roteiro.txt, voz.wav, words.json)"""
import json, os, re, subprocess, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import W, H, FPS, finish, red_cut
import beats, engine
from align import Words, norm

SR = 48000


def sentences(script):
    lines = script.strip().split("\n")
    title = lines[0].strip()
    body = " ".join(l.strip() for l in lines[1:])
    parts = re.split(r"(?<=[.?!])\s+", body)
    return title, [p for p in parts if p.strip()]


def key(s, n=4):
    return " ".join(s.split()[:n])


def stretch(x, tempo):
    if abs(tempo - 1) < 0.01:
        return x
    p = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-af", f"rubberband=tempo={tempo:.4f}", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-"],
                       input=x.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32)


def scene_cuts(video, thr=0.32):
    p = subprocess.run(["ffmpeg", "-i", video, "-vf", f"scale=270:480,select='gt(scene,{thr})',showinfo", "-f", "null",
                        "-"], capture_output=True, text=True)
    return [float(m) for m in re.findall(r"pts_time:([\d.]+)", p.stderr)]


def run(d, narr_start=None):
    orig = os.path.join(d, "orig.mp4")
    vdur = engine.dur_of(orig)
    title, sents = sentences(open(os.path.join(d, "roteiro.txt")).read())
    Wo = Words(json.load(open(os.path.join(d, "orig_words.json"))))
    Wn = Words(json.load(open(os.path.join(d, "words.json"))))
    nwords = Wn.words
    # início de cada frase no original e na voz nova
    from align import sentence_starts
    t_title_new, _ = Wn.find(key(title, 3), 0)
    title_words = len(norm(title))
    tw_end = Wn.words[min(len(Wn.words) - 1, Wn.find(key(title, 3), 0)[1] + title_words - 1)]["e"]
    o_st = sentence_starts(sents, Wo.words, t_min=1.2)
    n_st = sentence_starts(sents, Wn.words, t_min=tw_end - 0.05)
    if narr_start is not None:
        o_st[0] = narr_start
    narr0 = o_st[0]
    voice = engine.read_wav(os.path.join(d, "voz.wav"))

    def speech_end(t0, t1):
        ws = [w for w in nwords if t0 - 0.05 <= w["s"] < t1 - 0.02]
        return (ws[-1]["e"] + 0.06) if ws else t1

    total = vdur
    siga_i = max(i for i, s in enumerate(sents) if s.lower().startswith("siga"))
    siga_t = o_st[siga_i] - 0.1
    # duração da animação de seguir
    s_len = speech_end(n_st[siga_i], 1e9) - n_st[siga_i]
    total = max(vdur, siga_t + max(s_len + 1.3, 2.7))
    out = np.zeros(int(SR * (total + 1)), np.float32)
    report = []

    def place(seg, t):
        i = int(t * SR)
        m = min(len(seg), len(out) - i)
        out[i:i + m] += seg[:m]
        return t + m / SR

    # título: de 0,35 s até pouco antes da narração
    te = speech_end(t_title_new, n_st[0])
    seg = voice[int(max(0.0, t_title_new - 0.03) * SR):int(te * SR)]
    slot = narr0 - 0.3 - 0.35
    tempo = min(1.35, max(1.0, (len(seg) / SR) / slot))
    end = place(stretch(seg, tempo), 0.35)
    report.append(("TÍTULO", tempo))
    title_end = end
    cursor = end
    for i, s in enumerate(sents):
        ns = n_st[i]
        nxt = n_st[i + 1] if i + 1 < len(sents) else 1e9
        ne = speech_end(ns, nxt)
        seg = voice[int(max(0, ns - 0.03) * SR):int(ne * SR)]
        start = max(o_st[i], cursor + 0.06)
        slot_end = (o_st[i + 1] - 0.1) if i + 1 < len(sents) else total - 0.4
        L = len(seg) / SR
        S = max(0.3, slot_end - start)
        tempo = min(1.3, max(1.0, L / S))
        cursor = place(stretch(seg, tempo), start)
        report.append((s[:40], round(tempo, 2), round(start - o_st[i], 2)))
    # trilha e efeitos
    mix_len = len(out)
    fx = np.zeros(mix_len, np.float32)

    def add(x, t, g=1.0):
        i = int(t * SR)
        if 0 <= i < mix_len:
            m = min(len(x), mix_len - i)
            fx[i:i + m] += x[:m] * g

    add(engine.sfx_boom(), 0.0, 0.9)
    tout = narr0 - 0.8
    add(engine.sfx_riser(0.9), tout - 0.6, 0.6)
    add(engine.sfx_whoosh(0.6, 11), tout, 0.9)
    last = -9
    for k, c in enumerate(scene_cuts(orig)):
        if c > narr0 + 0.3 and c - last > 1.2 and c < siga_t - 0.3:
            add(engine.sfx_whoosh(0.4, k), c - 0.05, 0.55)
            last = c
    add(engine.sfx_whoosh(0.4, 99), siga_t, 0.6)
    mu = engine.music(total + 1)[:mix_len]
    env = np.convolve(np.abs(out), np.ones(int(0.15 * SR)) / int(0.15 * SR), mode="same")
    duck = np.where(env > 0.02, 0.45, 1.0).astype(np.float32)
    duck = np.convolve(duck, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    fade = np.clip((total + 0.3 - np.arange(mix_len) / SR) / 1.2, 0, 1)
    mix = out + fx * 0.6 + mu * duck * 0.55 * fade
    raw = os.path.join(d, "mix.f32")
    mix.astype(np.float32).tofile(raw)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", raw,
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", os.path.join(d, "mix.wav")],
                   check=True)
    os.remove(raw)
    # vídeo: original até o "Siga", depois a animação de seguir
    fol = os.path.join(d, "follow.mp4")
    n = int(round((total - siga_t) * FPS))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                          "-pix_fmt", "yuv420p", fol], stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS
        img = beats.render_follow({}, t)
        red_cut(img, t)
        p.stdin.write(finish(img).tobytes())
    p.stdin.close()
    p.wait()
    final = os.path.join(d, "final.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", orig, "-i", fol, "-i", os.path.join(d, "mix.wav"),
                    "-filter_complex",
                    f"[0:v]trim=0:{siga_t:.3f},setpts=PTS-STARTPTS,fps={FPS},format=yuv420p[a];"
                    f"[1:v]setpts=PTS-STARTPTS,format=yuv420p[b];[a][b]concat=n=2:v=1:a=0[v]",
                    "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-preset", "veryfast", "-b:v", "9000k",
                    "-maxrate", "9000k", "-bufsize", "18000k", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}",
                    "-movflags", "+faststart", final], check=True)
    for r in report:
        print("  ", r)
    print(f"{d}: original {vdur:.2f}s -> final {total:.2f}s  título até {title_end:.2f}s (narração {narr0:.2f}s)  siga {siga_t:.2f}s")
    return final


if __name__ == "__main__":
    run(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else None)
