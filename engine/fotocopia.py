"""The artist as a modern photocopy cutout (Cool Culture Club bricolage portrait), made locally from the cut-out portrait
(retrato.py -> retrato_recorte.png): crisp high-contrast black and white with a fine halftone dot texture, cut by hand
along the silhouette with a thin even white paper border, transparent background. Replaces the paid GPT Image edit of
the handoff (prompts/subject_cutout.txt) for a first pass. Writes retrato_bricolage.png.
Usage: python fotocopia.py <project> [--hombros 0.62]"""
import sys
from pathlib import Path

import cv2
import numpy as np

carpeta = Path(sys.argv[1]).resolve()
hombros = float(sys.argv[sys.argv.index("--hombros") + 1]) if "--hombros" in sys.argv else 0.62
src = cv2.imread(str(carpeta / "retrato_recorte.png"), cv2.IMREAD_UNCHANGED)
if src is None or src.shape[2] < 4:
    sys.exit("fotocopia: needs retrato_recorte.png with alpha (engine/retrato.py)")
a = src[..., 3]
ys, xs = np.where(a > 128)
y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
# a bust like the Bosch template's cutout (A_bosch_cutout): top of the head to mid-chest, cut straight across.
# In the template the chin sits at 55% of the cutout's height (head 570 px, chest below the chin 460 px): find the face
# and cut 0.8 head-heights below the chin; without a face, fall back to --hombros of the figure
gris = cv2.cvtColor(src[..., :3], cv2.COLOR_BGR2GRAY)
caras = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml").detectMultiScale(gris, 1.1, 6, minSize=(60, 60))
if len(caras):
    fx, fy, fw, fh = max(caras, key=lambda r: r[2] * r[3])
    barbilla = fy + fh * 1.08
    y1 = int(min(y1, barbilla + 0.8 * (barbilla - y0)))
    print("fotocopia: face", (fx, fy, fw, fh), "bust bottom", y1)
else:
    y1 = int(y0 + (y1 - y0) * hombros)
xs2 = np.where(a[y0:y1].max(0) > 128)[0]
x0, x1 = xs2.min(), xs2.max()
cara = None
if len(caras):
    # a wide figure (long hair, fur coat) is trimmed at the sides to 0.95 face widths from the face centre (Bosch: bust width = 1.2 head heights), so the bust keeps
    # the template's proportions and the head can match the template's head size
    cx = fx + fw / 2
    x0, x1 = int(max(x0, cx - 0.95 * fw)), int(min(x1, cx + 0.95 * fw))
    cara = {"top": int(y0), "chin": float(barbilla)}
im, a = src[y0:y1, x0:x1, :3], src[y0:y1, x0:x1, 3]
# black and white, strong contrast like a fresh laser copy
g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
g = clahe.apply(g.astype(np.uint8)).astype(np.float32)
lo, hi = np.percentile(g[a > 128], [8, 92])
g = np.clip((g - lo) / max(1, hi - lo), 0, 1)
g = np.clip((g - 0.5) * 1.6 + 0.5, 0, 1)
# halftone: a dot grid at 45 degrees; each dot's size follows the darkness
h, w = g.shape
cell = max(5, int(w / 160))
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
u = (xx + yy) / np.sqrt(2); v = (xx - yy) / np.sqrt(2)
du = (u % cell) - cell / 2; dv = (v % cell) - cell / 2
d = np.sqrt(du * du + dv * dv) / (cell * 0.72)
dark = 1 - cv2.GaussianBlur(g, (0, 0), cell * 0.35)
dots = (d < dark).astype(np.float32)
ink = np.where(g < 0.18, 1.0, np.where(g > 0.86, 0.0, dots))
ink = np.maximum(ink, (cv2.Canny((g * 255).astype(np.uint8), 60, 140) > 0).astype(np.float32) * 0.9)
out = (255 * (1 - ink)).astype(np.uint8)
# hand-cut silhouette with a thin white paper border
m = (a > 128).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
borde = max(8, int(w / 70))
pad = borde * 2
m = cv2.copyMakeBorder(m, pad, pad, pad, pad, cv2.BORDER_CONSTANT, 0)
out = cv2.copyMakeBorder(out, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=255)
grande = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (borde * 2 + 1, borde * 2 + 1)))
cnts, _ = cv2.findContours(grande, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
corte = np.zeros_like(grande)
for cn in cnts:
    ap = cv2.approxPolyDP(cn, borde * 0.6, True)   # scissors: a slightly faceted outline, not a perfect one
    cv2.fillPoly(corte, [ap], 1)
rgb = np.where(m[..., None] > 0, out[..., None].repeat(3, 2), 250)
rgba = np.dstack([rgb.astype(np.uint8), (corte * 255).astype(np.uint8)])
cv2.imwrite(str(carpeta / "retrato_bricolage.png"), rgba)
# where the head sits in the cutout (output pixels), so the AE builder can match the template's head size and place
if cara:
    import json
    meta = {"head_top": int(pad), "chin": float(cara["chin"] - y0 + pad), "w": int(rgba.shape[1]), "h": int(rgba.shape[0])}
    (carpeta / "retrato_bricolage.json").write_text(json.dumps(meta), encoding="utf-8")
    print("fotocopia: head", meta)
print("fotocopia", carpeta / "retrato_bricolage.png", rgba.shape)
