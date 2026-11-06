"""Path "reference video": a link (YouTube, TikTok, Instagram, Vimeo... via yt-dlp) or a local file -> measurements Claude
turns into a style. Writes <work_dir>/referencias/<slug>/: video.mp4, cortes.json (shot cuts), hoja.jpg (one frame per shot),
paleta.json, analisis.json {duration, fps, size, shots, cuts_per_min, avg_shot_s, motion_energy 0-1, loudness, palette}.
Next (Claude, with the skill): read hoja.jpg + analisis.json, write a Motion DNA reference profile
(<motion_dna>/library/references/<slug>.json, schema in its _schema.md), run match_reference, then create the missing moves
and a style file in library/styles/. Only analyse videos the user gives you; keep them out of git.
Usage: python referencia.py <url|file> <slug> [brand]"""
import json, re, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from comun import CFG, duracion, marca_dir  # noqa: E402

src, slug = sys.argv[1], sys.argv[2]
marca = sys.argv[3] if len(sys.argv) > 3 else None   # brand folder (brands/<marca>/references/<slug>)
d = marca_dir(marca, True) / "references" / slug; d.mkdir(parents=True, exist_ok=True)
v = d / "video.mp4"
if not v.exists():
    if re.match(r"https?://", src):
        subprocess.run([sys.executable, "-m", "yt_dlp", "-f", "bv*[height<=1920]+ba/b", "--merge-output-format", "mp4", "-o", str(v), src], check=True)
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c", "copy", str(v)], check=True)
info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                                  "-of", "json", str(v)], capture_output=True, text=True).stdout)["streams"][0]
num, den = info["r_frame_rate"].split("/"); fps = float(num) / float(den); dur = duracion(v)
# cortes: cambio de escena > 0.2 (los cortes tapados y los deslizamientos son graduales)
err = subprocess.run(["ffmpeg", "-i", str(v), "-vf", "select='gt(scene,0.2)',showinfo", "-f", "null", "-"], capture_output=True, text=True).stderr
cortes = [round(float(t), 2) for t in re.findall(r"pts_time:([\d.]+)", err)]
planos = [0.0] + cortes + [dur]
(d / "cortes.json").write_text(json.dumps(cortes), encoding="utf-8")
# un cuadro por plano (en su mitad), hasta 24, en una hoja
medios = [(a + b) / 2 for a, b in zip(planos, planos[1:]) if b - a > 0.15][:24]
ims = []
for i, t in enumerate(medios):
    f = d / f"_f{i:02d}.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(v), "-frames:v", "1", "-vf", "scale=-2:320", str(f)], check=True)
    ims.append(Image.open(f).convert("RGB")); f.unlink()
if ims:
    w = max(i.width for i in ims); cols = min(8, len(ims)); rows = -(-len(ims) // cols)
    hoja = Image.new("RGB", (cols * w, rows * 320), "white")
    for k, im in enumerate(ims):
        hoja.paste(im, ((k % cols) * w, (k // cols) * 320))
    hoja.save(d / "hoja.jpg", quality=88)
    allpx = np.concatenate([np.asarray(im.resize((64, 64))).reshape(-1, 3) for im in ims])
    q = Image.fromarray(allpx.reshape(-1, 64, 3).astype(np.uint8)).quantize(colors=8)
    pal = q.getpalette()[:24]; cnt = sorted(q.getcolors(), reverse=True)
    paleta = ["#%02X%02X%02X" % tuple(pal[i * 3:i * 3 + 3]) for _, i in cnt]
else:
    paleta = []
# energia de movimiento: diferencia media entre cuadros a 4 fps
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(v), "-vf", "fps=4,scale=96:-2,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
h = int(96 * info["height"] / info["width"]) // 2 * 2 or 96
fr = np.frombuffer(raw[: len(raw) // (96 * h) * 96 * h], np.uint8).reshape(-1, h, 96).astype(np.float32)
energia = float(np.clip(np.abs(np.diff(fr, axis=0)).mean() / 40, 0, 1)) if len(fr) > 1 else 0.0
lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", str(v), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)
a = {"fuente": src, "duracion_s": round(dur, 2), "fps": round(fps, 2), "tam": [info["width"], info["height"]], "planos": len(planos) - 1,
     "cortes_por_min": round(len(cortes) / dur * 60, 1), "plano_medio_s": round(dur / (len(planos) - 1), 2), "energia_movimiento": round(energia, 3),
     "energia_1a5": 1 + round(energia * 4), "lufs": float(lufs[-1]) if lufs else None, "paleta": paleta}
(d / "analisis.json").write_text(json.dumps(a, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(a, ensure_ascii=False))
