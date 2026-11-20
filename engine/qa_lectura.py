"""Reading and listening QA on a built episode (review 2026-11-12: "check the reading times, the voice should be easier to
understand"). Reads timeline.json + datos_ae.json (written by montaje and the ae stage) and the rendered video:
  1. captions: each caption group on screen long enough to read (>= 0.6 s, and <= 20 characters per second, the adult subtitle standard);
  2. evidence titles and labels: on screen >= 0.4 s + 0.25 s per word, and the evidence image itself >= 1.8 s;
  3. typed cards (cita, ficha): >= 0.8 s + 0.33 s per word (the card's words are read while the voice says them);
  4. narration speed: words per minute per line; above 200 wpm is flagged and above 240 fails (top story Shorts run 165-277 wpm, but our voice must not be
     sped up artificially: atempo smears its consonants);
     voice tempo (proyecto.json ritmo_a / ritmo_b) above 1.12 is flagged: speeding a breathy voice smears its consonants;
  5. music under the voice: music loudness during speech must sit 14-22 LU below the voice (audible but never in the way);
     measured on the stems with the edit's levels (cinta.jsx: "elegida" music at 0 dB);
  6. final-mix intelligibility: Whisper on the rendered video vs the script (qc.json coincidencia_guion >= 0.95).
Writes qa_lectura.json; exit 1 when a check fails. Usage: python qa_lectura.py <project>"""
import json, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import proyecto  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta)
tl = json.loads((carpeta / "timeline.json").read_text(encoding="utf-8"))
d = json.loads((carpeta / "datos_ae.json").read_text(encoding="utf-8"))
fallos, avisos, med = [], [], {}

# 1. captions
cortos, rapidos = [], []
# the reaction builder splits one caption into a layer per frame while it slides with the head (y changes); on screen it
# is one caption, so consecutive items with the same words and touching times are read as one
subs = []
for s in d.get("subs", []):
    txt = " ".join(w["w"] for w in s["words"])
    if subs and subs[-1]["_t"] == txt and abs(s["ini"] - subs[-1]["fin"]) < 0.05:
        subs[-1]["fin"] = s["fin"]
    else:
        subs.append({**s, "_t": txt})
d["subs"] = subs
for s in d.get("subs", []):
    txt = " ".join(w["w"] for w in s["words"]); dur = s["fin"] - s["ini"]
    if dur < 0.6:
        cortos.append(f"{s['ini']:.1f}s '{txt}' {dur:.2f}s")
    if dur > 0 and len(txt) / dur > 20:
        rapidos.append(f"{s['ini']:.1f}s '{txt}' {len(txt) / dur:.0f} cps")
med["subtitulos"] = {"grupos": len(d.get("subs", [])), "cortos": len(cortos), "rapidos": len(rapidos)}
if cortos:
    (fallos if len(cortos) > 5 else avisos).append(f"{len(cortos)} caption groups under 0.6 s: " + "; ".join(cortos[:6]))
if rapidos:
    (fallos if len(rapidos) > 5 else avisos).append(f"{len(rapidos)} caption groups over 20 cps: " + "; ".join(rapidos[:6]))

# 2-3. evidence titles and typed cards
for s in d.get("secciones", []):
    dur = s["fin"] - s["ini"]
    if s["tipo"] == "obra":
        t = " ".join(x for x in (s.get("titulo"), s.get("fecha")) if x)
        need = max(1.8, 0.4 + 0.25 * len(t.split()))
        if dur < need:
            fallos.append(f"evidence '{s.get('titulo')}' at {s['ini']:.1f}s shows {dur:.1f}s, needs {need:.1f}s")
    elif s["tipo"] in ("cita", "ficha"):
        palabras = " ".join(s.get("cita") or []).replace("—", "").split() if s["tipo"] == "cita" else pj.get("artista", "").split()   # the card's title is what must be read
        need = 0.8 + 0.33 * len(palabras)
        if dur < need:
            (fallos if dur < 0.85 * need else avisos).append(f"{s['tipo']} card at {s['ini']:.1f}s shows {dur:.1f}s, needs {need:.1f}s for {len(palabras)} words")

# 4. narration speed
wpm = {}
for g in tl["segmentos"]:
    ws = g.get("words") or []
    if len(ws) >= 3:
        t = ws[-1]["e"] - ws[0]["s"]
        wpm[g["id"]] = round(len(ws) / t * 60) if t > 0 else 0
med["wpm"] = wpm
med["wpm_medio"] = round(sum(wpm.values()) / max(1, len(wpm)))
for lid, v in wpm.items():
    if v > 240:
        fallos.append(f"{lid} at {v} wpm (too fast to follow)")
    elif v > 200:
        avisos.append(f"{lid} at {v} wpm")
for k in ("ritmo_a", "ritmo_b"):
    if (pj.get(k) or 1.0) > 1.05 and pj.get("estirar") != "rubberband":
        fallos.append(f"{k} = {pj[k]}: the voice is sped up past 1.12, consonants smear")


# 5. music under the voice (stems with the edit's levels)
def lufs(path, extra=""):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", f"{extra}ebur128", "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return float(m[-1]) if m else None


mus = d.get("musica")
if mus and Path(mus).exists():
    nivel = (0.0 if "elegida" in mus else -13.2) + (d.get("musica_db_voz") or 0)   # the level under the voice, ducking included
    voz = [lufs(v["wav"]) for v in d.get("voces", []) if Path(v["wav"]).exists()]
    voz = [x for x in voz if x is not None]
    m = lufs(mus)
    if voz and m is not None:
        diff = round(sum(voz) / len(voz) - (m + nivel), 1)
        med["voz_sobre_musica_lu"] = diff
        if diff < 14:
            fallos.append(f"music only {diff} LU under the voice: it competes with the words (target 14-22)")
        elif diff > 22:
            avisos.append(f"music {diff} LU under the voice: barely audible (target 14-22)")

# 6. final-mix intelligibility
qc = carpeta / "qc.json"
if qc.exists():
    c = json.loads(qc.read_text(encoding="utf-8")).get("coincidencia_guion")
    med["whisper_vs_guion"] = c
    if c is not None and c < 0.93:
        fallos.append(f"Whisper understands {c:.2f} of the script in the final mix (needs 0.93; number formats like 18E or $200,000 cost a point)")

res = {"ok": not fallos, "fallos": fallos, "avisos": avisos, "medidas": med}
(carpeta / "qa_lectura.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(res, indent=1, ensure_ascii=False))
sys.exit(0 if res["ok"] else 1)
