"""Comandos mecânicos da rotina diária.
  python3 lib/pipeline.py voice  DIR      -> voz.wav (Gemini Charon) + words.json + titulo.wav (Piper) + titulo_words.json
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
    import align, tts
    script = open(os.path.join(d, "roteiro.txt")).read()
    model = os.environ.get("AF_TTS_MODEL")
    for attempt in range(2):
        m = tts.tts(script, os.path.join(d, "voz.wav"), model)
        model = m  # mesma voz/modelo em todas as tentativas e em todo o lote
        words = align.transcribe(os.path.join(d, "voz.wav"))
        sim = align.similarity(script, words)
        print(f"modelo {m}  similaridade {sim:.3f}")
        if sim >= 0.9:
            break
    else:
        raise SystemExit("TTS reprovado duas vezes (similaridade < 0,9)")
    json.dump(words, open(os.path.join(d, "words.json"), "w"), ensure_ascii=False)
    title = open(os.path.join(d, "titulo.txt")).read().strip()
    raw = os.path.join(d, "titulo_raw.wav")
    subprocess.run([sys.executable, "-m", "piper", "-m", PIPER, "--length-scale", "1.1", "-f", raw], input=title.encode(),
                   check=True, capture_output=True)
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
       "rubberband=pitch=0.93,equalizer=f=120:t=q:w=1:g=4,acompressor=threshold=-18dB:ratio=3,"
       "aecho=0.8:0.5:40:0.18,loudnorm=I=-15:TP=-1.5", "-ar", "48000", os.path.join(d, "titulo.wav"))
    tw = align.transcribe(os.path.join(d, "titulo.wav"))
    json.dump(tw, open(os.path.join(d, "titulo_words.json"), "w"), ensure_ascii=False)
    print("título falado:", " ".join(w["w"] for w in tw))
    print("voz:", " ".join(w["w"] for w in words))


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
