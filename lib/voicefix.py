"""Pós-processamento da voz Gemini (voz_full.wav = título + roteiro num único pedido, mesma voz).
- Corta o título na primeira pausa (>= 0,3 s) depois de 0,6 s (robusto a número/algarismo e a título que o
  whisper não transcreve).
- Encurta pausas longas da narração (> 0,45 s viram ~0,3 s), sem mexer na velocidade da voz.
- Transcreve a narração (words.json) e confere com o roteiro; tempos do título são distribuídos nas palavras.
Uso: python3 lib/voicefix.py DIR"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import align


def silences(path, db=-40, dmin=0.3):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=n={db}dB:d={dmin}", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    return list(zip(st, en))


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)


def run(d, max_pause=0.45, keep=0.3):
    full = os.path.join(d, "voz_full.wav")
    title = open(os.path.join(d, "titulo.txt")).read().strip()
    script = open(os.path.join(d, "roteiro.txt")).read().strip()
    sil = silences(full)
    lead = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    gap = next((s for s in sil if s[0] > lead + 0.6), None)
    if gap is None:
        raise SystemExit("não achei a pausa depois do título")
    cut0, cut1 = gap[0] + 0.06, gap[1] - 0.06
    tw = os.path.join(d, "titulo.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(0, lead - 0.03):.3f}", "-to", f"{cut0:.3f}", "-i", full,
                    "-af", "afade=t=out:st=%.3f:d=0.05" % max(0, cut0 - lead - 0.05), tw], check=True)
    raw = os.path.join(d, "voz_raw.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{cut1:.3f}", "-i", full, raw], check=True)
    # encurta pausas longas da narração
    body = silences(raw, dmin=max_pause)
    parts, t = [], 0.0
    for s, e in body:
        if s < 0.05:
            continue
        mid_keep = keep
        parts.append((t, s + mid_keep / 2))
        t = e - mid_keep / 2
    parts.append((t, dur(raw) + 1))
    flt = "".join(f"[0]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[p{i}];" for i, (a, b) in enumerate(parts))
    flt += "".join(f"[p{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[o]"
    vz = os.path.join(d, "voz.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-filter_complex", flt, "-map", "[o]", vz], check=True)
    os.remove(raw)
    words = align.transcribe(vz)
    sim = align.similarity(script, words)
    json.dump(words, open(os.path.join(d, "words.json"), "w"), ensure_ascii=False)
    # título: palavras do texto distribuídas na duração falada
    td = dur(tw)
    toks = title.split()
    n = sum(len(align.norm(x)) for x in toks) or 1
    out, t0, k = [], 0.02, 0
    span = max(0.3, td - 0.1)
    for x in toks:
        m = len(align.norm(x))
        for j in range(m):
            out.append({"w": x, "s": round(t0 + span * k / n, 3), "e": round(t0 + span * (k + 1) / n, 3)})
            k += 1
    json.dump(out, open(os.path.join(d, "titulo_words.json"), "w"), ensure_ascii=False)
    print(f"{d}: título {td:.2f}s  narração {dur(vz):.2f}s (antes {dur(full) - cut1:.2f}s)  similaridade {sim:.3f}")
    print("narração:", " ".join(w["w"] for w in words))
    if sim < 0.9:
        print("ATENÇÃO: similaridade < 0,9")
    return sim


if __name__ == "__main__":
    for d in sys.argv[1:]:
        run(d)
