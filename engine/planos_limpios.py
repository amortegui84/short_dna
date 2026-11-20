"""Clean footage plans for the news/reaction format (QA 2026-11-19: N04 v1 had five 0.2-0.47 s flashes, N01 v3 two; review A08 v1:
"it appears for a split second, that must not be"). A news clip has its own edits inside; a plan whose range crosses one shows a
sliver of the other shot. For every plan in reaccion.json:
  1. finds the source clip's own cuts (ffmpeg scene score > 0.30, cached in material/.../<clip>.cortes.json);
  2. if a cut falls inside the plan's range, moves `desde` the least possible so the whole range sits inside ONE source shot,
     preferring the shot that held most of the original range (keeps the subject that was chosen);
  3. a plan under 1.5 s (rule: no scene under ~1.5 s) is merged into the neighbour from the same voice line (the longer one
     grows over it); the last plan may be 1.0 s.
Prints every change; with --aplicar writes reaccion.json (the old one goes to reaccion.antes_limpios.json).
Usage: python planos_limpios.py <project> [--aplicar]"""
import json, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import duracion  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); aplicar = "--aplicar" in sys.argv
R = json.loads((carpeta / "reaccion.json").read_text(encoding="utf-8"))
MIN = 1.5


def cortes(src):
    cache = src.with_name(src.stem + ".cortes.json")
    if cache.exists() and cache.stat().st_mtime >= src.stat().st_mtime:
        return json.loads(cache.read_text())
    err = subprocess.run(["ffmpeg", "-i", str(src), "-vf", "scale=320:-2,select='gt(scene,0.30)',showinfo", "-an", "-f", "null", "-"],
                         capture_output=True, text=True, errors="replace").stderr
    c = [round(float(x), 3) for x in re.findall(r"pts_time:([\d.]+)", err)]
    cache.write_text(json.dumps(c))
    return c


def cortes_ventana(src, foco_x, a, b):
    """QA 2026-11-19 (N01 v4 36.9 s, N06 v2 19.7 s): a mosaic or handheld source cuts inside the 9:16 window we show while the
    whole frame barely changes (score < 0.30). Cuts are also measured on the visible window (full height, 9:16 wide, centred on
    the plan's foco), at 0.15, over [a - 4, b + 4] s of the source. Cached per clip, window and span."""
    a0 = max(0.0, a - 4.0); dur = (b + 4.0) - a0
    cache = src.with_name(f"{src.stem}.cortes_v{int(round(foco_x * 100))}_{int(a0 * 10)}_{int(dur * 10)}.json")
    if cache.exists() and cache.stat().st_mtime >= src.stat().st_mtime:
        return json.loads(cache.read_text())
    vf = (f"crop='min(iw,ih*9/16)':ih:'max(0,min(iw-min(iw,ih*9/16),{foco_x}*iw-min(iw,ih*9/16)/2))':0,"
          f"scale=180:-2,select='gt(scene,0.15)',showinfo")
    err = subprocess.run(["ffmpeg", "-ss", f"{a0:.3f}", "-t", f"{dur:.3f}", "-i", str(src), "-vf", vf, "-an", "-f", "null", "-"],
                         capture_output=True, text=True, errors="replace").stderr
    c = [round(float(x) + a0, 3) for x in re.findall(r"pts_time:([\d.]+)", err)]
    cache.write_text(json.dumps(c))
    return c


def _tomas(src):
    d = duracion(src); c = [0.0] + cortes(src) + [d]
    return [(c[i], c[i + 1]) for i in range(len(c) - 1)]


planos = sorted(R["planos"], key=lambda p: p["ini"])
cambios = []
# 3. merge short plans first (their time goes to a neighbour), then 2. clean each range
i = 0
while i < len(planos):
    p = planos[i]; largo = p["fin"] - p["ini"]
    ultimo = i == len(planos) - 1
    if largo < MIN and not (ultimo and largo >= 1.0) and len(planos) > 1:
        prev = planos[i - 1] if i else None; nxt = planos[i + 1] if not ultimo else None
        dueno = max([q for q in (prev, nxt) if q], key=lambda q: q["fin"] - q["ini"])
        if dueno is prev:
            prev["fin"] = p["fin"]
        else:
            corr = nxt["ini"] - p["ini"]
            nxt["desde"] = max(0.0, nxt.get("desde", 0.0) - corr * nxt.get("vel", 1.0)); nxt["ini"] = p["ini"]
        cambios.append(f"plan at {p['ini']:.2f} s ({largo:.2f} s, {Path(p['src']).stem}) merged into the {'previous' if dueno is prev else 'next'} plan")
        planos.pop(i)
        continue
    i += 1
for p in planos:
    src = (carpeta / p["src"]).resolve()
    if not src.exists():
        cambios.append(f"MISSING {p['src']}"); continue
    if src.suffix.lower() not in (".mp4", ".mov", ".webm", ".mkv", ".m4v"):
        continue   # a still has no cuts of its own
    v = p.get("vel", 1.0); largo = (p["fin"] - p["ini"]) * v; a = p.get("desde", 0.0); b = a + largo
    cs = sorted(set(cortes(src)) | set(cortes_ventana(src, p.get("foco", [0.5, 0.5])[0], a, b))); dsrc = duracion(src)

    def astilla(x):   # shortest piece the source's own cuts leave inside [x, x + largo], in screen seconds
        # a cut right at the edge (N06 v3: 0.04 s after the plan's start) leaves a one-frame flash: it counts too
        # and a cut just outside the range (< 0.06 s, two frames) is too close: frame rounding can still show it
        if any(x - 0.06 < c <= x + 0.005 or x + largo - 0.005 <= c < x + largo + 0.06 for c in cs):
            return 0.0
        dentro = [c for c in cs if x + 0.005 < c < x + largo - 0.005]
        if not dentro:
            return 99.0
        bordes = [x] + dentro + [x + largo]
        return min(bordes[k + 1] - bordes[k] for k in range(len(bordes) - 1)) / v
    if astilla(a) >= MIN:
        continue   # a source cut that leaves two real shots is a normal cut
    # the least shift (<= 3 s either way, inside the clip) that leaves no piece under 1.5 s keeps the chosen moment
    opciones = [round(a + k * 0.05, 2) for k in range(-60, 61)]
    opciones = [x for x in opciones if 0 <= x and x + largo <= dsrc - 0.05 and astilla(x) >= MIN]
    if not opciones:
        cambios.append(f"NO CLEAN RANGE within 3 s: plan at {p['ini']:.2f} s ({src.name} {a:.2f}-{b:.2f}) leaves a "
                       f"{astilla(a):.2f} s sliver: pick the moment by hand")
        continue
    nuevo = min(opciones, key=lambda x: abs(x - a))
    cambios.append(f"plan at {p['ini']:.2f} s: desde {a:.2f} -> {nuevo:.2f} (a {astilla(a):.2f} s sliver of another shot of {src.name})")
    p["desde"] = nuevo
print("\n".join(cambios) or "all plans clean")
if aplicar and cambios:
    (carpeta / "reaccion.antes_limpios.json").write_text((carpeta / "reaccion.json").read_text(encoding="utf-8"), encoding="utf-8")
    R["planos"] = planos
    (carpeta / "reaccion.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
    print("written reaccion.json")
