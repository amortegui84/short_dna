"""Script QA before anything is generated: the general variety formula (docs/templates/variedad.md), for any brand and topic.
Checks a project's proyecto.json against the brand's episodios.json:
  1. "variacion" is filled (gancho, orden, tono, final, presentador) with known keys;
  2. the combination gancho + orden + tono + final repeats none of the last 4 episodes;
  3. gancho and final differ from the previous episode's (and are not the spent template defaults);
  4. no spent phrase in any line (said text and the TTS text);
  5. the order is wired: "revelacion" needs "ficha_en" on a late B line, "cita_primero" puts the quote second, "en_frio"
     starts on a B line, "mudo" has no spoken call to action;
  6. length: 120-160 words (about 55-65 s at the host's pace), research.md exists.
Prints the result and exits 1 when a check fails. --registrar adds the episode to episodios.json once it passes.
Usage: python qa_guion.py <project> [--registrar]"""
import json, re, sys
from pathlib import Path

carpeta = Path(sys.argv[1]).resolve()
pj = json.loads((carpeta / "proyecto.json").read_text(encoding="utf-8"))
reg_p = carpeta.parent.parent / "episodios.json"
reg = json.loads(reg_p.read_text(encoding="utf-8")) if reg_p.exists() else {"episodios": []}
eps = [e for e in reg["episodios"] if e.get("ep") != f"{pj.get('numero', 0):02d}"]

# the general keys (docs/templates/variedad.md); the template's original hook and ending ('dato_raro', 'debate') are allowed
# but count as spent, so they can never come twice in a row
CLAVES = {"gancho": {"numero", "orden", "voz_artista", "pregunta", "error", "en_frio", "dato_raro"},
          "orden": {"clasico", "revelacion", "cita_primero", "detalle_primero"},
          "tono": {"chisme", "detective", "seco", "asombro", "defensa"},
          "final": {"giro", "callback", "reto", "cliffhanger", "sobre_ti", "mudo", "debate"}}
# the brand's own settings: brand.json -> "variedad": {"gastadas": [...], "presentadores": [...], "palabras": [min, max]}
_marca = carpeta.parent.parent / "brand.json"
VAR = (json.loads(_marca.read_text(encoding="utf-8")).get("variedad") if _marca.exists() else None) or {}
GASTADAS = [g.lower() for g in VAR.get("gastadas", [])]
PRESENTADORES = set(VAR.get("presentadores", []))
if PRESENTADORES:
    CLAVES["presentador"] = PRESENTADORES
PMIN, PMAX = VAR.get("palabras", [120, 160])

fallos, avisos = [], []
v = pj.get("variacion") or {}
for k, ok in CLAVES.items():
    if v.get(k) not in ok:
        fallos.append(f"variacion.{k} = {v.get(k)!r}, expected one of {sorted(ok)}")
combo = tuple(v.get(k) for k in ("gancho", "orden", "tono", "final"))
for e in eps[-4:]:
    if combo == tuple(e.get(k) for k in ("gancho", "orden", "tono", "final")):
        fallos.append(f"the combination {combo} repeats episode {e['ep']} ({e['artista']})")
if eps:
    prev = eps[-1]
    for k in ("gancho", "final"):
        if v.get(k) == prev.get(k):
            fallos.append(f"{k} '{v.get(k)}' is the same as the previous episode ({prev['artista']})")
# the same tone three times in a row is allowed by the rules, but worth a look
if len(eps) >= 2 and all(e.get("tono") == v.get("tono") for e in eps[-2:]):
    avisos.append(f"tone '{v.get('tono')}' for the third episode in a row")

lineas = pj.get("lineas", [])
for ln in lineas:
    for campo in ("texto", "tts"):
        t = re.sub(r"\[[^\]]+\]", "", ln.get(campo, "")).lower().replace("’", "'")
        for g in GASTADAS:
            if g in t:
                fallos.append(f"{ln['id']} {campo}: spent phrase \"{g}\"")

ids = [l["id"] for l in lineas]
tipo = {l["id"]: l["tipo"] for l in lineas}
cita = next((l["id"] for l in lineas if l.get("obras") == ["__cita__"]), None)
if v.get("orden") == "revelacion":
    f = pj.get("ficha_en")
    if not f or tipo.get(f) != "B" or ids.index(f) < 4:
        fallos.append("reveal order: 'ficha_en' must name a B line from the 5th line on")
if v.get("orden") == "cita_primero" and (not cita or ids.index(cita) > 2):
    fallos.append("quote-first order: the __cita__ line must be the 2nd or 3rd line")
if v.get("gancho") == "en_frio" and lineas and lineas[0]["tipo"] != "B":
    fallos.append("cold open: L01 must be a B line (voice over the work)")
if v.get("final") == "mudo" and lineas and re.search(r"comment|below|tell me", lineas[-1]["texto"], re.I):
    fallos.append("silent ending: the last line must not ask for comments (the button does it)")
if not cita:
    avisos.append("no quote card in this script")

palabras = sum(len(l["texto"].split()) for l in lineas)
if not PMIN <= palabras <= PMAX:
    fallos.append(f"{palabras} words (the brand's range is {PMIN}-{PMAX})")
if not (carpeta / "research.md").exists():
    fallos.append("research.md missing (every fact needs its source)")

res = {"proyecto": pj.get("slug"), "variacion": v, "palabras": palabras, "fallos": fallos, "avisos": avisos, "ok": not fallos}
print(json.dumps(res, ensure_ascii=False, indent=1))
if not fallos and "--registrar" in sys.argv:
    reg["episodios"] = eps + [{"ep": f"{pj.get('numero', 0):02d}", "artista": pj.get("artista"), "estado": "script approved", **v}]
    reg_p.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    print("registered in", reg_p)
sys.exit(0 if not fallos else 1)
