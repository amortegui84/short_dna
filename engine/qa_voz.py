"""Storyteller voice QA (review 2026-11-12: "the way the voice tells it is very flat; it should sound like a storyteller").
For each voice file measures, with numpy only:
  - pitch movement: standard deviation of F0 in semitones over voiced frames (autocorrelation tracker, 60-400 Hz);
    flat narration sits under ~2 st, an expressive storyteller around 3-5 st;
  - loudness movement: standard deviation of short-term RMS in dB over voiced frames (whispers and rises widen it);
  - pauses: count of silences >= 0.35 s inside the line;
  - speed: words per minute when the text is given (python qa_voz.py --texto "..." file).
  python qa_voz.py <file.wav|mp3> [...]            print the measures
  python qa_voz.py --proyecto <project>           every vo/L*.mp3 of a project, with the script's words, + qa_voz.json
Thresholds for a pass: pitch >= 2.5 st on average across the lines, no line under 1.8 st."""
import json, subprocess, sys
from pathlib import Path

import numpy as np

SR = 16000


def leer(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def medir(p, texto=None):
    x = leer(p)
    hop, win = 160, 640
    f0, rms = [], []
    for i in range(0, len(x) - win, hop):
        fr = x[i:i + win] * np.hanning(win)
        e = float(np.sqrt(np.mean(fr ** 2)) + 1e-9)
        rms.append(e)
        if e < 0.01:
            f0.append(0.0); continue
        ac = np.correlate(fr, fr, "full")[win - 1:]
        lo, hi = SR // 400, SR // 60
        k = lo + int(np.argmax(ac[lo:hi]))
        f0.append(SR / k if ac[k] > 0.3 * ac[0] else 0.0)
    f0, rms = np.array(f0), np.array(rms)
    voz = f0 > 0
    st = 12 * np.log2(f0[voz] / np.median(f0[voz])) if voz.sum() > 20 else np.array([0.0])
    st = st[np.abs(st) < 12]   # octave errors out
    db = 20 * np.log10(rms[rms > 0.01]) if (rms > 0.01).sum() > 10 else np.array([0.0])
    silencio = rms < 0.008
    pausas, run = 0, 0
    for s in silencio:
        run = run + 1 if s else 0
        if run == int(0.35 * SR / hop):
            pausas += 1
    dur = len(x) / SR
    r = {"archivo": Path(p).name, "dur_s": round(dur, 2), "tono_st": round(float(np.std(st)), 2), "volumen_db": round(float(np.std(db)), 2), "pausas": pausas}
    if texto:
        r["wpm"] = round(len(texto.split()) / dur * 60)
    return r


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--proyecto":
        carpeta = Path(args[1]).resolve()
        pj = json.loads((carpeta / "proyecto.json").read_text(encoding="utf-8"))
        res = [medir(carpeta / "vo" / f"{l['id']}.mp3", l["texto"]) for l in pj["lineas"] if (carpeta / "vo" / f"{l['id']}.mp3").exists()]
        tono = [r["tono_st"] for r in res]
        ok = bool(res) and np.mean(tono) >= 2.5 and min(tono) >= 1.8
        out = {"ok": ok, "tono_medio_st": round(float(np.mean(tono)), 2) if res else 0, "lineas": res}
        (carpeta / "qa_voz.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(json.dumps(out, indent=1)); sys.exit(0 if ok else 1)
    texto = None
    if args and args[0] == "--texto":
        texto, args = args[1], args[2:]
    for p in args:
        print(json.dumps(medir(p, texto)))
