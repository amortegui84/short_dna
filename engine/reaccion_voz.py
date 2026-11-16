"""Reaction format, step between the voice and the render (docs/REACTION_FORMAT.md):
1. joins the edited voice lines (audio/Lxx.wav from montaje.py) into one track, vo/voz_reaccion.wav, with the gaps set in
   proyecto.json "reaccion_huecos" {"L03": 2.1, ...} (seconds of silence BEFORE that line; default 0.15). A gap is where an
   original sound of the footage plays alone or the replay runs;
2. writes vo/tiempos_reaccion.json (start of every line) and vo/palabras_reaccion.json (Whisper word times, for planning cuts
   on words and for the subtitles);
3. with --slots, fills reaccion.json host.clips: one narrator clip per line, starting 0.3 s before its line, and warns when
   a slot is longer than the clip H3 made (9.44 s at most): shift the boundary into a neighbour with room, or hide that
   join behind a "fuera" span (the host leaves the frame while the footage plays).
Usage: python reaccion_voz.py <project> [--slots]"""
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import duracion, palabras, proyecto  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta)
huecos = pj.get("reaccion_huecos", {})
ids = [l["id"] for l in pj["lineas"]]
t, ini = 0.0, {}
for k, lid in enumerate(ids):
    t += huecos.get(lid, 0.15) if k else 0.0
    ini[lid] = round(t, 2); t += duracion(carpeta / "audio" / f"{lid}.wav")
fin = round(t, 2)
ins, fil = [], []
for k, lid in enumerate(ids):
    ins += ["-i", str(carpeta / "audio" / f"{lid}.wav")]
    fil.append(f"[{k}:a]aresample=48000,adelay={int(ini[lid] * 1000)}:all=1[a{k}]")
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
    total = R.get("duracion") or round(fin + 1.2, 2)
    clips = []
    for k, lid in enumerate(ids):
        a = 0.0 if k == 0 else round(ini[lid] - 0.3, 2)
        b = round(ini[ids[k + 1]] - 0.3, 2) if k + 1 < len(ids) else total
        clips.append({"mate": f"mates/{lid}.mov", "ini": a, "fin": b})
        clip = carpeta / "clips" / f"{lid}.mp4"
        if clip.exists() and b - a > duracion(clip) - 0.02:
            print(f"WARNING {lid}: slot {b - a:.2f} s is longer than its clip ({duracion(clip):.2f} s): move the boundary or hide it with 'fuera'")
    R["host"]["clips"] = clips; R["duracion"] = total
    rp.write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
    print("host slots written to reaccion.json")
