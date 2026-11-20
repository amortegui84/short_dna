"""Reaction format, step between the voice and the render (docs/REACTION_FORMAT.md):
1. joins the edited voice lines (audio/Lxx.wav from montaje.py) into one track, vo/voz_reaccion.wav, with the gaps set in
   proyecto.json "reaccion_huecos" {"L03": 2.1, ...} (seconds of silence BEFORE that line; default 0.15). A gap is where an
   original sound of the footage plays alone or the replay runs;
2. writes vo/tiempos_reaccion.json (start of every line) and vo/palabras_reaccion.json (Whisper word times, for planning cuts
   on words and for the subtitles);
3. with --slots, fills reaccion.json host.clips: one narrator clip per line, starting 0.3 s before its line, and warns when
   a slot is longer than the clip H3 made (9.44 s at most): shift the boundary into a neighbour with room, or hide that
   join behind a "fuera" span (the host leaves the frame while the footage plays).
   A host WITH a mouth (Cool Culture Club) is lip-synced: each clip starts exactly on its line, from the second where its
   speech starts in the clip ("t0" in timeline.json, written by montaje.py), so the voice and the lips stay together.
Usage: python reaccion_voz.py <project> [--slots]"""
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import duracion, energia, palabras, personaje, proyecto  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta)
huecos = pj.get("reaccion_huecos", {})
HUECO = pj.get("reaccion_hueco", 0.15)   # default gap between lines (CCC 2026-11-17 "too many silences": 0.05)
recortes = pj.get("reaccion_recortes", {})   # {"L09": [[a, b]]} pauses cut out of a line (line seconds); the host clip is split
tipo = {l["id"]: l["tipo"] for l in pj["lineas"]}
ids = [l["id"] for l in pj["lineas"]]
lin = carpeta / "vo" / "_lineas"; lin.mkdir(parents=True, exist_ok=True)
partes = {}   # lid -> [(start in the processed line, start in the original line, length)]
for lid in ids:
    src = carpeta / "audio" / f"{lid}.wav"; d = duracion(src)
    # voice-over lines lose their leading/trailing air (no lips to keep in sync); host lines keep their window
    a0, a1 = 0.0, d
    if tipo[lid] == "B" and pj.get("reaccion_aire_b", True):
        e = energia(src, 50); voz_i = [i for i, v in enumerate(e) if v > 30]
        if voz_i:
            a0, a1 = max(0.0, voz_i[0] / 50 - 0.06), min(d, (voz_i[-1] + 1) / 50 + 0.10)
    tramos, cur = [], a0
    for x, y in sorted(recortes.get(lid, [])):
        tramos.append((cur, x)); cur = y
    tramos.append((cur, a1))
    sel = "+".join(f"between(t,{x:.3f},{y:.3f})" for x, y in tramos)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", f"aselect='{sel}',asetpts=N/SR/TB", str(lin / f"{lid}.wav")], check=True)
    pos, partes[lid] = 0.0, []
    for x, y in tramos:
        partes[lid].append((round(pos, 3), round(x, 3), round(y - x, 3))); pos += y - x
t, ini = 0.0, {}
for k, lid in enumerate(ids):
    t += huecos.get(lid, HUECO) if k else 0.0
    ini[lid] = round(t, 2); t += duracion(lin / f"{lid}.wav")
fin = round(t, 2)
ins, fil = [], []
for k, lid in enumerate(ids):
    ins += ["-i", str(lin / f"{lid}.wav")]
    # a 60 ms fade where the line's sound ends (its breath/room tail) and 10 ms in: a line never stops from sound to digital
    # silence in one step (2026-11-17: L07 ended 57 dB -> 0, a click; qa_audio.py flags such drops)
    e = energia(lin / f"{lid}.wav", 50); cola = max([i for i, v in enumerate(e) if v > 20] or [len(e) - 1]) / 50 + 0.02
    fil.append(f"[{k}:a]aresample=48000,afade=t=in:d=0.01,afade=t=out:st={max(0.0, cola - 0.06):.3f}:d=0.06,adelay={int(ini[lid] * 1000)}:all=1[a{k}]")
