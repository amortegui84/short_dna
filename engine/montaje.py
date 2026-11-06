"""Linea de tiempo del Short (sin render de video: el video lo arma After Effects con build_ae.py).
VOZ UNICA: todo el audio de voz es la VO de ElevenLabs. En las lineas A (avatar) la frase de ElevenLabs se ajusta con atempo
a la ventana en la que H3 mueve los labios, asi no hay salto de timbre ni de entonacion entre avatar y voz en off.
- A: ventana = primera a ultima palabra que Whisper oye en el clip H3; subtitulos con esos tiempos (labios).
- B: VO con silenceremove + atempo 1.08 (v3 deja pausas largas); subtitulos con Whisper sobre el audio final.
Escribe timeline.json y audio/<id>.wav (normalizado a -20 LUFS). Uso: python montaje.py <carpeta>"""
import json, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from comun import duracion, palabras, personaje, proyecto, run  # noqa: E402

GAP = 0.12
NIVELES = [1.0, 1.32, 1.12, 1.45]   # encuadres del avatar en cada salto de zoom
SIL = "silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.3:stop_threshold=-45dB"
# conservar_pausas (narradores dramaticos): solo se recortan el silencio del principio y del final; las pausas y silencios quedan
SIL_BORDES = ("silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.9:stop_silence=0.9:stop_threshold=-45dB,"   # pausas de hasta 0.9 s
              "areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse")


def tiempos_guion(texto, oidas, ini, fin, sustituir):
    """Palabras del guion (lo que se lee) con tiempos: los de Whisper si coinciden en numero; si no, repartidos."""
    guion = [sustituir.get(g, g) for g in texto.replace("...", " ").split()]
    if len(oidas) == len(guion):
        return [(g, a, b) for g, (_, a, b) in zip(guion, oidas)]
    pesos = np.array([len(g) + 2 for g in guion], float)
    bordes = ini + np.concatenate([[0], np.cumsum(pesos)]) / pesos.sum() * (fin - ini)
    return [(g, float(bordes[i]), float(bordes[i + 1])) for i, g in enumerate(guion)]


def main(carpeta):
    pj = proyecto(carpeta)
    sus = pj.get("sustituir", {})
    aud = carpeta / "audio"
    aud.mkdir(exist_ok=True)
    segs = []
    sin_boca = bool(pj.get("personaje") and personaje(pj).get("sin_boca"))
    filtro = SIL_BORDES if pj.get("conservar_pausas") else SIL
    for ln in pj["lineas"]:
        lid, vo = ln["id"], carpeta / "vo" / f"{ln['id']}.mp3"
        limpia = aud / f"{lid}_limpia.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(vo), "-af", filtro, "-ac", "2", "-ar", "48000", str(limpia)])
        wav = aud / f"{lid}.wav"
        if ln["tipo"] == "A" and sin_boca:
            # personaje sin boca: no hay labios que cuadrar; la linea dura lo que dura la voz (con sus pausas) y el clip arranca con ella
            clip = carpeta / "clips" / f"{lid}.mp4"
            run(["ffmpeg", "-y", "-v", "error", "-i", str(limpia), "-af", "apad=pad_dur=0.2,loudnorm=I=-20:TP=-2:LRA=9", "-ar", "48000", str(wav)])
            ws = palabras(wav)
            pal = tiempos_guion(ln["texto"], ws, ws[0][1], ws[-1][2], sus)
            segs.append({"id": lid, "tipo": "A", "clip": str(clip), "t0": 0.0, "dur": duracion(wav), "pal": pal, "wav": str(wav), "atempo": "voz"})
            continue
        if ln["tipo"] == "A":
            clip = carpeta / "clips" / f"{lid}.mp4"
            ws = palabras(clip)
            t0, t1 = max(0.0, ws[0][1] - 0.12), ws[-1][2] + 0.18
            ventana = t1 - t0
            sts = aud / f"{lid}_sts.mp3"
            if sts.exists():
                # el habla de H3 (labios perfectos) con el timbre de la voz del video (sts.py): mismo ritmo, mismas pausas
                run(["ffmpeg", "-y", "-v", "error", "-i", str(sts), "-af",
                     f"apad=whole_dur={ventana:.3f},atrim=0:{ventana:.3f},loudnorm=I=-20:TP=-2:LRA=7", "-ac", "2", "-ar", "48000", str(wav)])
                f = "sts"
            else:
                # sin STS: la VO cabe en la ventana de los labios con atempo (0.8-1.25); el lipsync queda aproximado
                f = min(1.25, max(0.8, duracion(limpia) / (ventana - 0.1)))
                run(["ffmpeg", "-y", "-v", "error", "-i", str(limpia), "-af",
                     f"atempo={f:.4f},adelay=60|60,apad=whole_dur={ventana:.3f},atrim=0:{ventana:.3f},loudnorm=I=-20:TP=-2:LRA=7",
                     "-ar", "48000", str(wav)])
            pal = [(p, a - t0, b - t0) for p, a, b in tiempos_guion(ln["texto"], ws, ws[0][1], ws[-1][2], sus)]
            segs.append({"id": lid, "tipo": "A", "clip": str(clip), "t0": t0, "dur": ventana, "pal": pal, "wav": str(wav),
                         "atempo": f if f == "sts" else round(f, 3)})
        else:
            # la voz en off va a 1.08; las cabezas flotantes piden mas ritmo (sin labios en estas lineas, se puede acelerar)
            ritmo_b = pj.get("ritmo_b") or (1.2 if pj.get("cabeza") else 1.08)   # proyecto.json "ritmo_b" manda (avatar v10b: 1.05, para ver las obras)
            run(["ffmpeg", "-y", "-v", "error", "-i", str(limpia), "-af", f"atempo={ritmo_b},apad=pad_dur=0.15,loudnorm=I=-20:TP=-2:LRA=7",
                 "-ar", "48000", str(wav)])
            ws = palabras(wav)
            pal = tiempos_guion(ln["texto"], ws, ws[0][1], ws[-1][2], sus)
            segs.append({"id": lid, "tipo": "B", "dur": duracion(wav), "pal": pal, "wav": str(wav), "obras": ln.get("obras", [])})

    linea, t = [], 0.0
    for s in segs:
        d = {k: v for k, v in s.items() if k != "pal"}
        d.update(start=round(t, 3), dur=round(s["dur"], 3),
                 words=[{"w": p, "s": round(t + a, 3), "e": round(t + b, 3)} for p, a, b in s["pal"]])
        if s["tipo"] == "A":
            cortes, ult = [0.0], 0.0
            for p, a, b in s["pal"][:-1]:
                if (p[-1] in ".:;?!" and b - ult > 1.8) or b - ult > 3.2:   # saltos de zoom al final de frase, 1,8 s minimo
                    cortes.append(b)
                    ult = b
            d.update(t0=round(s["t0"], 3), cortes=[round(t + c, 3) for c in cortes], niveles=NIVELES)
        linea.append(d)
        t += s["dur"] + (pj.get("pausa_b", GAP) if s["tipo"] == "B" else GAP)   # "pausa_b": la obra se queda un momento despues de la voz en off
    (carpeta / "timeline.json").write_text(json.dumps({"total": round(t, 3), "gap": GAP, "segmentos": linea}, indent=1,
                                                      ensure_ascii=False), encoding="utf-8")
    print("timeline", round(t, 1), "s |", " ".join(f"{s['id']}x{s.get('atempo', '')}" for s in segs if s["tipo"] == "A"))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
