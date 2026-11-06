"""Estimated cost BEFORE anything runs (the user's rule: in API mode, see the cost first).
  python costo.py proyecto <project> [--from STAGE] [--to STAGE]   -> per stage: provider, quantity, USD; total
  python costo.py asset <provider> [--n 1] [--seconds 5]           -> one asset
Prices: library/costs.json (edit them; unverified ones are flagged). Quantities come from the real script when it exists
(characters of the voice lines, seconds of talking lines, number of start frames), else from the template's typical use.
Prints JSON; the app shows it and asks before running; factory.py refuses paid stages without --yes."""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import CFG, LIB  # noqa: E402

C = json.loads((LIB / "costs.json").read_text(encoding="utf-8"))
P = C["proveedores"]; U = C["uso_tipico_artist_short"]
PROV = CFG.get("providers", {})


def precio(clave, cantidad):
    p = P.get(clave, {"usd": 0, "unidad": "?"})
    div = 1000 if p["unidad"].startswith("1000") else 1e6 if p["unidad"].startswith("1M") else 1
    return round(p["usd"] * cantidad / div, 3), p


def proyecto(carpeta, desde=None, hasta=None):
    carpeta = Path(carpeta)
    pj = json.loads((carpeta / "proyecto.json").read_text(encoding="utf-8")) if (carpeta / "proyecto.json").exists() else {}
    lineas = pj.get("lineas") or []
    chars = sum(len(l.get("tts", l.get("texto", ""))) for l in lineas) or U["caracteres_voz"]
    seg_a = sum(len(l.get("texto", "").split()) / 2.7 + 0.8 for l in lineas if l.get("tipo") == "A") or U["segundos_clips"]
    n_a = sum(1 for l in lineas if l.get("tipo") == "A") or 5
    filas = [
        ("inicios", PROV.get("image", "comfy_klein"), n_a, "images"),
        ("voz", "elevenlabs_tts" if PROV.get("voice", "elevenlabs") == "elevenlabs" else PROV.get("voice"), chars * U["tomas_voz"], "characters"),
        ("clips", PROV.get("video_talking", "comfy_h3"), seg_a * U["semillas_clips"], "seconds"),
        ("sts", "elevenlabs_sts", seg_a / 60, "minutes"),
        ("musica", {"comfy_ace": "comfy_ace", "suno": "suno"}.get(PROV.get("music", "comfy_ace"), PROV.get("music")), U["pistas_musica"], "tracks"),
        ("research+script", "claude", U["tokens_claude_M"] * 1e6, "tokens"),
    ]
    from_i = 0
    names = [f[0] for f in filas]
    out, total, sin_verificar = [], 0.0, []
    for st, prov, q, unidad in filas:
        if (carpeta / f".done_{st}").exists():
            continue
        usd, p = precio(prov, q)
        total += usd
        if usd and not p.get("verificado") and not p.get("local"):
            sin_verificar.append(prov)
        out.append({"etapa": st, "proveedor": prov, "cantidad": round(q, 1), "unidad": unidad, "usd": usd, "local": bool(p.get("local")),
                    "verificado": p.get("verificado")})
    return {"total_usd": round(total, 2), "filas": out, "precios_sin_verificar": sorted(set(sin_verificar)),
            "nota": "estimate from library/costs.json; real cost depends on plan, retries and seeds"}


ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
a1 = sub.add_parser("proyecto"); a1.add_argument("carpeta")
a2 = sub.add_parser("asset"); a2.add_argument("proveedor"); a2.add_argument("--n", type=float, default=1); a2.add_argument("--seconds", type=float, default=5)
a = ap.parse_args()
if a.cmd == "proyecto":
    print(json.dumps(proyecto(a.carpeta), ensure_ascii=False))
else:
    q = a.seconds * a.n if P.get(a.proveedor, {}).get("unidad", "").startswith("second") else a.n
    usd, p = precio(a.proveedor, q)
    print(json.dumps({"total_usd": usd, "proveedor": a.proveedor, "cantidad": q, "unidad": p.get("unidad"), "verificado": p.get("verificado"),
                      "local": bool(p.get("local")), "nota": p.get("nota", "")}, ensure_ascii=False))
