"""The artist's portrait cut out (PNG with alpha) for the artist card ("ficha": the silhouette that fills with colour blocks
and the painter's tools). Source: proyecto.json "retrato" (an artwork stem in obras/). Motion DNA video_matte.py on a still.
Usage: python retrato.py <project>"""
import subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import MOTION_DNA, PY_PORTABLE, proyecto  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta)
out = carpeta / "retrato_recorte.png"
if not out.exists():
    subprocess.run([PY_PORTABLE, str(MOTION_DNA / "tools" / "video_matte.py"), str(carpeta / "obras" / f"{pj['retrato']}.jpg"), str(out)], check=True)
print("retrato", out)
