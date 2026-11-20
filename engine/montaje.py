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
from comun import duracion, palabras, personaje, proyecto, run, fin_habla, inicio_real, inicio_habla, apretar_pausas  # noqa: E402


PJ_ESTIRAR = None


def tempo(r):
    """Voice speed-up: rubberband keeps the timbre and the consonants (proyecto.json "estirar": "rubberband"; the v3 storyteller
    voice comes out at ~90 wpm and needs 1.6-1.8x, review 2026-11-12); atempo smears a gravelly voice past ~1.05."""
    if r == 1.0:
        return "anull"
    return f"rubberband=tempo={r}:transients=crisp:formant=preserved" if PJ_ESTIRAR == "rubberband" else f"atempo={r}"

GAP = 0.12
NIVELES = [1.0, 1.32, 1.12, 1.45]   # encuadres del avatar en cada salto de zoom
SIL = ("silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.06:stop_periods=-1:stop_duration=0.3:stop_silence=0.08:stop_threshold=-55dB,afade=t=in:d=0.012")
# conservar_pausas (narradores dramaticos): solo se recortan el silencio del principio y del final; las pausas y silencios quedan
SIL_BORDES_T = ("silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.06:stop_periods=-1:stop_duration={pausa}:stop_silence={pausa}:stop_threshold=-55dB,"   # pausas de hasta 0.9 s
              "areverse,silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.08,areverse,afade=t=in:d=0.012")
# the -45 dB threshold ate soft onsets and word tails of a breathy voice; -55 dB plus 60-80 ms of kept air does not


def tiempos_guion(texto, oidas, ini, fin, sustituir):
    """Palabras del guion (lo que se lee) con tiempos: los de Whisper si coinciden en numero; si no, repartidos."""
    guion = [sustituir.get(g, g) for g in texto.replace("...", " ").split()]
    if len(oidas) == len(guion):
        return [(g, a, b) for g, (_, a, b) in zip(guion, oidas)]
    pesos = np.array([len(g) + 2 for g in guion], float)
    bordes = ini + np.concatenate([[0], np.cumsum(pesos)]) / pesos.sum() * (fin - ini)
    return [(g, float(bordes[i]), float(bordes[i + 1])) for i, g in enumerate(guion)]


