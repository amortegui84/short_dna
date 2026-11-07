"""Cajas de la presentadora (alfa del recorte, en coordenadas del mate 1080x1920) cada 0.2 s, como cajas_cabeza.json de las cabezas.
Uso: python cajas_avatar.py avatar_bosch avatar_redon"""
import json, subprocess, sys
from pathlib import Path

import numpy as np

W, H = 1080, 1920
for c in sys.argv[1:]:
    d = Path(c); out = {}
    for m in sorted((d / "mates").glob("L*.mov")):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(m), "-vf", "fps=5,alphaextract,scale=270:480", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                             capture_output=True).stdout
        fr = np.frombuffer(raw, np.uint8).reshape(-1, 480, 270)
        lst = []
        for i, a in enumerate(fr):
            ys, xs = np.nonzero(a > 40)
            caja = [int(xs.min() * 4), int(ys.min() * 4), int((xs.max() + 1) * 4), int((ys.max() + 1) * 4)] if len(xs) else None
            lst.append({"t": round(i * 0.2, 1), "caja": caja})
        out[m.stem.replace("_full", "")] = lst   # Lxx_full (clip + new footage) replaces Lxx
    (d / "cajas_cabeza.json").write_text(json.dumps(out), encoding="utf-8")
    print(c, {k: len(v) for k, v in out.items()})
