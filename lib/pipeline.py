"""Comandos mecânicos da rotina diária.
  python3 lib/pipeline.py voice  DIR      -> voz.wav (Gemini Charon) + words.json + titulo.wav (mesma voz Gemini) + titulo_words.json
  python3 lib/pipeline.py render DIR      -> DIR/<out>.mp4, DIR/capa.jpg, DIR/folha.jpg
  python3 lib/pipeline.py publish DIR...  -> sobe os MP4 no branch media e agenda no Buffer (DIR/meta.json)
"""
import datetime as dt, importlib.util, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
REPO = os.environ.get("AF_REPO", "/home/claude/alemdofato-videos")
SLUG = os.environ.get("AF_SLUG", "alemdofatottk-ship-it/alemdofato-videos")
PIPER = os.path.join(ROOT, "assets", "piper", "pt_BR-faber-medium.onnx")


def sh(*a, **k):
    return subprocess.run(a, check=True, **k)


def voice(d):
    """Um único pedido ao Gemini (Charon) com título + roteiro; o trecho do título vira titulo.wav."""
    import align, tts
    script = open(os.path.join(d, "roteiro.txt")).read().strip()
    title = open(os.path.join(d, "titulo.txt")).read().strip()
    full = title + "\n\n" + script
    allwav = os.path.join(d, "voz_full.wav")
    model = os.environ.get("AF_TTS_MODEL")
    reuse = os.environ.get("AF_REUSE") and os.path.exists(allwav)  # voz já conferida à mão (números viram algarismos)
    for attempt in range(2):
        m = "reuso" if reuse else tts.tts(full, allwav, model)
        model = m  # mesma voz/modelo em todas as tentativas e em todo o lote
        words = align.transcribe(allwav)
        sim = align.similarity(full, words)
        print(f"modelo {m}  similaridade {sim:.3f}")
        if sim >= (0.85 if reuse else 0.9):
            break
    else:
        raise SystemExit("TTS reprovado duas vezes (similaridade < 0,9)")
    # fim do título: casa as palavras normalizadas do título com o começo da transcrição
    import difflib
    tn = align.norm(title)
    wn = [" ".join(align.norm(w["w"])) for w in words]
    flat, owner = [], []
    for k, w in enumerate(wn):
        for x in w.split():
            flat.append(x); owner.append(k)
    sm = difflib.SequenceMatcher(None, tn, flat[:len(tn) + 8], autojunk=False)
    last = max(b.b + b.size - 1 for b in sm.get_matching_blocks() if b.size) if any(b.size for b in sm.get_matching_blocks()) else len(tn) - 1
    k = owner[min(last, len(owner) - 1)]
    cut = (words[k]["e"] + words[k + 1]["s"]) / 2
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", allwav, "-t", f"{cut:.3f}", "-af", "afade=t=out:st=%.3f:d=0.05" % max(0, cut - 0.05),
       os.path.join(d, "titulo.wav"))
    sh("ffmpeg", "-y", "-loglevel", "error", "-ss", f"{cut:.3f}", "-i", allwav, os.path.join(d, "voz.wav"))
    tw = [w for w in words[:k + 1]]
    vw = [dict(w, s=round(w["s"] - cut, 3), e=round(w["e"] - cut, 3)) for w in words[k + 1:]]
    json.dump(vw, open(os.path.join(d, "words.json"), "w"), ensure_ascii=False)
    json.dump(tw, open(os.path.join(d, "titulo_words.json"), "w"), ensure_ascii=False)
    print("título falado:", " ".join(w["w"] for w in tw))
    print("voz:", " ".join(w["w"] for w in vw))


def load_spec(d):
    spec = importlib.util.spec_from_file_location("spec", os.path.join(d, "spec.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.SPEC


def render(d):
    import engine
    spec = load_spec(d)
    out = engine.run(spec, d)
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", out, "-vf", "fps=1/3.6,scale=216:384,tile=5x5", "-frames:v", "1",
       os.path.join(d, "folha.jpg"))
    sz = os.path.getsize(out) / 2 ** 20
    print(f"ok {out} {sz:.1f} MiB")
    shutil.rmtree(os.path.join(d, "beats"), ignore_errors=True)
    for f in ("video.mp4", "mix.wav"):
        if os.path.exists(os.path.join(d, f)):
            os.remove(os.path.join(d, f))


def publish(dirs):
    import post
    now = dt.datetime.now(dt.timezone.utc)
    git = ["git", "-C", REPO]
    subprocess.run(git + ["fetch", "--depth", "1", "origin", "media"], capture_output=True)
    keep = {}
    has = subprocess.run(git + ["rev-parse", "--verify", "origin/media"], capture_output=True).returncode == 0
    tmp = "/tmp/af_media"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    if has:  # mantém vídeos ainda não publicados (vencimento + 2 dias)
        sh(*(git + ["worktree", "add", "-f", "/tmp/af_old", "origin/media"]))
        for f in os.listdir("/tmp/af_old"):
            if f.endswith(".mp4"):
                try:
                    due = dt.datetime.strptime(f[:13], "%Y%m%d-%H%M").replace(tzinfo=dt.timezone.utc)
                except ValueError:
                    continue
                if due + dt.timedelta(days=2) > now:
                    shutil.copy(os.path.join("/tmp/af_old", f), tmp)
        sh(*(git + ["worktree", "remove", "--force", "/tmp/af_old"]))
    metas = []
    for d in dirs:
        meta = json.load(open(os.path.join(d, "meta.json")))
        fname = meta.get("file") or load_spec(d)["out"]
        due = dt.datetime.fromisoformat(meta["due_at"].replace("Z", "+00:00"))
        name = due.strftime("%Y%m%d-%H%M") + "_" + os.path.basename(fname)
        shutil.copy(os.path.join(d, fname), os.path.join(tmp, name))
        meta["url"] = f"https://raw.githubusercontent.com/{SLUG}/media/{name}"
        metas.append((d, meta))
    # commit órfão novo no branch media (histórico não acumula vídeos velhos)
    wt = "/tmp/af_wt"
    shutil.rmtree(wt, ignore_errors=True)
    sh(*(git + ["worktree", "prune"]))
    subprocess.run(git + ["branch", "-D", "media_new"], capture_output=True)
    sh(*(git + ["worktree", "add", "--orphan", "-B", "media_new", wt]))
    for f in os.listdir(tmp):
        shutil.copy(os.path.join(tmp, f), wt)
    sh("git", "-C", wt, "add", "-A")
    sh("git", "-C", wt, "-c", "user.name=Alem do Fato bot", "-c", "user.email=bot@alemdofato.local", "commit", "-q", "-m",
       "media " + now.strftime("%Y-%m-%d %H:%M"))
    sh("git", "-C", wt, "push", "-f", "origin", "media_new:media")
    sh(*(git + ["worktree", "remove", "--force", wt]))
    import time, urllib.request
    for d, meta in metas:
        for _ in range(10):
            try:
                urllib.request.urlopen(urllib.request.Request(meta["url"], method="HEAD"), timeout=30)
                break
            except Exception:
                time.sleep(6)
        res = post.schedule(meta)
        json.dump({"meta": meta, "buffer": res}, open(os.path.join(d, "agendado.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "voice":
        voice(sys.argv[2])
    elif cmd == "render":
        render(sys.argv[2])
    elif cmd == "publish":
        publish(sys.argv[2:])
