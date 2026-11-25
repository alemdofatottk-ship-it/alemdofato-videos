"""Gemini TTS (voz Charon), um pedido por roteiro inteiro. Uso: tts.py roteiro.txt saida.wav [modelo]"""
import base64, json, os, subprocess, sys, urllib.request, urllib.error, time

MODELS = ["gemini-2.5-pro-preview-tts", "gemini-2.5-flash-preview-tts"]
STYLE = ("Narre em português do Brasil, como um narrador de documentário investigativo: voz grave, "
         "séria e envolvente, ritmo ágil de vídeo curto, pausas curtas entre as frases. Texto:\n\n")


def tts(text, out_wav, model=None):
    key = os.environ.get("GEMINI_KEY")  # sem chave: o proxy injeta o segredo de rede
    models = [model] if model else MODELS
    last = None
    for m in models:
        body = {"contents": [{"parts": [{"text": STYLE + text}]}],
                "generationConfig": {"responseModalities": ["AUDIO"],
                                     "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Charon"}}}}}
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
            data=json.dumps(body).encode(),
            headers=dict({"Content-Type": "application/json"}, **({"x-goog-api-key": key} if key else {})))
        try:
            d = json.load(urllib.request.urlopen(req, timeout=600))
        except urllib.error.HTTPError as e:
            last = f"{m}: {e.code} {e.read()[:300]}"
            print(last, file=sys.stderr)
            continue
        part = d["candidates"][0]["content"]["parts"][0]["inlineData"]
        pcm = base64.b64decode(part["data"])
        raw = out_wav + ".pcm"
        open(raw, "wb").write(pcm)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", raw,
                        "-af", "loudnorm=I=-16:TP=-1.5", "-ar", "48000", out_wav], check=True)
        os.remove(raw)
        return m
    raise RuntimeError(last)


if __name__ == "__main__":
    t0 = time.time()
    m = tts(open(sys.argv[1]).read(), sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print("ok", m, round(time.time() - t0, 1), "s")
