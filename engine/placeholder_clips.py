"""Edit-first placeholders for the artist format (user 2026-11-17: "solo pondrás donde va la cara la imagen estática para
saber qué va en ese punto"): every host line (tipo A) gets mates/Lxx.mov (ProRes 4444 with alpha, 1080x1920, 24 fps) and
clips/Lxx.mp4 made from the host's still (characters/<host>/placeholder_head.png), as long as its voice line plus 1 s, so
build_collage.py, cajas.py and the AE builder work unchanged. Replaced by the real Kling cut-outs once the edit is approved.
Run after montaje.py (the line audio sets the length).
Usage: python placeholder_clips.py <project>"""
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import duracion, marca_dir, proyecto  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta)
still = marca_dir(pj["marca"]) / "characters" / pj["personaje"] / "placeholder_head.png"
(carpeta / "mates").mkdir(exist_ok=True); (carpeta / "clips").mkdir(exist_ok=True)
for ln in [l for l in pj["lineas"] if l["tipo"] == "A"]:
    wav = carpeta / "audio" / f"{ln['id']}.wav"
    d = (duracion(wav) if wav.exists() else float(ln.get("dur_mudo", 3.0))) + 1.0
    mate, clip = carpeta / "mates" / f"{ln['id']}.mov", carpeta / "clips" / f"{ln['id']}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(still), "-t", f"{d:.2f}", "-r", "24",
                    "-vf", "scale=1080:1920,format=yuva444p10le", "-c:v", "prores_ks", "-profile:v", "4444", str(mate)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(still), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-t", f"{d:.2f}", "-r", "24", "-vf", "scale=1080:1920,format=yuv420p", "-c:v", "libx264", "-crf", "18",
                    "-c:a", "aac", "-shortest", str(clip)], check=True)
    print(ln["id"], f"{d:.1f} s placeholder", flush=True)
subprocess.run([sys.executable, str(Path(__file__).parent / "cajas.py"), str(carpeta)], check=True)