fil.append("".join(f"[a{k}]" for k in range(len(ids))) + f"amix=inputs={len(ids)}:normalize=0:duration=longest[o]")
(carpeta / "vo").mkdir(exist_ok=True)
voz = carpeta / "vo" / "voz_reaccion.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fil), "-map", "[o]", "-ac", "2", str(voz)], check=True)
(carpeta / "vo" / "tiempos_reaccion.json").write_text(json.dumps({"ini": ini, "fin": fin}, indent=1), encoding="utf-8")
ws = [list(w) for w in palabras(voz)]
(carpeta / "vo" / "palabras_reaccion.json").write_text(json.dumps(ws), encoding="utf-8")
print("voice", fin, "s |", " ".join(f"{lid}@{s}" for lid, s in ini.items()))
print(" ".join(f"{w[0]}@{w[1]:.1f}" for w in ws))

if "--slots" in sys.argv:
    rp = carpeta / "reaccion.json"
    R = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {"slug": pj["slug"], "voz": "vo/voz_reaccion.wav", "host": {}, "planos": [], "tarjetas": []}
    total = R.get("duracion_fija") or round(fin + 1.0, 2)   # the video ends 1 s after the last word
    labios = not personaje(pj).get("sin_boca")
    t0s = {}
    if labios and (carpeta / "timeline.json").exists():
        t0s = {sg["id"]: sg.get("t0") or 0.0 for sg in json.loads((carpeta / "timeline.json").read_text(encoding="utf-8"))["segmentos"]}
    lead = 0.0 if labios else 0.3   # a mouthless narrator can start his gesture before the word; lips cannot
    clips, fuera = [], []
    for k, lid in enumerate(ids):
        if tipo[lid] != "A":
            continue
        a = 0.0 if k == 0 else round(ini[lid] - lead, 2)
        b = round(ini[ids[k + 1]] - lead, 2) if k + 1 < len(ids) else total
        c = {"mate": f"mates/{lid}.mov", "ini": a, "fin": b}
        if pj.get("cabeza_placeholder"):   # edit-first: the host's still marks where the head goes
            from comun import marca_dir
            c["mate"] = (marca_dir(pj["marca"]) / "characters" / pj["personaje"] / "placeholder_head.png").as_posix()
        if labios:
            c["desde"] = round(t0s.get(lid, 0.0), 3)
        if len(partes[lid]) > 1:   # a pause was cut: one clip per kept part, each from its own place in the take
            for q, (po, pi, ln) in enumerate(partes[lid]):
                cq = dict(c, ini=round(a if q == 0 else ini[lid] + po, 2), fin=round(b if q == len(partes[lid]) - 1 else ini[lid] + po + ln, 2))
                cq["desde"] = round(c.get("desde", 0.0) + pi - (0.0 if q == 0 else 0.0), 3) if q else c.get("desde", 0.0)
                clips.append(cq)
            continue
        clips.append(c)
        clip = carpeta / "clips" / f"{lid}.mp4"
        if clip.exists() and b - a > duracion(clip) - c.get("desde", 0) - 0.02:
            util = duracion(clip) - c.get("desde", 0)
            falta = b - a - util
            if k == len(ids) - 1:   # the last host clip closes the video: it ends with him, he never ducks out at the close
                total = round(a + util - 0.04, 2); clips[-1]["fin"] = total
                continue
            if falta < 0.3:   # a few frames held on the last frame read as a natural pause
                continue
            if falta < 2.5:
                # the clip runs out in the gap before the next line: he ducks out instead of freezing (a still mouth reads
                # as broken), and comes back up with the next line
                fuera.append([round(a + util - 0.35, 2), round(b + 0.05, 2)])
                print(f"{lid}: clip ends {b - a - util:.2f} s before the next line -> host ducks out {fuera[-1]}")
            else:
                print(f"WARNING {lid}: slot {b - a:.2f} s is longer than its clip ({util:.2f} s usable): move the boundary or hide it with 'fuera'")
    R["host"]["clips"] = clips; R["duracion"] = total
    R["host"]["fuera"] = sorted(fuera + R["host"].get("fuera_manual", []))   # manual spans live in "fuera_manual"
    rp.write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
    print("host slots written to reaccion.json")