def main(carpeta):
    global PJ_ESTIRAR
    pj = proyecto(carpeta)
    PJ_ESTIRAR = pj.get("estirar")
    sus = pj.get("sustituir", {})
    aud = carpeta / "audio"
    aud.mkdir(exist_ok=True)
    segs = []
    sin_boca = bool(pj.get("personaje") and personaje(pj).get("sin_boca"))
    filtro = SIL_BORDES_T.format(pausa=pj.get("pausa_max", 0.45)) if pj.get("conservar_pausas") else SIL   # pausas dramaticas de hasta pausa_max s
    for ln in pj["lineas"]:
        lid, vo = ln["id"], carpeta / "vo" / f"{ln['id']}.mp3"
        limpia = aud / f"{lid}_limpia.wav"
        # with Seedance a host line has no TTS (its voice is the clip's, converted by sts.py): nothing to clean
        if vo.exists():
            run(["ffmpeg", "-y", "-v", "error", "-i", str(vo), "-af", filtro, "-ac", "2", "-ar", "48000", str(limpia)])
        wav = aud / f"{lid}.wav"
        if ln["tipo"] == "A" and sin_boca:
            # personaje sin boca: no hay labios que cuadrar; la linea dura lo que dura la voz (con sus pausas) y el clip arranca con ella
            clip = carpeta / "clips" / f"{lid}.mp4"
            ritmo_a = pj.get("ritmo_a", 1.0)   # narrador sin boca: se puede acelerar sin romper labios (ep de ~1 min)
            run(["ffmpeg", "-y", "-v", "error", "-i", str(limpia), "-af", f"{tempo(ritmo_a)},apad=pad_dur=0.2,loudnorm=I=-20:TP=-2:LRA=9", "-ar", "48000", str(wav)])
            ws = palabras(wav)
            pal = tiempos_guion(ln["texto"], ws, ws[0][1], ws[-1][2], sus)
            segs.append({"id": lid, "tipo": "A", "clip": str(clip), "t0": 0.0, "dur": duracion(wav), "pal": pal, "wav": str(wav), "atempo": "voz"})
            continue
        if ln["tipo"] == "A" and ln.get("mudo"):
            # a silent host beat (a grimace, a look): no words, silent audio for "dur_montaje" s (default the clip's length)
            clip = carpeta / "clips" / f"{lid}.mp4"
            dm = float(ln.get("dur_montaje") or (duracion(clip) if clip.exists() else ln.get("dur_mudo", 2.0)))
            run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{dm:.3f}", str(wav)])
            segs.append({"id": lid, "tipo": "A", "clip": str(clip), "t0": 0.0, "dur": dm, "pal": [], "wav": str(wav), "atempo": "mudo"})
            continue
        if ln["tipo"] == "A" and not pj.get("cabeza_placeholder"):
            clip = carpeta / "clips" / f"{lid}.mp4"
            ws = palabras(clip)
            t0, t1 = max(0.0, inicio_real(clip, ws[0][1]) - 0.12), fin_habla(clip, ws[-1][2]) + 0.18   # by sound: Whisper ends trailing words early
            ventana = t1 - t0
            sts = aud / f"{lid}_sts.mp3"
            if sts.exists():
                # el habla de H3 (labios perfectos) con el timbre de la voz del video (sts.py): mismo ritmo, mismas pausas
                # STS turns the take's room tone before the first word into a loud breath/hiss (A08 L09 2026-11-17, 70 dB): mute the
                # audio until 60 ms before the speech onset in the clip (timing untouched, so the lips stay in sync)
                pre = max(0.0, inicio_habla(clip, t0, umbral=45.0) - t0 - 0.06)
                run(["ffmpeg", "-y", "-v", "error", "-i", str(sts), "-af",
                     f"afade=t=in:st={pre:.3f}:d=0.05,apad=whole_dur={ventana:.3f},atrim=0:{ventana:.3f},loudnorm=I=-20:TP=-2:LRA=7", "-ac", "2", "-ar", "48000", str(wav)])
                f = "sts"
            else:
                # sin STS: la VO cabe en la ventana de los labios con atempo (0.8-1.25); el lipsync queda aproximado
                f = min(1.25, max(0.8, duracion(limpia) / (ventana - 0.1)))
                run(["ffmpeg", "-y", "-v", "error", "-i", str(limpia), "-af",
                     f"atempo={f:.4f},adelay=60|60,apad=whole_dur={ventana:.3f},atrim=0:{ventana:.3f},loudnorm=I=-20:TP=-2:LRA=7",
                     "-ar", "48000", str(wav)])
            pal = [(p, a - t0, b - t0) for p, a, b in tiempos_guion(ln["texto"], ws, ws[0][1], ws[-1][2], sus)]
            if lid in (pj.get("sin_cara") or []):
                # QA 2026-11-19 (A08 v5, 4.2-5.6 s): a host line played without its face kept the take's 1.1 s of air before the
                # first word. No lips on screen, so the air goes: start 0.06 s before the speech onset
                lead = max(0.0, inicio_habla(wav, 0.0, umbral=45.0) - 0.06)
                if lead > 0.15:
                    tmp = wav.with_name(f"{lid}_sinaire.wav")
                    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{lead:.3f}", "-i", str(wav), "-af", "afade=t=in:d=0.01", str(tmp)])
                    tmp.replace(wav); t0 += lead; ventana -= lead
                    pal = [(p, a - lead, b - lead) for p, a, b in pal]
                    print(lid, f"sin_cara: {lead:.2f} s of air cut before the first word", flush=True)
            segs.append({"id": lid, "tipo": "A", "clip": str(clip), "t0": t0, "dur": ventana, "pal": pal, "wav": str(wav),
                         "atempo": f if f == "sts" else round(f, 3)})
        else:
            # la voz en off va a 1.08; las cabezas flotantes piden mas ritmo (sin labios en estas lineas, se puede acelerar)
            ritmo_b = pj.get("ritmo_b") or (1.2 if pj.get("cabeza") else 1.08)   # proyecto.json "ritmo_b" manda (avatar v10b: 1.05, para ver las obras)
            # 90 % rule: the gaps between words go first (no speed change), then the line's tempo
            apretada = aud / f"{lid}_apretada.wav"
            antes, despues = apretar_pausas(limpia, apretada)
            # safety: the tightened line must keep every word Whisper heard before (a lost word = the cut ate a sound)
            w0, w1 = len(palabras(limpia)), len(palabras(apretada))
            if w1 < w0:
                print(f"{lid} pauses: tightening lost {w0 - w1} word(s), kept the original", flush=True)
            else:
                print(f"{lid} pauses: {antes:.2f} s -> {despues:.2f} s ({despues / max(antes, 0.01) * 100:.0f} %)", flush=True)
                limpia = apretada
            # QA 2026-11-19 (A09 v1: 0.6 s of silence between voice-over lines): the line's own trailing air goes (0.10 s kept),
            # like the news format's reaccion_aire_b; the leading air is already cut by apretar_pausas
            aire = "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.10,areverse"
            run(["ffmpeg", "-y", "-v", "error", "-i", str(limpia), "-af", f"{aire},{tempo(ritmo_b)},apad=pad_dur=0.05,loudnorm=I=-20:TP=-2:LRA=7",
                 "-ar", "48000", str(wav)])
            ws = palabras(wav)
            pal = tiempos_guion(ln["texto"], ws, ws[0][1], ws[-1][2], sus)
            # edit-first (user 2026-11-17): with "cabeza_placeholder" a host line is voiced like a voice-over line and keeps its tipo
            segs.append({"id": lid, "tipo": ln["tipo"], "dur": duracion(wav), "pal": pal, "wav": str(wav), "obras": ln.get("obras", [])})

    # the first word must not sit on frame 0: players and phones swallow the first ~100 ms, and silenceremove leaves no breath
    # before it ("the Cooper audio is cut at the start", review 2026-11-13). The first line gets a 0.35 s lead-in.
    ENTRADA = 0.35
    if segs and segs[0]["tipo"] == "B" or (segs and segs[0].get("atempo") == "voz"):
        s0 = segs[0]
        con = Path(s0["wav"]).with_name(Path(s0["wav"]).stem + "_entrada.wav")
        ms = int(ENTRADA * 1000)
        run(["ffmpeg", "-y", "-v", "error", "-i", s0["wav"], "-af", f"adelay={ms}|{ms}", "-ar", "48000", str(con)])
        con.replace(s0["wav"])
        s0["dur"] += ENTRADA
        s0["pal"] = [(p, a + ENTRADA, b + ENTRADA) for p, a, b in s0["pal"]]
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
            d.update(t0=round(s.get("t0", 0.0), 3), cortes=[round(t + c, 3) for c in cortes], niveles=NIVELES)
        linea.append(d)
        t += s["dur"] + (pj.get("pausa_b", GAP) if s["tipo"] == "B" else GAP)   # "pausa_b": la obra se queda un momento despues de la voz en off
    (carpeta / "timeline.json").write_text(json.dumps({"total": round(t, 3), "gap": GAP, "segmentos": linea}, indent=1,
                                                      ensure_ascii=False), encoding="utf-8")
    # gate: the cleaned, sped-up lines are checked again (silenceremove or rubberband must not eat a word or cut into a sound)
    from qa_lineas import revisar
    fallas = revisar(carpeta, audio=True)
    if fallas:
        for f in fallas:
            print("qa_lineas FAIL", f)
        sys.exit(f"montaje: {len(fallas)} line(s) cut or silent after cleaning (qa_lineas_audio.json)")
    print("timeline", round(t, 1), "s |", " ".join(f"{s['id']}x{s.get('atempo', '')}" for s in segs if s["tipo"] == "A"))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
