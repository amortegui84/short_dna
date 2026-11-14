"""A different start frame for every talking line (line type A), so no line opens on the same pose. Flux Klein with
<1> the video's look (proyecto.json "escena") and <2> the master portrait. The variants (frontal close-up, three-quarter
left, three-quarter right with surprise, wider shot with an open hand, head tilted with a low camera) live in
character.json "inicios_variantes". Writes <project>/inicios/iNN.png and fills proyecto.json "inicios" (line -> frame).
Face check afterwards: python qa_cara.py --ref <master> <project>/inicios/*.png (0.68-0.86 was fine with the head turned).
Usage: python inicios.py <project> [--seed-base 42000]"""
import argparse, json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import con_mesa, escena_de, personaje, proyecto, sin_niebla, toma  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("carpeta"); ap.add_argument("--seed-base", type=int, default=42000)
ap.add_argument("--solo", nargs="+", help="redraw only these lines' own start frames (e.g. after the reality QA, qa_realidad.py)")
ap.add_argument("--seed-extra", type=int, default=0, help="added to the seed of a redrawn frame, to get a different draw")
a = ap.parse_args()
carpeta = Path(a.carpeta).resolve(); pj = proyecto(carpeta); c = personaje(pj)
out = carpeta / "inicios"; out.mkdir(exist_ok=True)
look = str(escena_de(pj, carpeta))
# the narrator never looks the same twice: an episode may bring its own poses (proyecto.json "inicios_variantes") and its
# own props on the table ("mesa", which replaces the candles everywhere: start frames, clips, ending)
var = pj.get("inicios_variantes") or c["inicios_variantes"]
fijo = con_mesa(c["inicios_fijo"], pj)
items = [{"name": f"i{i + 1:02d}", "refs": [look, str(c["_dir"] / c["maestro"])], "seed": a.seed_base + 10 * i, "size": "768x1344",
          "prompt": f"{con_mesa(p, pj)} {c['inicios_mirada']} {fijo}"} for i, p in enumerate(var)]
if not a.solo:
    spec = out / "spec.json"
    spec.write_text(json.dumps({"out_dir": str(out), "items": items}, indent=2), encoding="utf-8")
    subprocess.run([sys.executable, str(Path(__file__).parent / "klein_gen.py"), "--spec", str(spec)], check=True)
    lineas_a = [l["id"] for l in pj["lineas"] if l["tipo"] == "A"]
    orden = [0, 1, 3, 2, 4]   # the hook opens frontal; then the sides alternate
    pj["inicios"] = {lid: f"inicios/{items[orden[k % len(orden)] % len(items)]['name']}.png" for k, lid in enumerate(lineas_a)}
# a line with its own place ("toma") may bring its own start frame ("inicio"): drawn in that place, so the clip starts there
# instead of morphing out of the episode's main set (review 2026-11-10: "more variation in what he does")
propias = []
for l in pj["lineas"]:
    if l["tipo"] != "A" or not l.get("inicio") or (a.solo and l["id"] not in a.solo):
        continue
    fijo_l = toma(c["inicios_fijo"], pj, l["id"]).replace("and the room from the first reference image exactly",
                                                         "from the first reference image exactly; only the place and the framing change")
    # "inicio_solo_maestro": a shot inside the look's own place (in the car the look sits in) copied the look's framing,
    # so it is drawn from the master portrait alone (ep09 L06, 2026-11-12)
    refs = [str(c["_dir"] / c["maestro"])] if l.get("inicio_solo_maestro") else [look, str(c["_dir"] / c["maestro"])]
    propias.append({"name": f"t_{l['id'].lower()}", "refs": refs, "seed": a.seed_base + 500 + a.seed_extra + [x["id"] for x in pj["lineas"] if x.get("inicio")].index(l["id"]),
                    "size": "768x1344", "prompt": f"{sin_niebla(l['inicio'])} {c['inicios_mirada']} {fijo_l}"})
if a.solo:   # keep the old frames to compare
    for it in propias:
        f = out / f"{it['name']}.png"
        if f.exists():
            f.replace(out / f"{it['name']}_old.png")
if propias:
    spec2 = out / "spec_tomas.json"
    spec2.write_text(json.dumps({"out_dir": str(out), "items": propias}, indent=2), encoding="utf-8")
    subprocess.run([sys.executable, str(Path(__file__).parent / "klein_gen.py"), "--spec", str(spec2)], check=True)
    for it in propias:
        pj["inicios"][it["name"][2:].upper()] = f"inicios/{it['name']}.png"
(carpeta / "proyecto.json").write_text(json.dumps(pj, indent=1, ensure_ascii=False), encoding="utf-8")
print("inicios:", pj["inicios"])
