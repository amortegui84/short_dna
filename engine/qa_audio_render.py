"""Listens to the RENDERED video, line by line, and fails when any voice line is cut or missing in the final mix.
Review 2026-11-14 (ep13 D.B. Cooper, 1:08): "what he left behind" lost "behind". The line files and the edit passed every gate;
After Effects had kept the duration of the previous, shorter L11.wav (same path, same session) and ended the layer early.
Only a check on the final file catches that, so this compares the render with what should be in it:

  1. waveform: each voice wav (datos_ae.json "voces") is located in the render by envelope cross-correlation (+-0.8 s), then
     every 10 ms frame where the wav is speaking must also be loud in the render (same gain as the rest of the line). A run of
     >= 0.10 s where the render falls 12 dB below the wav is a cut; the words under it are named from timeline.json.
  2. transcript: Whisper on the render; every word Whisper heard in the line's own file (qa_lineas_audio.json, else the script)
     must be heard inside that line's window in the render (fuzzy match, numbers ignored). A missing LAST word, or two, fails.

  python qa_audio_render.py <project> [video.mp4]     writes qa_audio_render.json, exit 1 on a failure
"""
import difflib, json, re, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from comun import palabras, pcm16k, proyecto, ultimo_render  # noqa: E402

HOP = 160          # 10 ms at 16 kHz
CAIDA_DB = 12      # render this far under the wav (after gain) = voice missing
MIN_RUN = 0.10     # seconds
NUMEROS = set("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen "
              "eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million".split())


def env_db(x):
    n = len(x) // HOP
    if n == 0:
        return np.zeros(0)
    fr = x[:n * HOP].reshape(n, HOP)
    return 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower().replace("-", ""))


def ubicar(w_db, f_db, s0, busca=80):
    """Lag (frames) of the wav inside the render around frame s0, by correlation of the speech envelopes."""
    w = np.clip(w_db + 60, 0, None)
    best, lag = -1, 0
    for d in range(-busca, busca + 1):
        a = s0 + d
        if a < 0 or a + len(w) > len(f_db):
            continue
        f = np.clip(f_db[a:a + len(w)] + 60, 0, None)
        c = float(np.dot(w - w.mean(), f - f.mean()) / (np.linalg.norm(w - w.mean()) * np.linalg.norm(f - f.mean()) + 1e-9))
        if c > best:
            best, lag = c, d
    return lag, best


