"""Reaction format: after the voice is re-timed (a slower ritmo_b, new TTS), move every hand-planned time of reaccion.json
to the new voice. Uses vo/tiempos_reaccion.antes_estirar.json (old line starts + "dur" of each vo/_lineas/Lxx.wav, saved
before montaje.py / reaccion_voz.py ran) and the new vo/tiempos_reaccion.json + vo/_lineas. Inside a line a time scales
with the line; in a gap it keeps its offset from the previous line's end; after the last line, from the voice's end.
Moves: planos ini/fin, tarjetas ini/fin, host grande, host fuera_manual (host clips, fuera and duracion come from
reaccion_voz.py --slots). Run planos_limpios.py afterwards: longer plans can now cross a source cut.
Usage: python reaccion_reescalar.py <project>   (writes reaccion.json; the old one stays in reaccion.antes_estirar.json)"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import duracion  # noqa: E402

carpeta = Path(sys.argv[1]).resolve()
A = json.loads((carpeta / "vo" / "tiempos_reaccion.antes_estirar.json").read_text(encoding="utf-8"))
N = json.loads((carpeta / "vo" / "tiempos_reaccion.json").read_text(encoding="utf-8"))
ids = sorted(A["ini"], key=lambda k: A["ini"][k])
nd = {lid: duracion(carpeta / "vo" / "_lineas" / f"{lid}.wav") for lid in ids}


def mapa(t):
    prev_fin_a, prev_fin_n = 0.0, 0.0
    for lid in ids:
        a0, a1 = A["ini"][lid], A["ini"][lid] + A["dur"][lid]
        n0, n1 = N["ini"][lid], N["ini"][lid] + nd[lid]
        if t < a0:   # in the gap before this line: keep the offset from the end of the previous line (or from 0)
            return round(prev_fin_n + (t - prev_fin_a) * ((n0 - prev_fin_n) / max(a0 - prev_fin_a, 1e-6)), 3)
        if t <= a1:
            return round(n0 + (t - a0) * (n1 - n0) / max(a1 - a0, 1e-6), 3)
        prev_fin_a, prev_fin_n = a1, n1
    return round(prev_fin_n + (t - prev_fin_a), 3)


rp = carpeta / "reaccion.json"
R = json.loads(rp.read_text(encoding="utf-8"))
for p in R["planos"] + R.get("tarjetas", []):
    p["ini"], p["fin"] = mapa(p["ini"]), mapa(p["fin"])
for k in ("grande", "fuera_manual"):
    R["host"][k] = [[mapa(a), mapa(b)] for a, b in R["host"].get(k, [])]
rp.write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
print("moved", len(R["planos"]), "plans,", len(R.get("tarjetas", [])), "cards | voice", A.get("fin"), "->", N.get("fin"), "s")
