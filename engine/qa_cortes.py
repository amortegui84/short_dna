"""Deep cut QA on a rendered episode, run before every delivery (review CCC Blake v1: "lost frames that look like jumps", "the
black background in the image transitions", "she shows for one second and is cut before finishing the word").
Checks:
  1. flashes: a shot shorter than 0.5 s between two hard cuts (a cut = mean frame change > 40 on a 108x192 thumbnail);
  2. black: frames where more than 15% of the picture is flat black (dark, textureless 4x4 blocks: an empty background, not the
     textured ink of a print), outside the first and last 0.2 s;
  3. host shots: every host section (datos_ae.json) stays on screen at least 1.2 s before a cut;
  4. the type wall behind the head moves like the reference (normalised motion 0.18-0.45 in the top-left corner of host shots;
     Bosch measures 0.24-0.36; the raw loop 0.54 is too fast, ~0 means it is not playing).
Writes qa_cortes.json; exit 1 when a check fails.
Usage: python qa_cortes.py <project> [video]"""
import json, sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from comun import ultimo_render  # noqa: E402

carpeta = Path(sys.argv[1]).resolve()
pj = json.loads((carpeta / "proyecto.json").read_text(encoding="utf-8"))
video = Path(sys.argv[2]) if len(sys.argv) > 2 else ultimo_render(carpeta, pj["slug"])
datos = json.loads((carpeta / "datos_ae.json").read_text(encoding="utf-8"))
# news/reaction format (build_reaccion_ae.py): no host sections over a type wall; the head floats over the footage plans,
# so checks 3-4 do not apply and the plan lengths are checked instead (review A08 v1: "no scene under ~1.5 s")
REACCION = "secciones" not in datos and "planos" in datos
datos.setdefault("secciones", [])
cap = cv2.VideoCapture(str(video)); fps = cap.get(cv2.CAP_PROP_FPS) or 30
G, C = [], []
while True:
    ok, f = cap.read()
    if not ok:
        break
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    G.append(cv2.resize(g, (108, 192)).astype(np.float32))
    C.append(f[60:500, 0:220].copy())
n = len(G); dur = n / fps
dif = np.array([0.0] + [float(np.abs(G[k] - G[k - 1]).mean()) for k in range(1, n)])
# a cut is an isolated spike: a slide or a fast move changes many frames in a row and is not a cut
cortes = [k / fps for k in range(1, n) if dif[k] > 40 and dif[k - 1] < 0.5 * dif[k] and (k + 1 >= n or dif[k + 1] < 0.5 * dif[k])]
fallos, avisos = [], []
# 1. flashes
for a, b in zip(cortes, cortes[1:]):
    if b - a < 0.5:
        fallos.append(f"flash: a {b - a:.2f} s shot between cuts at {a:.2f} and {b:.2f} s")
# checks 2 and 4 belong to styles with a type wall behind the host (CCC); a dark VHS style (Cult Pixel) has flat black on purpose
CCC = bool(datos.get("type_wall"))
# 2. black areas
negros = []
for k in (range(n) if CCC else []):
    t = k / fps
    if t < 0.2 or t > dur - 0.2:
        continue
    # flat black (an empty background: dark AND textureless 4x4 blocks), not the textured black ink of a print
    b = G[k].reshape(48, 4, 27, 4)
    plano = (b.mean(axis=(1, 3)) < 14) & (b.std(axis=(1, 3)) < 1.5)
    if plano.mean() > 0.15:
        negros.append(round(t, 2))
if negros:
    tramos, ini = [], negros[0]
    for x, y in zip(negros, negros[1:] + [None]):
        if y is None or y - x > 0.05:
            tramos.append((ini, x)); ini = y
    for a, b in tramos:
        if b - a < 0.25:     # a print's solid ink flickers in and out as it moves; an empty background stays
            continue
        sec = next((x for x in datos["secciones"] if x["ini"] <= (a + b) / 2 < x["fin"]), {})
        # inside a host line, after its first internal cut, the picture is a work (a print's solid ink): a warning to look at
        dentro = [c for c in cortes if sec.get("ini", 0) + 0.05 < c < sec.get("fin", 0) - 0.05] if sec.get("tipo") in ("gancho", "cabeza") else []
        destino = avisos if dentro and a >= dentro[0] - 0.05 else fallos
        destino.append(f"flat black background >15% of the frame {a:.2f}-{b:.2f} s ({sec.get('tipo', '?')}{', inside a work shot' if destino is avisos else ''})")
