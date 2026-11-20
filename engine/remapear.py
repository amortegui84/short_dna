"""After the voice track changes (a line re-cut, tighter gaps, a pause cut), move every time in reaccion.json with the words:
old and new Whisper words are matched in order and each time is interpolated between its nearest matched words (CCC rule
2026-11-17: never shift times by hand). Moves planos, tarjetas, titulo, host grande / fuera_manual and duracion; host
clips are rewritten after by reaccion_voz.py --slots.
Usage: python remapear.py <project> <old palabras_reaccion.json>"""
import bisect, difflib, json, re, sys
from pathlib import Path

carpeta = Path(sys.argv[1]).resolve()
old = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
new = json.loads((carpeta / "vo" / "palabras_reaccion.json").read_text(encoding="utf-8"))
norm = lambda w: re.sub(r"[^a-z0-9]", "", w[0].lower())
sm = difflib.SequenceMatcher(None, [norm(w) for w in old], [norm(w) for w in new], autojunk=False)
pares = {0.0: 0.0}
for a, b, n in sm.get_matching_blocks():
    for k in range(n):
        pares[old[a + k][1]] = new[b + k][1]; pares[old[a + k][2]] = new[b + k][2]
xs = sorted(pares); ys = [pares[x] for x in xs]
for i in range(1, len(ys)):   # monotonic
    ys[i] = max(ys[i], ys[i - 1])


def m(t):
    i = bisect.bisect_right(xs, t) - 1
    if i >= len(xs) - 1:
        return round(ys[-1] + (t - xs[-1]), 3)
    x0, x1, y0, y1 = xs[i], xs[i + 1], ys[i], ys[i + 1]
    return round(y0 + (t - x0) * (y1 - y0) / max(x1 - x0, 1e-6), 3)


rp = carpeta / "reaccion.json"; R = json.loads(rp.read_text(encoding="utf-8"))
for p in R.get("planos", []):
    p["ini"], p["fin"] = m(p["ini"]), m(p["fin"])
for t in R.get("tarjetas", []):
    t["ini"], t["fin"] = m(t["ini"]), m(t["fin"])
if R.get("titulo"):
    for k in ("desde", "hasta"):
        if k in R["titulo"]:
            R["titulo"][k] = m(R["titulo"][k])
h = R.get("host", {})
for k in ("grande", "fuera_manual"):
    if k in h:
        h[k] = [[m(a), m(b)] for a, b in h[k]]
if R.get("duracion"):
    R["duracion"] = m(R["duracion"])
rp.write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"remapped with {len(xs)} anchors | duration {R.get('duracion')}")
