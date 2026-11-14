"""Reality QA: does every generated picture make sense? Generated images and clips drift into things that cannot exist: a
taxi with five doors and a seat inside a door, a car with no windshield and a roof that bends the wrong way, a hand with six
fingers, smoke crossing the narrator's mask, a sign in fake letters (review 2026-11-12, ep09: "the car looks very bad,
lots of hallucinations: check that it makes sense, body position, number of doors").

The script makes the review sheets; a person or Claude looks at them with the checklist below and records a verdict per item.
The factory stage "realidad" (before "musica"/"ae") passes only when every item is ok, so nothing reaches the edit unchecked.

  python qa_realidad.py <project>                       build qa_realidad/hoja_NN.jpg + items.json (keeps old verdicts)
  python qa_realidad.py <project> --ok ID [ID ...]      mark items fine
  python qa_realidad.py <project> --mal ID "what is wrong and the fix"
  python qa_realidad.py <project> --estado              list pending and bad items; exit 1 if any

Items: every evidence image (obras/), every start frame used (inicios/), the look, and three frames (start, middle, end) of
every narrator clip, continuation and the ending. Each card carries what it must show (the line or the image prompt), so the
check is against the story too (a "1970 two-door car" drawn with four doors fails).

CHECKLIST (look at each card for all of these):
 1. Vehicles: the number of doors fits the body (two-door coupe: 1 per side; sedan and 1970s taxi: 2 per side; pickup: 1),
    4 wheels on the ground with the same rims, a windshield with glass in front of the driver, the steering wheel in front
    of the driver (left side for the US), one continuous roof, the era and model asked for, no seat or part outside where it goes.
 2. Bodies: two arms, two legs, five fingers per hand, joints bending the right way, weight resting on something (no
    floating crouch), the pose physically possible from the camera position (a selfie arm reaches toward the lens). A shot from
    the 'imposible' category (library/tomas: balanced on a tip, tightrope, floating) breaks physics on purpose and calmly: there
    the impossible part is fine, but everything else in the frame must still obey physics.
 3. Objects: nothing fused, melted or half-made (a jug growing out of a steering wheel), nothing floating, real scale.
 4. Text: no fake letters or words on signs, screens, plates or papers (ask for "no letters" instead).
 5. The narrator: the mask intact (no mouth or nose), no smoke, mist, fog or vapour on or in front of him, gloves on.
 6. Light and space: light sources that exist in the shot, shadows that agree, a place that matches the line.
 7. Story: what the card says it must show is what is there (place, year, object, number of people).
 8. Crowds (library/tomas 'multitud' shots and any place with passers-by): every person has one head, two arms and two
    legs, nobody is fused with a neighbour or the narrator, nobody looks into the lens, clothes and cars fit the year,
    signs and billboards carry no letters or logos.
"""
import argparse, json, subprocess, sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from comun import escena_de, proyecto  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("carpeta")
ap.add_argument("--ok", nargs="+")
ap.add_argument("--mal", nargs=2, metavar=("ID", "NOTA"))
ap.add_argument("--estado", action="store_true")
a = ap.parse_args()
carpeta = Path(a.carpeta).resolve()
out = carpeta / "qa_realidad"; out.mkdir(exist_ok=True)
fitems = out / "items.json"
items = json.loads(fitems.read_text(encoding="utf-8")) if fitems.exists() else {}


def guardar():
    fitems.write_text(json.dumps(items, indent=1, ensure_ascii=False), encoding="utf-8")


def estado():
    malos = {k: v for k, v in items.items() if v["veredicto"] != "ok"}
    for k, v in malos.items():
        print(f"{v['veredicto']:9s} {k}: {v.get('nota', '')}")
    print(f"{len(items) - len(malos)}/{len(items)} ok")
    return 1 if malos or not items else 0


if a.ok or a.mal:
    for k in (a.ok or []) + ([a.mal[0]] if a.mal else []):
        if k not in items:
            sys.exit(f"no item {k} (build the sheets first)")
    for k in a.ok or []:
        items[k].update(veredicto="ok", nota="")
    if a.mal:
        items[a.mal[0]].update(veredicto="mal", nota=a.mal[1])
    guardar(); sys.exit(estado())
if a.estado:
    sys.exit(estado())

pj = proyecto(carpeta)
lineas = {l["id"]: l for l in pj["lineas"]}
vis = pj.get("visuales") or {}


def huella(p):
    s = p.stat(); return f"{s.st_size}-{int(s.st_mtime)}"


nuevos = {}   # id -> {archivo, debe, tipo}
for f in sorted((carpeta / "obras").glob("*.*")):
    if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
        nuevos[f"obra:{f.stem}"] = {"archivo": f, "debe": vis.get(f.stem, "evidence image (downloaded)"), "tipo": "img"}