def revisar(carpeta, video=None):
    carpeta = Path(carpeta)
    pj = proyecto(carpeta)
    video = Path(video) if video else ultimo_render(carpeta, pj["slug"])
    datos = json.loads((carpeta / "datos_ae.json").read_text(encoding="utf-8"))
    tl = {s["id"]: s for s in json.loads((carpeta / "timeline.json").read_text(encoding="utf-8"))["segmentos"]}
    textos = {l["id"]: l["texto"] for l in pj["lineas"]}
    # baseline = what Whisper heard in each line's own file (qa_lineas audio mode): a word Whisper mishears in the wav too
    # ("Just after takeoff" heard "Just have to take off") is not a loss in the render
    qa = carpeta / "qa_lineas_audio.json"
    if qa.exists():
        for l in json.loads(qa.read_text(encoding="utf-8")).get("lineas", []):
            if l.get("oido"):
                textos[l["id"]] = re.sub(r"\b(\w+) (s|t|re|ll|ve|d|m)\b", r"\1\2", l["oido"])   # "it s" -> "its"
    f_db = env_db(pcm16k(video))
    oidas = palabras(video)
    lineas, fallas = [], []
    voces = datos.get("voces")
    if voces is None:   # news/reaction format: one voice track; its lines are vo/_lineas/Lxx.wav placed at tiempos_reaccion
        tr = json.loads((carpeta / "vo" / "tiempos_reaccion.json").read_text(encoding="utf-8"))["ini"]
        voces = [{"id": k, "wav": str(carpeta / "vo" / "_lineas" / f"{k}.wav"), "start": s} for k, s in tr.items()
                 if (carpeta / "vo" / "_lineas" / f"{k}.wav").exists()]
        for v in voces:     # timeline word times are on the pre-tightening clock: shift them to the line's real start
            seg = tl.get(v["id"])
            if seg and seg.get("words"):
                d = v["start"] - seg.get("start", 0)
                tl[v["id"]] = {**seg, "start": v["start"], "words": [{**w, "s": w["s"] + d, "e": w["e"] + d} for w in seg["words"]]}
    mudos = {l["id"] for l in pj["lineas"] if l.get("mudo")}   # a silent beat (a grimace) has no voice to find
    for v in [v for v in voces if v["id"] not in mudos]:
        lid, ini = v["id"], v["start"]
        w_db = env_db(pcm16k(v["wav"]))
        lag, corr = ubicar(w_db, f_db, int(round(ini * 100)))
        a = int(round(ini * 100)) + lag
        f = f_db[a:a + len(w_db)]
        if len(f) < len(w_db):                                  # the render ends before the line does
            f = np.concatenate([f, np.full(len(w_db) - len(f), -120.0)])
        habla = w_db > max(w_db.max() - 25, -40)
        gan = float(np.median((f - w_db)[habla])) if habla.any() else 0.0
        falta = habla & (f < w_db + gan - CAIDA_DB)
        cortes, i = [], 0
        while i < len(falta):
            if falta[i]:
                j = i
                while j + 1 < len(falta) and (falta[j + 1] or (j + 3 < len(falta) and falta[j + 2:j + 4].any())):
                    j += 1
                if (j - i + 1) / 100 >= MIN_RUN:
                    cortes.append([i / 100, (j + 1) / 100])
                i = j + 1
            else:
                i += 1
        # end of the line: the last 0.4 s of speech, on average, must not sink (an early layer end is often patchy under music)
        cola_db = 0.0
        hi = np.where(habla)[0]
        if len(hi):
            ult = hi[hi >= hi[-1] - 40]
            cola_db = float(np.mean((w_db[ult] + gan) - f[ult]))
            if cola_db >= 7 and not any(c1 >= (hi[-1] - 40) / 100 for _, c1 in cortes):
                cortes.append([ult[0] / 100, (ult[-1] + 1) / 100])
        # name the words under each cut (timeline word times are absolute on the timeline; shift to the wav's own clock)
        seg = tl.get(lid, {})
        t0 = seg.get("start", 0)
        nombres = []
        for c0, c1 in cortes:
            ws = [w["w"] for w in seg.get("words", []) if (w["s"] - t0) < c1 and (w["e"] - t0) > c0 + 0.03]
            nombres.append(" ".join(ws))
        # transcript inside the line's window in the render
        r0, r1 = a / 100 - 0.4, (a + len(w_db)) / 100 + 0.6
        oido = [norm(w) for w, s, e in oidas if s < r1 and e > r0]
        guion = [norm(w) for w in textos.get(lid, "").split()]
        guion = [w for w in guion if w and w not in NUMEROS and not any(ch.isdigit() for ch in w)]
        junto = "".join(oido)
        def oye(w):
            if len(w) > 2 and w in junto:          # "p m" / "u s" written apart, or two words heard as one
                return True
            return any(w == o or (len(w) > 3 and difflib.SequenceMatcher(None, w, o).ratio() >= 0.75) or (len(w) > 4 and w in o)
                       for o in oido)
        faltan = [w for w in guion if not oye(w)]
        ultima = bool(guion) and not oye(guion[-1])
        problemas = []
        if cortes:
            problemas += [f"voice missing {round(ini + lag / 100 + c0, 2)}-{round(ini + lag / 100 + c1, 2)} s"
                          + (f" ({n})" if n else "") for (c0, c1), n in zip(cortes, nombres)]
        # Whisper alone misreads names and spellings ("Arecibo", "U.S. called" heard as "cold"): a transcript miss fails only when
        # the waveform agrees (a cut, or the line's end sinking >= 4 dB); otherwise it is a warning to listen to
        avisos = []
        if ultima:
            (problemas if (cortes or cola_db >= 4) else avisos).append(f"last word not heard: {guion[-1]}")
        if len(faltan) >= 2:
            (problemas if cortes else avisos).append("words not heard: " + " ".join(faltan))
        if corr < 0.3:
            problemas.append(f"line not found in the render (corr {corr:.2f})")
        r = {"id": lid, "en_render": round(ini + lag / 100, 2), "desfase": round(lag / 100, 2), "corr": round(corr, 2),
             "ganancia_db": round(gan, 1), "cola_db": round(cola_db, 1), "cortes": cortes, "faltan": faltan, "problemas": problemas, "avisos": avisos}
        lineas.append(r)
        if problemas:
            fallas.append({"id": lid, "problemas": problemas})
    out = {"video": video.name, "ok": not fallas, "fallas": fallas, "lineas": lineas}
    (carpeta / "qa_audio_render.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return out


if __name__ == "__main__":
    r = revisar(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    for l in r["lineas"]:
        if l["avisos"]:
            print(l["id"], "| warning:", "; ".join(l["avisos"]))
    for f in r["fallas"]:
        print(f["id"], "|", "; ".join(f["problemas"]))
    print("audio render", "OK" if r["ok"] else "FAILED", "-", r["video"])
    sys.exit(0 if r["ok"] else 1)
