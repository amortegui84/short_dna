"""Stage "continuar": the narrator never loops. When a narrator section of the edit (datos_ae.json, written by the ae stage)
lasts longer than his talking clip, the edit used to play the clip forward and backward (ping-pong) and it looked like a
rewind (review 2026-11-06, ep04). This stage generates NEW footage instead: H3 (local) from the clip's last frame, the
narrator silently going on with the story with gestures that follow the voice-over of the lines that play over him, then
joins it to the clip as clips/Lxx_full.mp4 (the talking clip stays untouched: After Effects may hold it open; the matte
and the comp use _full when it exists), re-cuts his matte and rebuilds the comp.
A section that still came up short holds its last frame (ae/cinta.jsx), never rewinds.
Usage: python continuar.py <project> [--dry]"""
import json, os, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import H3, PY_PORTABLE, clip_roto, con_mesa, duracion, personaje, proyecto, run  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta); seco = "--dry" in sys.argv
PJE = personaje(pj)
datos = json.loads((carpeta / "datos_ae.json").read_text(encoding="utf-8"))
REJILLA = [4.46, 5.17, 5.875, 6.58, 7.29, 8.0, 8.71, 9.42]
PIKA = ["--turbo", "pika_h3_flex_ref2va_v1_bf16.safetensors", "--steps", "6", "--no-shift", "--size", "768x1344",
        "--lora", "minidv_lora_h3_v1.safetensors:0.9"]
ENV = dict(os.environ, H3_SAMPLER="lcm", H3_SIGMAS="1.0, 0.972973, 0.923077, 0.8, 0.571429, 0.333333, 0.0")
lineas = pj["lineas"]; ids = [l["id"] for l in lineas]

def gesto(lid, ini, fin):
    """What he does while the voice goes on (rule: docs/templates/script.md › Movement): proyecto.json "continuacion" if the
    script wrote it; else derived from the words read over him, chained between the move he just made and the next scene's
    move, and avoiding every move already used in the episode."""
    extra = (pj.get("continuacion") or {}).get(lid)
    if extra:
        return extra
    tl = json.loads((carpeta / "timeline.json").read_text(encoding="utf-8"))["segmentos"]
    textos = [s for s in tl if s["tipo"] == "B" and s["start"] < fin - 0.3 and s["start"] + s["dur"] > ini + 0.3]
    dichos = " ".join(next(l["texto"] for l in lineas if l["id"] == s["id"]) for s in textos)
    a_ids = [l["id"] for l in lineas if l["tipo"] == "A"]
    acc = {l["id"]: l.get("accion", "") for l in lineas if l["tipo"] == "A"}
    sig = a_ids[a_ids.index(lid) + 1] if lid in a_ids and a_ids.index(lid) + 1 < len(a_ids) else None
    usados = "; ".join(v for v in acc.values() if v)
    que = (f"he listens to the voice-over and stays calm, mostly still, with at most one small slow gesture that fits it: \"{dichos}\""
           if dichos else "he listens in silence, a slow small movement of the head and one hand")
    return (f"{que}. He has just finished this move, so he starts from its end pose and does not repeat it: \"{acc.get(lid, '')}\". "
            + (f"He ends calmly, ready for the next scene, where he will: \"{acc[sig]}\". " if sig else "")
            + f"Use a new movement, none of these moves already used in the video: {usados}. "
            + "He only moves his hands, head and shoulders: his gloved hands stay empty, and no other person, child or object "
            + "appears in the shot (the model draws whatever a gesture names). He keeps his face toward the lens and never turns "
            + "to look behind him or over his shoulder")

