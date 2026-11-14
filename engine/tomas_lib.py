"""Dynamic shot library for talking lines (review 2026-11-12: "more dynamism and hook: he grabs the camera and turns it toward
himself, snaps his fingers, odd influencer / YouTuber angles, sometimes drinking coffee or holding something tied to the story").

library/tomas/tomas.json holds the shots: each one has a camera, a start-frame description and one physical action, with
{lugar} (the place of this line) and {prop} (an object tied to the story) slots, an energy level, the story beats it suits and
a risk note for AI video. A line in proyecto.json asks for a shot with
    "toma_lib": {"id": "<shot id>", "lugar": "<where he is>", "prop": "<object, optional>", "sonido": "<ambience, optional>"}
and this script expands it into the line's "toma" (lugar, verbo, camara, sonido), "inicio" (the start frame) and the action
part of "accion" / "direccion" that the clip stage already uses. Run it after writing the script (before inicios):
    python tomas_lib.py <project>            expand every line with toma_lib (keeps the line's emotion and words)
    python tomas_lib.py --list [category]    print the library
Checks (also in qa_guion when the brand sets "tomas_lib"): at least 4 different categories in an episode, never the same
category twice in a row, the first talking line at energy 3 or more."""
import json, sys
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "library" / "tomas" / "tomas.json"


def cargar():
    return {t["id"]: t for t in json.loads(LIB.read_text(encoding="utf-8"))["tomas"]}


def rellenar(texto, ln_t, corto=True):
    """{prop} is the full description in the start frame and the short one ("prop_corto") in camera and action text."""
    prop = (ln_t.get("prop_corto") if corto else None) or ln_t.get("prop") or "nothing in his hands"
    return texto.replace("{lugar}", ln_t.get("lugar", "the place")).replace("{prop}", prop)


def expandir(carpeta):
    p = Path(carpeta) / "proyecto.json"
    pj = json.loads(p.read_text(encoding="utf-8"))
    lib = cargar()
    usadas = []
    for ln in pj["lineas"]:
        tl = ln.get("toma_lib")
        if ln["tipo"] != "A" or not tl:
            continue
        t = lib[tl["id"]]
        usadas.append(t)
        ln["toma"] = {"lugar": tl["lugar"], "verbo": t["verbo"], "mesa": tl.get("prop"), "camara": rellenar(t["camara"], tl),
                      "sonido": tl.get("sonido", "quiet night ambience")}
        ln["inicio"] = rellenar(t["inicio"], tl, corto=False)
        # drawn from the master portrait alone: with the look as reference Klein copied the look's frontal composition and
        # ignored the shot's framing (ep13 test, 2026-11-12); the place comes from the text
        ln["inicio_solo_maestro"] = True
        d = ln.setdefault("direccion", {})
        d["entra"] = rellenar(t["entra"], tl)
        d["gesto"] = rellenar(t["gesto"], tl) + (f"; {tl['gesto_extra']}" if tl.get("gesto_extra") else "")
        d["sale"] = rellenar(t["sale"], tl)
        emo = d.get("emocion", "calm")
        ln["accion"] = (f"Emotion: {emo}. He starts {d['entra']}; {d['gesto']}; he ends {d['sale'].split(' (')[0]}. "
                        + t.get("reglas", "") + " He never points at the lens. He keeps his face toward the lens.").strip()
        pj.setdefault("continuacion", {})[ln["id"]] = rellenar(t.get("sigue", "he holds the last pose, very still, then looks back into the lens."), tl) + \
            " His hands keep exactly what they hold at the start and nothing else: no new object of any kind appears."
    p.write_text(json.dumps(pj, indent=1, ensure_ascii=False), encoding="utf-8")
    return usadas


def revisar(usadas):
    fallos = []
    cats = [t["categoria"] for t in usadas]
    if usadas and len(set(cats)) < min(4, len(usadas)):
        fallos.append(f"only {len(set(cats))} shot categories ({', '.join(sorted(set(cats)))}): use at least 4")
    for a, b in zip(cats, cats[1:]):
        if a == b:
            fallos.append(f"two '{a}' shots in a row")
    if usadas and usadas[0]["energia"] < 3:
        fallos.append(f"the first talking shot '{usadas[0]['id']}' has energy {usadas[0]['energia']}: open with 3 or more")
    return fallos


if __name__ == "__main__":
    if sys.argv[1] == "--list":
        cat = sys.argv[2] if len(sys.argv) > 2 else None
        for t in cargar().values():
            if not cat or t["categoria"] == cat:
                print(f"{t['id']:24s} {t['categoria']:12s} e{t['energia']} {', '.join(t['beats']):28s} {t['nombre']}")
        sys.exit(0)
    u = expandir(sys.argv[1])
    f = revisar(u)
    print(f"{len(u)} lines expanded:", ", ".join(t["id"] for t in u))
    for x in f:
        print("FAIL", x)
    sys.exit(1 if f else 0)
