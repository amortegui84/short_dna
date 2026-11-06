"""Cut-out of the presenter in every talking clip (Motion DNA tools/video_matte.py, InSPyReNet on the local GPU): ProRes 4444
with alpha at 1080x1920 / 24 fps in <project>/mates/Lxx.mov. The boom mic stays in the cut-out (the user kept it).
Then cajas.py writes the bounding boxes used to keep labels off her face.
Usage: python mates.py <project>"""
import subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import MOTION_DNA, PY_PORTABLE, proyecto  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta)
(carpeta / "mates").mkdir(exist_ok=True)
for ln in [l for l in pj["lineas"] if l["tipo"] == "A"]:
    out = carpeta / "mates" / f"{ln['id']}.mov"
    if out.exists():
        continue
    subprocess.run([PY_PORTABLE, str(MOTION_DNA / "tools" / "video_matte.py"), str(carpeta / "clips" / f"{ln['id']}.mp4"), str(out),
                    "--size", "1080x1920", "--fps", "24"], check=True)
    print(ln["id"], "mate ok", flush=True)
subprocess.run([sys.executable, str(Path(__file__).parent / "cajas.py"), str(carpeta)], check=True)
