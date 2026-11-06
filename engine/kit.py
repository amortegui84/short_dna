"""A brand's kit (icons, props, backgrounds, textures) from brands/<brand>/kit/kit_spec.json:
  "alfa":  props with real alpha via Qwen-Image-Layered (RGBA layers; the layer with the most opaque, compact content is kept)
  "fondo": backgrounds and textures via Z-Image Turbo
Local and free (ComfyUI H3 instance). Writes brands/<brand>/kit/<name>.png and HOJA_kit.jpg (contact sheet on red and black).
Skips files that exist (move them to _descartados/ to regenerate). Usage: python kit.py <brand> [name ...]"""
import json, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from comun import marca_dir  # noqa: E402

E = Path(__file__).parent
marca = sys.argv[1]; solo = set(sys.argv[2:])
K = marca_dir(marca, True) / "kit"; tmp = K / "_capas"; tmp.mkdir(exist_ok=True)
spec = json.loads((K / "kit_spec.json").read_text(encoding="utf-8"))
est = spec.get("estilo", "")


def recortar(im):
    """Recorta al objeto: el alfa trae ruido casi invisible; se limpia (<30 -> 0) y se recorta con margen de 8 px."""
    a = np.asarray(im)[..., 3]; arr = np.asarray(im).copy(); arr[..., 3] = np.where(a < 30, 0, a)
    ys, xs = np.nonzero(arr[..., 3])
    if not len(xs):
        return im
    m = 8; return Image.fromarray(arr).crop((max(0, xs.min() - m), max(0, ys.min() - m), min(im.width, xs.max() + m), min(im.height, ys.max() + m)))


def mejor_capa(base):
    """De las capas RGBA, la que tiene un objeto: alfa entre 3 % y 85 % del cuadro, la mas compacta."""
    best, score = None, -1
    for f in sorted(tmp.glob(base.name + "_*.png")):
        a = np.asarray(Image.open(f).convert("RGBA"))[..., 3] > 30
        cov = a.mean()
        if 0.03 < cov < 0.85:
            ys, xs = np.nonzero(a); comp = a.sum() / ((np.ptp(xs) + 1) * (np.ptp(ys) + 1))
            if comp > score:
                best, score = f, comp
    return best


for it in spec.get("alfa", []):
    out = K / f"{it['name']}.png"
    if out.exists() or (solo and it["name"] not in solo):
        continue
    base = tmp / it["name"]
    subprocess.run([sys.executable, str(E / "qwen_layered.py"), "-p", f"{it['prompt']}, {est}", "-o", str(base), "--layers", "3", "--seed", "7"], check=True)
    f = mejor_capa(base)
    if f:
        im = recortar(Image.open(f).convert("RGBA")); im.save(out); print("alfa", out.name, im.size, flush=True)
    else:
        print("alfa", it["name"], "SIN CAPA UTIL (ver _capas/)", flush=True)
for it in spec.get("fondo", []):
    out = K / f"{it['name']}.png"
    if out.exists() or (solo and it["name"] not in solo):
        continue
    subprocess.run([sys.executable, str(E / "zimage_gen.py"), "-p", it["prompt"], "-o", str(out), "--size", it.get("size", "768x1344"), "--seed", "7"], check=True)
    print("fondo", out.name, flush=True)
# recortar lo que ya existe (piezas de corridas anteriores)
for it in spec.get("alfa", []):
    f = K / f"{it['name']}.png"
    if f.exists():
        im = Image.open(f).convert("RGBA")
        if im.size == (768, 768):
            recortar(im).save(f)
# hoja de contacto
fs = sorted(p for p in K.glob("*.png"))
if fs:
    th = []
    for p in fs:
        im = Image.open(p).convert("RGBA"); im.thumbnail((220, 220))
        cell = Image.new("RGBA", (230, 250), (186, 24, 51, 255) if len(th) % 2 else (7, 22, 33, 255)); cell.alpha_composite(im, ((230 - im.width) // 2, (230 - im.height) // 2)); th.append(cell)
    cols = 6; rows = -(-len(th) // cols); hoja = Image.new("RGBA", (cols * 230, rows * 250), (0, 0, 0, 255))
    for i, c in enumerate(th):
        hoja.alpha_composite(c, ((i % cols) * 230, (i // cols) * 250))
    hoja.convert("RGB").save(K / "HOJA_kit.jpg", quality=86)
print("kit:", len(fs), "files in", K)
