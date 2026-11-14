"""Episode planner: combines the story library (library/historia/historia.json) and the shot library (library/tomas/tomas.json)
into a plan for one episode, inside the viral ranges and without repeating the brand's last episodes (review 2026-11-12: "a
library and a method to combine all this intelligently, variations inside the viral ranges: how the story is told, the cuts,
the information").

Input, in proyecto.json:
  "historia": {"naturaleza": "<one of historia.json naturalezas>", "estado": "unsolved|solved_strange|debunked|disputed",
               "flags": ["object", "number", "quote_verified", "timeline", "myth_layer", "two_threads", "official_record",
                         "identity_twist", "theories", "searchable_detail"]}
History: brands/<brand>/episodios.json entries that carry "plan" (written by qa_guion --registrar).
  python plan_episodio.py <project> [--seed N] [--dur 72]   writes proyecto.json "plan" and prints it
The plan names hook, structure (beats in seconds), tone (+ voice tags), ending, 3-5 devices (one key, at most one big), edit
pattern, music, the energy per beat and, per beat, the shot categories that fit its energy. The script is then written to it."""
import argparse, json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
H = json.loads((ROOT / "library" / "historia" / "historia.json").read_text(encoding="utf-8"))
TOMAS_P = ROOT / "library" / "tomas" / "tomas.json"

ap = argparse.ArgumentParser(); ap.add_argument("carpeta"); ap.add_argument("--seed", type=int); ap.add_argument("--dur", type=float, default=72)
a = ap.parse_args()
carpeta = Path(a.carpeta).resolve()
pj = json.loads((carpeta / "proyecto.json").read_text(encoding="utf-8"))
hist = pj.get("historia") or {}
nat, flags = hist.get("naturaleza"), set(hist.get("flags", []))
if nat not in H["naturalezas"]:
    raise SystemExit(f"proyecto.json historia.naturaleza must be one of {H['naturalezas']}")
reg_p = carpeta.parent.parent / "episodios.json"
eps = [e for e in (json.loads(reg_p.read_text(encoding="utf-8"))["episodios"] if reg_p.exists() else []) if e.get("plan")]
eps = [e for e in eps if e.get("ep") != f"{pj.get('numero', 0):02d}"][-H["anti_repeticion"]["ventana"]:]
rng = random.Random(a.seed if a.seed is not None else hash(pj.get("slug")) & 0xFFFF)
pref = H["por_naturaleza"].get(nat, {})


def ok(item):
    return ("*" in item.get("fits", ["*"]) or nat in item.get("fits", [])) and set(item.get("requires", [])) <= flags


def reciente(clave, iid, n):
    return any(e["plan"].get(clave) == iid for e in eps[-n:]) if n else False


def elegir(lista, clave, natural):
    cand = [x for x in lista if ok(x) and not reciente(clave, x["id"], x.get("cooldown", 2))]
    if not cand:
        cand = [x for x in lista if ok(x)] or lista
    def score(x):
        s = 1.0 + (2.0 if x["id"] in natural else 0.0)
        for age, e in enumerate(reversed(eps), 1):
            if e["plan"].get(clave) == x["id"]:
                s -= 1.0 / age
        return s
    top = sorted(cand, key=score, reverse=True)[:5]
    pesos = [max(0.1, score(x)) for x in top]
    return rng.choices(top, weights=pesos)[0]


for intento in range(200):
    est = elegir(H["estructuras"], "estructura", pref.get("estructuras", []))
    gan = elegir(H["ganchos"], "gancho", pref.get("ganchos", []))
    tonos = [t for t in H["tonos"] if (not t.get("solo_con") or est["id"] in t["solo_con"]) and set(t.get("requires", [])) <= flags]
    ton = elegir(tonos, "tono", [])
    fins = [f for f in H["finales"] if f["id"] not in ton.get("nunca_con", []) and (not f.get("requires_estructura") or est["id"] in f["requires_estructura"])]
    fin = elegir(fins, "final", pref.get("finales", []))
    edi = elegir(H["edicion"], "edicion", pref.get("edicion", []))
    combo = {"estructura": est["id"], "gancho": gan["id"], "tono": ton["id"], "final": fin["id"], "edicion": edi["id"]}
    seguidos = [e["plan"].get("tono") for e in eps[-H["anti_repeticion"]["tono_seguidos_max"]:]]
    if seguidos and all(t == ton["id"] for t in seguidos) and len(seguidos) >= H["anti_repeticion"]["tono_seguidos_max"]:
        continue
    if all(sum(combo[k] != e["plan"].get(k) for k in combo) >= H["anti_repeticion"]["distancia_min"] for e in eps):
        break
else:
    raise SystemExit("no combination far enough from the last episodes: widen the story flags or the library")

clave = [d for d in H["recursos"] if d.get("clave")]
grande = [d for d in H["recursos"] if d.get("grande")]
resto = [d for d in H["recursos"] if not d.get("clave") and not d.get("grande")]
recursos = [rng.choice(clave), rng.choice(grande)] + rng.sample(resto, rng.randint(1, 3))

dur = a.dur
beats = [{"rol": r, "ini_s": round(dur * s / 100, 1), "fin_s": round(dur * e / 100, 1), "energia": en}
         for (r, s, e), en in zip(est["beats"], est["energia"])]
tomas = json.loads(TOMAS_P.read_text(encoding="utf-8"))["tomas"] if TOMAS_P.exists() else []
for b in beats:
    cats = sorted({t["categoria"] for t in tomas if abs(t["energia"] - b["energia"]) <= 1})
    b["categorias_toma"] = cats
plan = {**combo, "naturaleza": nat, "recursos": [d["id"] for d in recursos], "musica": pref.get("musica", ""),
        "voz_tags": ton.get("voz_tags", []), "beats": beats,
        "nombres": {"estructura": est["nombre"], "gancho": gan["nombre"], "tono": ton["nombre"], "final": fin["nombre"], "edicion": edi["nombre"],
                    "recursos": [d["nombre"] for d in recursos]},
        "gancho_formula": gan["formula"], "rangos": H["rangos_virales"]}
pj["plan"] = plan
(carpeta / "proyecto.json").write_text(json.dumps(pj, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: plan[k] for k in ("nombres", "musica", "voz_tags")}, indent=1, ensure_ascii=False))
for b in beats:
    print(f"  {b['ini_s']:5.1f}-{b['fin_s']:5.1f}s  e{b['energia']}  {b['rol']:22s} shots: {', '.join(b['categorias_toma'][:5])}")
