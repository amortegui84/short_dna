"""A different start frame for every talking line (line type A), so no line opens on the same pose. Flux Klein with
<1> the video's look (proyecto.json "escena") and <2> the master portrait. The variants (frontal close-up, three-quarter
left, three-quarter right with surprise, wider shot with an open hand, head tilted with a low camera) live in
character.json "inicios_variantes". Writes <project>/inicios/iNN.png and fills proyecto.json "inicios" (line -> frame).
Face check afterwards: python qa_cara.py --ref <master> <project>/inicios/*.png (0.68-0.86 was fine with the head turned).
Usage: python inicios.py <project> [--seed-base 42000]"""
import argparse, json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import con_mesa, escena_de, personaje, proyecto  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("carpeta"); ap.add_argument("--seed-base", type=int, default=42000)
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
spec = out / "spec.json"
spec.write_text(json.dumps({"out_dir": str(out), "items": items}, indent=2), encoding="utf-8")
subprocess.run([sys.executable, str(Path(__file__).parent / "klein_gen.py"), "--spec", str(spec)], check=True)
lineas_a = [l["id"] for l in pj["lineas"] if l["tipo"] == "A"]
orden = [0, 1, 3, 2, 4]   # the hook opens frontal; then the sides alternate
pj["inicios"] = {lid: f"inicios/{items[orden[k % len(orden)] % len(items)]['name']}.png" for k, lid in enumerate(lineas_a)}
(carpeta / "proyecto.json").write_text(json.dumps(pj, indent=1, ensure_ascii=False), encoding="utf-8")
print("inicios:", pj["inicios"])
