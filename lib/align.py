"""Transcreve com faster-whisper (tempo por palavra) e compara com o roteiro."""
import difflib, json, re, subprocess, sys, unicodedata
import numpy as np

_model = None


def load_audio(path, sr=16000):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def transcribe(path):
    global _model
    from faster_whisper import WhisperModel
    if _model is None:
        _model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = _model.transcribe(load_audio(path), language="pt", word_timestamps=True, beam_size=5)
    words = []
    for s in segs:
        for w in s.words:
            words.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)})
    return words


def norm(t):
    t = t.lower().replace("%", " por cento ")
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", t)


def _spell(txt):
    """Algarismos da transcrição viram palavras (o roteiro usa números por extenso)."""
    try:
        from num2words import num2words
    except ImportError:
        return txt

    def rep(m):
        x = m.group(0).replace(".", "")
        try:
            if "," in x:
                a, b = x.split(",", 1)
                return num2words(int(a), lang="pt_BR") + " virgula " + num2words(int(b), lang="pt_BR")
            return num2words(int(x), lang="pt_BR")
        except Exception:
            return m.group(0)
    return re.sub(r"\d[\d.]*(,\d+)?", rep, txt)


def similarity(script, words):
    a = norm(script)
    b = norm(_spell(" ".join(w["w"] for w in words)))
    return difflib.SequenceMatcher(None, a, b).ratio()


class Words:
    def __init__(self, words):
        self.words = words
        self.toks = [(norm(w["w"]) or [""])[0] for w in words]

    def find(self, phrase, after=0.0):
        """Tempo de início da frase (match aproximado) depois de `after`."""
        p = norm(phrase)
        n = len(p)
        best, bt = 0, None
        for i, w in enumerate(self.words):
            if w["s"] < after:
                continue
            cand = self.toks[i:i + n]
            r = difflib.SequenceMatcher(None, p, cand).ratio()
            if r > best + 1e-9:
                best, bt = r, i
            if r == 1:
                break
        if bt is None or best < 0.6:
            raise KeyError(f"gatilho não encontrado: {phrase!r} depois de {after}")
        return self.words[bt]["s"], bt

    def span(self, phrase, after=0.0):
        s, i = self.find(phrase, after)
        n = len(norm(phrase))
        return s, self.words[min(i + n - 1, len(self.words) - 1)]["e"], i

    def words_between(self, t0, t1):
        return [w for w in self.words if w["s"] >= t0 - 0.05 and w["s"] < t1]


if __name__ == "__main__":
    words = transcribe(sys.argv[1])
    json.dump(words, open(sys.argv[2], "w"), ensure_ascii=False)
    if len(sys.argv) > 3:
        sc = open(sys.argv[3]).read()
        print("similaridade", round(similarity(sc, words), 3))
    print(" ".join(w["w"] for w in words))


def sentence_starts(sents, words, t_min=0.0):
    """Início (s) de cada frase no áudio transcrito, por alinhamento global de tokens.
    Robusto a números por extenso x algarismos: ancora no último token casado antes da frase."""
    stoks, sidx = [], []
    for k, s in enumerate(sents):
        for t in norm(s):
            stoks.append(t)
            sidx.append(k)
    ttoks, towner = [], []
    for i, w in enumerate(words):
        if w["s"] < t_min:
            continue
        for t in norm(w["w"]):
            ttoks.append(t)
            towner.append(i)
    sm = difflib.SequenceMatcher(None, stoks, ttoks, autojunk=False)
    m = {}
    for a, b, n in sm.get_matching_blocks():
        for j in range(n):
            m[a + j] = b + j
    first = {}
    for i, k in enumerate(sidx):
        first.setdefault(k, i)
    out = []
    for k in range(len(sents)):
        si = first[k]
        if si in m:
            out.append(words[towner[m[si]]]["s"])
            continue
        prev = max((j for j in m if j < si), default=None)
        if prev is not None:
            wi = towner[m[prev]] + 1
            # pula palavras que ainda pertencem à mesma palavra transcrita
            out.append(words[min(wi, len(words) - 1)]["s"])
        else:
            ws = [w for w in words if w["s"] >= t_min]
            out.append(ws[0]["s"] if ws else 0.0)
    return out
