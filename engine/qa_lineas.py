"""Voice line gate: no line may reach the edit silent, cut mid-sound or missing words.
Review 2026-11-13: "at second 2 and 14 the audio cuts, at 35 again, look at the waveform so the voices are not cut; this happens
very often". The causes found: lines cut from a block take with output seeking came out silent (ep13 L05/L06), silenceremove at
-45 dB ate soft onsets and word tails, and eleven_v3 stopped mid-syllable at the end of its takes.
Checks, per line:
  1. not silent: mean level above -40 dB and at least 0.25 s of speech;
  2. clean edges: the file's first and last 30 ms (after the 10-20 ms fades) sit at least 15 dB under the line's speech level;
     a loud edge means the cut went through a sound;
  3. words: Whisper on the line alone matches the script at >= 0.80 (catches a clipped first or last word);
  4. length: at least 0.12 s per script word (a line that lost its tail is short).
Stages call it and stop on a failure (exit 1), so a broken line never reaches After Effects:
  python qa_lineas.py <project>            vo/L*.mp3 (after the voz stage, before anything is built on them)
  python qa_lineas.py <project> --audio    audio/L*.wav (after montaje: silenceremove, speed-up, lead-in)
Writes qa_lineas.json (or qa_lineas_audio.json)."""
import json, re, subprocess, sys
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

SR = 16000
NUMEROS = set("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen "
              "eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million billion dollars "
              "dollar percent th st nd rd".split())


def leer(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def db(x):
    return float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)) if len(x) else -99.0


def norm(t):
    return re.sub(r"[^a-z0-9 ]", " ", t.lower()).split()


def revisar(carpeta, audio=False):
    from comun import palabras
    pj = json.loads((carpeta / "proyecto.json").read_text(encoding="utf-8"))
    fallas, filas = [], []
    for ln in pj["lineas"]:
        f = carpeta / ("audio" if audio else "vo") / (f"{ln['id']}.wav" if audio else f"{ln['id']}.mp3")
        if not f.exists():
            continue   # a host line voiced by its own clip (Seedance) has no file here
        x = leer(f)
        r = {"id": ln["id"], "dur": round(len(x) / SR, 2), "problemas": []}
        habla = x[np.abs(x) > 0.02]
        nivel = db(habla)
        r["nivel"] = round(db(x), 1)
        if r["nivel"] < -40 or len(habla) < 0.25 * SR * 0.3:
            r["problemas"].append("silent")
        else:
            # after montaje the line was trimmed by silenceremove (it keeps 60-80 ms of air) and sped up 1.6x, so the kept air is
            # ~40 ms and a word onset can sit inside a 10-40 ms window (ep16 L02 at -32 vs -20 dB, not a cut: silenceremove only
            # removes sound under -55 dB). There the window is the first/last 2-12 ms and the margin 10 dB.
            e0, e1, margen = (int(0.002 * SR), int(0.012 * SR), 10) if audio else (int(0.01 * SR), int(0.04 * SR), 15)
            ini, fin = db(x[e0:e1]), db(x[-e1:-e0])
            r["bordes"] = [round(ini, 1), round(fin, 1), round(nivel, 1)]
            if ini > nivel - margen:
                r["problemas"].append(f"cut at start ({ini:.0f} dB vs speech {nivel:.0f})")
            if fin > nivel - margen:
                r["problemas"].append(f"cut at end ({fin:.0f} dB vs speech {nivel:.0f})")
            guion = norm(ln["texto"])
            if r["dur"] < 0.12 * len(guion):
                r["problemas"].append(f"too short for {len(guion)} words")
            oido = norm(" ".join(w for w, _, _ in palabras(f)))
            r["oido"] = " ".join(oido)
            # numbers are written in words in the script and in digits by Whisper ("two hundred thousand dollars" -> "$200,000"):
            # both sides drop numbers, number words and currency before comparing
            a = [w for w in guion if not w.isdigit() and w not in NUMEROS]
            b = [w for w in oido if not w.isdigit() and w not in NUMEROS]
            # compared letter by letter without spaces: Whisper writes "Stargate" for the script's "Star Gate" (ep18)
            r["parecido"] = round(SequenceMatcher(None, "".join(a), "".join(b), autojunk=False).ratio(), 2) if a else 1.0
            if r["parecido"] < 0.8:
                r["problemas"].append(f"words missing (match {r['parecido']})")
            # the edges of the line must be spoken: v3 skipped "His price?" at the start of ep13 L06 and the line still matched 0.88
            if len(a) >= 3 and len(b) >= 2:
                if not (set(a[:2]) & set(b[:4]) or "".join(a[:2]) in "".join(b[:4]) or a[0] in "".join(b[:3])):
                    r["problemas"].append(f"first words not heard ('{' '.join(a[:2])}')")
                if a[-1] not in "".join(b[-3:]):
                    r["problemas"].append(f"last word not heard ('{a[-1]}')")
        filas.append(r)
        if r["problemas"]:
            fallas.append(f"{ln['id']}: " + "; ".join(r["problemas"]))
    (carpeta / ("qa_lineas_audio.json" if audio else "qa_lineas.json")).write_text(
        json.dumps({"ok": not fallas, "fallas": fallas, "lineas": filas}, indent=1, ensure_ascii=False), encoding="utf-8")
    return fallas


if __name__ == "__main__":
    c = Path(sys.argv[1]).resolve()
    fl = revisar(c, "--audio" in sys.argv)
    for f in fl:
        print("FAIL", f)
    print("qa_lineas:", "ok" if not fl else f"{len(fl)} line(s) failed")
    sys.exit(1 if fl else 0)
