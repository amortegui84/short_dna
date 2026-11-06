r"""QA de CARA para imagenes y videos (capa de control de calidad).

Usa ArcFace (faceid.py, carpeta en config face_check.faceid_dir; onnxruntime en CPU, sin tocar la GPU).
Para cada imagen o video mide:
  - presencia: % de fotogramas (o paneles) donde se detecta una cara,
  - parecido: similitud coseno ArcFace de la cara MAS PARECIDA a la foto real (no la mas grande: hay gente de fondo) (>0.55 casi seguro la misma persona, 0.35-0.55 plausible, <0.30 otra),
  - tamano: alto de la cara / alto del fotograma (una cara minuscula no cuenta como cara integrada),
  - estabilidad: parecido minimo y numero de fotogramas "sin cara".
Veredicto PASS si presencia >= 0.80, parecido medio >= 0.45 y parecido minimo >= 0.20.

  python qa_cara.py --ref foto.png video1.mp4 imagen.png ...  [--fps 2] [--json salida.json] [--panels 3 imagen_hoja.png]
Correr con el python del portable (tiene cv2 + onnxruntime):
  D:\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\python_embeded\python.exe engine\qa_cara.py ...
"""
import argparse, json, os, sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import CFG  # noqa: E402
sys.path.insert(0, CFG["face_check"]["faceid_dir"])   # ArcFace (faceid.py: detector + recognizer, onnxruntime on CPU)
from faceid import Caras  # noqa: E402

C = Caras()


def emb_ref(refs):
    es = []
    for r in refs:
        img = cv2.imdecode(np.fromfile(r, dtype=np.uint8), cv2.IMREAD_COLOR)
        d = C.detectar(img)
        if d:
            caja, pts, _ = max(d, key=lambda t: (t[0][2] - t[0][0]) * (t[0][3] - t[0][1]))
            es.append(C.embedding(img, pts))
    if not es:
        sys.exit("no hay cara en la referencia")
    e = np.mean(es, axis=0)
    return e / np.linalg.norm(e)


def medir(img, ref):
    """-> (parecido, alto_rel) de la cara MAS PARECIDA a la referencia (escenas con gente de fondo: no vale la mas grande), o (None, 0)"""
    d = C.detectar(img)
    if not d:
        return None, 0.0
    mejor = None
    for caja, pts, _ in d:
        s = float(C.embedding(img, pts) @ ref)
        if mejor is None or s > mejor[0]:
            mejor = (s, float((caja[3] - caja[1]) / img.shape[0]))
    return mejor


def frames_video(path, fps):
    cap = cv2.VideoCapture(path)
    src = cap.get(cv2.CAP_PROP_FPS) or 24
    paso = max(1, int(round(src / fps)))
    n = 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        if n % paso == 0:
            yield f
        n += 1
    cap.release()


def veredicto(sims, alt):
    n = len(sims)
    con = [s for s in sims if s is not None and s >= 0.30]   # 'presente' = hay una cara con parecido >= 0.30
    pres = len(con) / n if n else 0
    med = float(np.mean(con)) if con else 0.0
    mn = float(np.min(con)) if con else 0.0
    ok = pres >= 0.80 and med >= 0.45 and mn >= 0.20
    return {"n": n, "presencia": round(pres, 3), "parecido_medio": round(med, 3), "parecido_min": round(mn, 3),
            "sin_cara": n - len(con), "alto_cara_medio": round(float(np.mean([a for a in alt if a > 0])) if any(a > 0 for a in alt) else 0, 3),
            "veredicto": "PASS" if ok else "FAIL"}


def qa(path, ref, fps, panels):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".mp4", ".mov", ".webm", ".mkv"):
        fr = list(frames_video(path, fps))
    else:
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if panels > 1:
            w = img.shape[1] // panels
            fr = [img[:, i * w:(i + 1) * w] for i in range(panels)]
        else:
            fr = [img]
    sims, alt = [], []
    for f in fr:
        s, a = medir(f, ref)
        sims.append(s)
        alt.append(a)
    r = veredicto(sims, alt)
    r["archivo"] = path
    r["serie"] = [None if s is None else round(s, 2) for s in sims]
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True, help="foto(s) real(es), separadas por ;")
    ap.add_argument("--fps", type=float, default=2.0)
    ap.add_argument("--panels", type=int, default=1, help="para hojas: numero de paneles verticales iguales")
    ap.add_argument("--json")
    ap.add_argument("archivos", nargs="+")
    a = ap.parse_args()
    ref = emb_ref(a.ref.split(";"))
    out = []
    for p in a.archivos:
        r = qa(p, ref, a.fps, a.panels)
        out.append(r)
        print("%-4s pres=%.2f sim_medio=%.2f sim_min=%.2f sin_cara=%d/%d alto=%.2f  %s" % (
            r["veredicto"], r["presencia"], r["parecido_medio"], r["parecido_min"], r["sin_cara"], r["n"], r["alto_cara_medio"], os.path.basename(p)), flush=True)
    if a.json:
        json.dump(out, open(a.json, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
