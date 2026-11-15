"""Script QA before anything is generated: the general variety formula (docs/templates/variedad.md), for any brand and topic.
Checks a project's proyecto.json against the brand's episodios.json:
  1. "variacion" is filled (gancho, orden, tono, final, presentador) with known keys;
  2. the combination gancho + orden + tono + final repeats none of the last 4 episodes;
  3. gancho and final differ from the previous episode's (and are not the spent template defaults);
  4. no spent phrase in any line (said text and the TTS text);
  5. the order is wired: "revelacion" needs "ficha_en" on a late B line, "cita_primero" puts the quote second, "en_frio"
     starts on a B line, "mudo" has no spoken call to action;
  6. length in the brand's range, research.md exists;
  7. every host line has its acting direction (emocion, entra, gesto, sale).
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

# every host line carries its acting direction: emotion, how it starts (tied to the scene before), the gesture on its word,
# and how it ends (the pose the edit cuts on) -- review 2026-11-09: "context between scene and scene"
if VAR.get("direccion", True):
    for ln in lineas:
        if ln["tipo"] == "A":
            d = ln.get("direccion") or {}
            falta = [k for k in ("emocion", "entra", "gesto", "sale") if not d.get(k)]
            if falta:
                fallos.append(f"{ln['id']}: acting direction missing {', '.join(falta)}")
palabras = sum(len(l["texto"].split()) for l in lineas)
if not PMIN <= palabras <= PMAX:
    fallos.append(f"{palabras} words (the brand's range is {PMIN}-{PMAX})")
if not (carpeta / "research.md").exists():
    fallos.append("research.md missing (every fact needs its source)")
else:
    # depth and coherence (review 2026-11-12: "deep research, relevant facts, a coherent script"): a brand can ask for a
    # minimum of sources from different sites, and every number or year said in the script must be in research.md
    rs = (carpeta / "research.md").read_text(encoding="utf-8")
    urls = set(re.findall(r"https?://[^\s|)>\]]+", rs))
    dominios = {re.sub(r"^www\.", "", u.split("/")[2]) for u in urls}
    smin, dmin = VAR.get("fuentes_min", [0, 0])
    if len(urls) < smin or len(dominios) < dmin:
        fallos.append(f"research.md cites {len(urls)} sources from {len(dominios)} sites (the brand asks for {smin} from {dmin})")
    num = lambda t: {re.sub(r"[,\s]", "", n) for n in re.findall(r"\b\d[\d,]*(?:\.\d+)?\b", t)}
    pal_num = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
               "ten": "10", "twelve": "12", "thirteen": "13", "twenty": "20", "fifty": "50", "hundred": "100"}
    en_rs = num(rs) | {k for k, n in pal_num.items() if n in num(rs)}
    for ln in lineas:
        for n in sorted(num(ln["texto"])):
            if n not in en_rs:
                fallos.append(f"{ln['id']}: '{n}' is in the script but not in research.md (unsourced number)")
    # real media first: archival photos, documents, footage (Wikimedia Commons, government archives, newspapers in the public
    # domain) are more gripping than reconstructions; generated images fill only the gaps (review 2026-11-12)
    rmin = VAR.get("reales_min", 0)
    if rmin:
        reales = len(pj.get("obras_descarga") or []) + sum(len(d.get("paginas", {})) for d in pj.get("documentos", []))
        total_ev = reales + len(pj.get("visuales") or {})
        if total_ev and reales / total_ev < rmin and "## No real media" not in rs:
            fallos.append(f"{reales} of {total_ev} evidence images are real (the brand asks for {rmin:.0%}); find archival media or "
                          "explain in research.md under '## No real media' why none exists")
    if VAR.get("contexto") and lineas:
        # the first 4 lines place the story: a year and a place name (a capitalised word after in/at/near or a comma pair)
        cab = " ".join(l["texto"] for l in lineas[:4])
        if not re.search(r"\b1\d{3}\b|\b20\d{2}\b", cab):
            fallos.append("no year in the first 4 lines: the viewer needs to know when this happened")
        if not re.search(r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)*, [A-Z][a-z]+|\b(?:in|at|near|outside|from|to|over|off) [A-Z][a-z]+", cab):
            fallos.append("no place in the first 4 lines: the viewer needs to know where this happened")

# dynamic shots (library/tomas, engine/tomas_lib.py): variety of shot categories, a lively first talking shot
if VAR.get("tomas_lib"):
    import tomas_lib
    lib = tomas_lib.cargar()
    usadas = [lib[l["toma_lib"]["id"]] for l in lineas if l["tipo"] == "A" and l.get("toma_lib") and l["toma_lib"]["id"] in lib]
    if len(usadas) < sum(1 for l in lineas if l["tipo"] == "A") - 1:
        fallos.append("talking lines without a library shot (toma_lib): every narrator line but the main-set one picks a shot")
    fallos += tomas_lib.revisar(usadas)
    # storyteller voice text: whispers on 1-2 lines only, at most one CAPS word per line
    sus = sum("[whispers]" in l.get("tts", "") for l in lineas)
    if sus > 2:
        fallos.append(f"[whispers] on {sus} lines: keep the whisper drop for 1-2 lines so it lands")
    for l in lineas:
        caps = [w for w in re.findall(r"\b[A-Z]{3,}\b", re.sub(r"\[[^\]]+\]", "", l.get("tts", ""))) if w not in ("FBI", "UFO", "USA", "NASA", "CIA")]
        if len(caps) > 1:
            fallos.append(f"{l['id']}: {len(caps)} CAPS words in the voice text; one emphasis per line")

# ideas over data (review 2026-11-15: "too much data, few ideas that give people ideas; the script turned into only data"):
# few numbers, and at least two lines that hand the viewer a thought of their own (what it means, what if, what it says about us)
if VAR.get("ideas"):
    imax_l, imax_t, imin = VAR["ideas"] if isinstance(VAR["ideas"], list) else (2, 6, 2)
    pal = r"one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|twenty|thirty|forty|fifty|" \
          r"sixty|seventy|eighty|ninety|hundred|thousand|million|billion|first|second|third"
    cuenta = lambda t: len(re.findall(r"\b\d[\d,:.]*(?:st|nd|rd|th)?\b", t)) + len(re.findall(rf"\b(?:{pal})(?:[- ](?:{pal}))*\b", t, re.I))
    total = 0
    for ln in lineas:
        n = cuenta(ln["texto"]); total += n
        if n > imax_l:
            fallos.append(f"{ln['id']}: {n} numbers in one line (max {imax_l}); keep the one that matters, turn the rest into an image")
    if total > imax_t:
        fallos.append(f"{total} numbers in the script (max {imax_t}): it reads like a data sheet; trade numbers for ideas")
    ideas = [l for l in lineas if l.get("idea")]
    if len(ideas) < imin:
        fallos.append(f"{len(ideas)} idea lines (mark them \"idea\": true; at least {imin}): a thought the viewer keeps, not a fact")
    for l in ideas:
        if cuenta(l["texto"]):
            fallos.append(f"{l['id']}: an idea line carries no numbers")

res = {"proyecto": pj.get("slug"), "variacion": v, "palabras": palabras, "fallos": fallos, "avisos": avisos, "ok": not fallos}
print(json.dumps(res, ensure_ascii=False, indent=1))
if not fallos and "--registrar" in sys.argv:
    plan = {k: pj["plan"][k] for k in ("estructura", "gancho", "tono", "final", "edicion", "recursos") if k in (pj.get("plan") or {})}
    reg["episodios"] = eps + [{"ep": f"{pj.get('numero', 0):02d}", "artista": pj.get("artista"), "estado": "script approved", **v,
                               **({"plan": plan} if plan else {})}]
    reg_p.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    print("registered in", reg_p)
sys.exit(0 if not fallos else 1)