hechos = []
for s in datos["secciones"]:
    if s.get("tipo") not in ("gancho", "cabeza") or not s.get("clip"):
        continue
    lid = s["id"]; base = carpeta / "clips" / f"{lid}.mp4"; full = carpeta / "clips" / f"{lid}_full.mp4"
    falta = (s["fin"] - s["ini"]) - duracion(base) + 0.4
    if falta <= 0.45:
        continue
    print(f"[{lid}] section {s['fin'] - s['ini']:.1f} s, clip {duracion(base):.1f} s: {falta:.1f} s of new footage", flush=True)
    if seco:
        continue
    piezas, previo, k = [base], base, 0
    while falta > 0.2:
        k += 1
        seg = next((x for x in REJILLA if x >= falta), REJILLA[-1])
        ini_png = carpeta / "clips" / f"{lid}_cont{k}_inicio.png"
        run(["ffmpeg", "-y", "-v", "error", "-sseof", "-0.12", "-i", str(previo), "-frames:v", "1", "-update", "1", str(ini_png)])
        prompt = con_mesa(f"""subject_definitions:
<Subject 1> is the hooded storyteller from <Picture 1>: black hood and robe, a smooth pale-yellow oval mask with no mouth and a single painted black eye, black gloves; his look matches <Picture 2> exactly.

summary:
[reference-to-video generation + audio generation]
A vertical horror-storytelling Shorts clip: the masked narrator goes on telling the story without words while his voice-over plays.

retention_analysis:
<Subject 1>: fully_preserved (mask, hood, robe, gloves, room, the objects on the table)

detailed_description:
A realistic, grainy vertical 9:16 video, static camera at eye level, medium shot, continuing exactly from <Picture 1>, same pose to start, same room: CRT televisions with static behind him, clear plastic sheeting, melted candles, red light from one side and cold blue CRT glow from the other. He does not speak and his mask never moves or gets a mouth. Then {gesto(lid, s['ini'], s['fin'])}. Smooth, continuous motion, no cuts, no jumps. Whatever is in his hands in <Picture 1> stays the same; nothing new appears in his hands and nothing vanishes.

overall_soundscape:
Low room tone and a faint CRT hum only. No voice.

non_diegetic_music:
N/A
""", pj)
        pf = carpeta / "prompts" / f"{lid}_cont{k}.txt"; pf.parent.mkdir(exist_ok=True); pf.write_text(prompt, encoding="utf-8")
        out = carpeta / "clips" / f"{lid}_cont{k}.mp4"
        # H3 sometimes collapses mid-clip (ep05 L10_cont1 went dark and smeared): check every take, re-seed up to 3 times
        for intento, seed in enumerate((41 + k, 141 + k, 241 + k)):
            if not out.exists():
                subprocess.run([PY_PORTABLE, H3, "-p", str(pf), "--img", str(ini_png), str(PJE["_dir"] / PJE["maestro"]),
                                "--seconds", str(seg), *PIKA, "--gen-audio", "--seeds", str(seed), "-o", str(out)], check=True, env=ENV)
            roto = clip_roto(out)
            if not roto:
                break
            print(f"[{lid}] cont{k} seed {seed}: {roto}" + ("; new seed" if intento < 2 else "; kept, check it by eye"), flush=True)
            if intento < 2:
                out.replace(out.with_name(f"{out.stem}_roto{intento}.mp4"))
        piezas.append(out); previo = out; falta -= duracion(out) - 0.1
    # join: the talking clip and its continuations, same size and rate, no audio (the voice-over is separate)
    w, h, r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                              "-of", "csv=p=0", str(base)], capture_output=True, text=True).stdout.strip().split(",")
    # H3 does not always start exactly on the given frame (ep05 L08: a one-frame pose jump at the join), so each join is a
    # short cross-dissolve (XF s) instead of a hard cut
    XF = 0.24
    ent = sum([["-i", str(p)] for p in piezas], [])
    fil = "".join(f"[{i}:v]scale={w}:{h},fps={r},setsar=1,settb=AVTB[v{i}];" for i in range(len(piezas)))
    prev, acc = "v0", duracion(piezas[0])
    for i in range(1, len(piezas)):
        fil += f"[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={acc - XF:.3f}[x{i}];"
        prev, acc = f"x{i}", acc + duracion(piezas[i]) - XF
    fil += f"[{prev}]null[v]"
    run(["ffmpeg", "-y", "-v", "error", *ent, "-filter_complex", fil, "-map", "[v]", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(full)])
    hechos.append(lid); print(f"[{lid}] joined -> {full} ({duracion(full):.1f} s)", flush=True)

if hechos and not seco:
    E = Path(__file__).parent
    # the ending starts from the narrator's last frame, but stage "final" runs before this one: when the last section was
    # extended here, its end pose changed (ep05: the ending started from the short clip), so remake the ending from it
    ultimo = [l["id"] for l in lineas if l["tipo"] == "A"][-1]
    full, fin = carpeta / "clips" / f"{ultimo}_full.mp4", carpeta / "final" / "autodestruccion.mp4"
    def otro_inicio():
        """True when the ending was not started from the extended clip's last frame (final/inicio.png differs from it)."""
        import cv2, numpy as np
        ini = carpeta / "final" / "inicio.png"
        if not fin.exists() or not ini.exists():
            return True
        tmp = carpeta / "clips" / f"{ultimo}_full_ultimo.png"
        run(["ffmpeg", "-y", "-v", "error", "-sseof", "-0.15", "-i", str(full), "-frames:v", "1", "-update", "1", str(tmp)])
        a, b = (cv2.resize(cv2.imread(str(x), cv2.IMREAD_GRAYSCALE), (96, 168)).astype(np.float32) for x in (ini, tmp))
        return float(np.abs(a - b).mean()) > 3   # a re-encode differs < 1; another pose > 10
    if (pj.get("autodestruccion") or {}).get("prompt") and full.exists() and otro_inicio():
        if fin.exists():
            fin.replace(fin.with_name("autodestruccion_previo.mp4"))
        print(f"[{ultimo}] extended: remaking the ending from its last frame", flush=True)
        subprocess.run([sys.executable, str(E / "final.py"), str(carpeta)], check=True)
    subprocess.run([sys.executable, str(E / "mates.py"), str(carpeta)], check=True)
    subprocess.run([sys.executable, str(E / "build_collage.py"), str(carpeta)], check=True)
print("continuar:", ", ".join(hechos) or "nothing to extend")