look = escena_de(pj, carpeta)
nuevos[f"look:{look.stem}"] = {"archivo": look, "debe": "the episode's main narrator set", "tipo": "img"}
for lid, rel in sorted((pj.get("inicios") or {}).items()):
    f = carpeta / rel
    if f.exists():
        t = (lineas.get(lid) or {}).get("toma") or {}
        nuevos[f"inicio:{lid}"] = {"archivo": f, "debe": (lineas.get(lid) or {}).get("inicio") or t.get("lugar") or "narrator start frame", "tipo": "img"}
for f in sorted((carpeta / "clips").glob("L*.mp4")):
    if "_s2" in f.stem or f.stem.endswith("_full"):
        continue   # discarded seeds; _full is the clip and its continuation joined, both checked on their own
    lid = f.stem.split("_")[0]
    t = (lineas.get(lid) or {}).get("toma") or {}
    nuevos[f"clip:{f.stem}"] = {"archivo": f, "debe": f"{t.get('verbo', 'talks')} {t.get('lugar', 'in the main set')}: \"{(lineas.get(lid) or {}).get('texto', '')}\"", "tipo": "vid"}
fin = carpeta / "final" / "autodestruccion.mp4"
if fin.exists():
    nuevos["clip:final"] = {"archivo": fin, "debe": f"the ending ({pj.get('autodestruccion', '')})", "tipo": "vid"}

# a verdict stays only while the file is the same; a redrawn image or a new clip is checked again
for k, v in nuevos.items():
    h = huella(v["archivo"])
    if k in items and items[k].get("huella") == h:
        continue
    items[k] = {"archivo": str(v["archivo"]), "debe": v["debe"], "huella": h, "veredicto": "pendiente", "nota": ""}
for k in [k for k in items if k not in nuevos]:
    del items[k]


def cuadros(v):
    if v["tipo"] == "img":
        return [Image.open(v["archivo"]).convert("RGB")]
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v["archivo"])],
                             capture_output=True, text=True).stdout.strip() or 1)
    ims = []
    for i, t in enumerate((0.1, 0.5, 0.92)):
        tmp = out / f"_t{i}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{d * t:.2f}", "-i", str(v["archivo"]), "-frames:v", "1", str(tmp)], check=True)
        ims.append(Image.open(tmp).convert("RGB")); tmp.unlink()
    return ims


try:
    fuente = ImageFont.truetype("arial.ttf", 22); chica = ImageFont.truetype("arial.ttf", 17)
except OSError:
    fuente = chica = ImageFont.load_default()
ALTO, ANCHO_HOJA = 640, 2400
cartas = []
for k, v in items.items():
    ims = [im.resize((int(im.width * ALTO / im.height), ALTO)) for im in cuadros({"archivo": v["archivo"], "tipo": "vid" if v["archivo"].endswith(".mp4") else "img"})]
    ancho = max(560, sum(im.width for im in ims) + 6 * (len(ims) - 1))
    carta = Image.new("RGB", (ancho, ALTO + 110), (18, 18, 18))
    x = 0
    for im in ims:
        carta.paste(im, (x, 0)); x += im.width + 6
    dr = ImageDraw.Draw(carta)
    dr.text((8, ALTO + 6), f"{k}   [{v['veredicto']}]", fill=(255, 210, 80), font=fuente)
    debe, filas, n = "must show: " + v["debe"], [], max(40, ancho // 9)
    while debe and len(filas) < 3:
        filas.append(debe[:n]); debe = debe[n:]
    for i, f in enumerate(filas):
        dr.text((8, ALTO + 36 + 22 * i), f, fill=(220, 220, 220), font=chica)
    cartas.append(carta)
for f in out.glob("hoja_*.jpg"):
    f.unlink()
filas_h, fila, x = [], [], 0          # pack the cards in rows, two rows per sheet
for c in cartas:
    if fila and x + c.width > ANCHO_HOJA:
        filas_h.append(fila); fila, x = [], 0
    fila.append(c); x += c.width + 10
if fila:
    filas_h.append(fila)
for n in range(0, len(filas_h), 2):
    grupo = filas_h[n:n + 2]
    hoja = Image.new("RGB", (ANCHO_HOJA, (ALTO + 120) * len(grupo)), (0, 0, 0))
    for j, fila in enumerate(grupo):
        x = 0
        for c in fila:
            hoja.paste(c, (x, j * (ALTO + 120))); x += c.width + 10
    hoja.save(out / f"hoja_{n // 2 + 1:02d}.jpg", quality=85)
guardar()
print(f"{len(items)} items, {len(cartas)} cards in {out} (checklist: python qa_realidad.py --help)")
sys.exit(estado())