# 3. host shots on screen at least 1.2 s before a cut
for s in datos["secciones"]:
    if s.get("tipo") not in ("gancho", "cabeza"):
        continue
    dentro = [c for c in cortes if s["ini"] + 0.05 < c < s["fin"] - 0.05]
    primero = dentro[0] if dentro else s["fin"]
    if primero - s["ini"] < 1.2:
        fallos.append(f"host {s['id']} cut after {primero - s['ini']:.2f} s (min 1.2)")
# 3b. the host is on screen in his sections (Cult ep08 v2: a stale matte left two host lines as an empty dark frame and every
# other check passed): the middle of the frame, sampled every 0.5 s outside evidence cuts, must not be near black
for s in datos["secciones"]:
    if s.get("tipo") not in ("gancho", "cabeza"):
        continue
    ks = [int(t * fps) for t in np.arange(s["ini"] + 0.2, min(s["fin"], s["ini"] + 1.2), 0.25) if int(t * fps) < n]
    if ks and max(float(G[k][50:130, 24:84].mean()) for k in ks) < 18:
        fallos.append(f"host {s['id']}: no narrator on screen at {s['ini']:.2f} s (the middle of the frame is near black)")
# 4. type wall motion in host shots (first second of each host section, before any punch-in)
mov = []
for s in datos["secciones"]:
    if s.get("tipo") not in ("gancho", "cabeza"):
        continue
    k0, k1 = int((s["ini"] + 0.25) * fps), int(min(s["fin"], s["ini"] + 1.2) * fps)
    d, sd = [], []
    for k in range(k0 + 1, min(k1, n)):
        a = cv2.cvtColor(C[k], cv2.COLOR_BGR2GRAY).astype(np.float32); b = cv2.cvtColor(C[k - 1], cv2.COLOR_BGR2GRAY).astype(np.float32)
        d.append(np.abs(a - b).mean()); sd.append(a.std())
    if d and np.mean(sd) > 1:
        mov.append(float(np.mean(d) / np.mean(sd)))
m = float(np.mean(mov)) if mov else 0.0
if CCC and not 0.18 <= m <= 0.45:
    fallos.append(f"type wall motion {m:.2f} outside 0.18-0.45 (reference 0.24-0.36)")
if REACCION:
    pl = sorted(datos["planos"], key=lambda x: x["ini"])
    for i, x in enumerate(pl):
        largo = x["fin"] - x["ini"]
        if largo < 1.5 and not (i == len(pl) - 1 and x["fin"] >= datos.get("total", dur) - 0.05 and largo >= 1.0):
            fallos.append(f"plan {i + 1} at {x['ini']:.2f} s lasts {largo:.2f} s (min 1.5): {Path(x['src']).name}")
    # a cut inside a plan is an edit inside the source clip itself: it must not leave a sliver
    bordes = [x["ini"] for x in pl] + [pl[-1]["fin"]] if pl else []
    propios = [c for c in cortes if all(abs(c - b) > 0.08 for b in bordes)]
    for c in propios:
        x = next((q for q in pl if q["ini"] <= c < q["fin"]), None)
        if x:
            antes, despues = c - max([x["ini"]] + [d for d in propios if d < c]), min([x["fin"]] + [d for d in propios if d > c]) - c
            if min(antes, despues) < 1.0:
                avisos.append(f"edit inside the source clip at {c:.2f} s leaves {min(antes, despues):.2f} s: {Path(x['src']).name}")
if dur <= 0:
    fallos.append(f"{video.name} missing or empty: nothing was checked")
res = {"video": video.name, "duracion_s": round(dur, 2), "cortes": len(cortes), "muro_movimiento": round(m, 3), "fallos": fallos, "avisos": avisos, "ok": not fallos}
(carpeta / "qa_cortes.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
sys.exit(0 if not fallos else 1)
