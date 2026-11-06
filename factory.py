"""shorts-factory: one command from a brief to a finished, collected Short.

  python factory.py stages                                   list the stages
  python factory.py brand-new <brand> --name "Cult Pixel" --handle cult_pixel [--platforms tiktok,instagram_reels]
  python factory.py new <slug> --brand <brand> --topic "Odilon Redon" [--template artist_short] [--character green_hair_presenter]
                        [--style collage_v10c] [--look 05_corse_camisa]
  python factory.py run <slug|folder> [--from STAGE] [--to STAGE] [--only STAGE] [--force]
  python factory.py status <slug|folder>
  python factory.py estimate <slug|folder>                  estimated USD of the remaining stages

A project is a folder brands/<brand>/proyectos/<slug> with proyecto.json (docs/PROJECT_SCHEMA.md). Every stage leaves a mark
.done_<stage>; run resumes where it stopped. The "creative" stages (research, script, design) are done by Claude with the
skill (.claude/skills/shorts-factory/SKILL.md) and the user; the factory checks their output and stops until it exists.
GPU stages run one at a time; if config "comfy_switch" is set, the factory switches ComfyUI (Klein for images, H3 for video
and music) before them."""
import argparse, json, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).parent
sys.path.insert(0, str(REPO / "engine"))
from comun import BRANDS, CFG, LIB, buscar, marca_dir  # noqa: E402

E = REPO / "engine"
# (name, kind, what it needs / does, command or check)
STAGES = [
    ("research", "claude", "research.md with facts and sources (docs/templates/research.md)", "research.md"),
    ("script", "claude", "proyecto.json lineas + momentos_a + obras_b + titulos + cita (docs/templates/script.md)", "lineas"),
    ("design", "claude", "optional: storyboard frames in Figma with the style tokens (docs/FIGMA.md); mark it done to skip", None),
    ("obras", "cpu", "download the public-domain artworks (obras_descarga)", ["obras.py"]),
    ("retrato", "gpu:h3", "cut out the artist portrait for the artist card", ["retrato.py"]),
    ("look", "check", "the character look exists (else: engine/looks.py with the user)", None),
    ("inicios", "gpu:klein", "a different start frame per talking line", ["inicios.py"]),
    ("voz", "api:voice", "voice-over lines with ElevenLabs v3 (3 takes, Whisper QC)", ["tts.py"]),
    ("clips", "gpu:h3", "talking clips with H3 (lipsync, QC by transcript, up to 3 seeds)", ["clips.py"]),
    ("sts", "api:voice", "H3 speech -> the video's voice with ElevenLabs speech-to-speech (exact lipsync)", ["sts.py"]),
    ("montaje", "cpu", "timeline: voice pace, holds, subtitles timing", ["montaje.py"]),
    ("mates", "gpu:h3", "cut-out of the presenter + face boxes", ["mates.py"]),
    ("musica", "gpu:h3", "music (ACE-Step locally; or the music provider)", ["musica.py"]),
    ("ae", "ae", "build the comp in After Effects with Motion DNA (sound, layout QA)", ["build_collage.py"]),
    ("render", "ae", "aerender + encode + QA (black frames, LUFS, motion)", ["render_ae.py"]),
    ("qc", "cpu", "transcript match, loudness, contact sheet", ["qc.py"]),
    ("collect", "ae", "light collect of the project + zip", ["collect.py"]),
]
NAMES = [s[0] for s in STAGES]


def carpeta_de(x):
    """A folder, "<brand>/<slug>", or a slug searched in every brand."""
    p = Path(x)
    if p.exists():
        return p.resolve()
    if "/" in x:
        b, sl = x.split("/", 1); return marca_dir(b) / "proyectos" / sl
    hits = list(BRANDS.glob(f"*/proyectos/{x}"))
    if not hits:
        sys.exit(f"no project {x} in {BRANDS}")
    return hits[0]


def gpu(kind, log):
    sw = CFG.get("comfy_switch")
    if not sw or not kind.startswith("gpu:"):
        return
    want = kind.split(":")[1]
    if gpu.actual != want:
        log.write(f"-- comfy_switch {want}\n"); log.flush()
        subprocess.run(["powershell", "-NoProfile", "-File", sw, want], check=True, stdout=log, stderr=subprocess.STDOUT)
        gpu.actual = want


gpu.actual = None


def check(name, carpeta, pj):
    if name == "research":
        return (carpeta / "research.md").exists()
    if name == "script":
        return bool(pj.get("lineas")) and all(l.get("texto") for l in pj["lineas"])
    if name == "look":
        c = json.loads((buscar("characters", pj["personaje"], pj.get("marca")) / "character.json").read_text(encoding="utf-8"))
        return not pj.get("look") or pj["look"] in c["looks"]
    return False


def run(args):
    carpeta = carpeta_de(args.proyecto)
    i0 = NAMES.index(args.only or args.desde or NAMES[0]); i1 = NAMES.index(args.only or args.hasta or NAMES[-1])
    # the user's rule: with paid providers, show the estimated cost first and run only after a yes
    est = json.loads(subprocess.run([sys.executable, str(E / "costo.py"), "proyecto", str(carpeta)], capture_output=True, text=True).stdout or "{}")
    rango = set(NAMES[i0:i1 + 1])
    pago = [f for f in est.get("filas", []) if f["usd"] > 0 and f["etapa"] in rango]
    if pago and not args.yes:
        print("ESTIMATED COST before running:")
        for f in pago:
            print(f"  {f['etapa']:9s} {f['proveedor']:16s} {f['cantidad']:>9} {f['unidad']:10s} ~ ${f['usd']:.2f}" + ("" if f["verificado"] else "  (price not verified)"))
        print(f"  total ~ ${sum(f['usd'] for f in pago):.2f}   (library/costs.json). Run again with --yes to accept.")
        return 3
    log = (carpeta / "factory.log").open("a", encoding="utf-8")
    for name, kind, what, cmd in STAGES[i0:i1 + 1]:
        mark = carpeta / f".done_{name}"
        if mark.exists() and not args.force:
            continue
        pj = json.loads((carpeta / "proyecto.json").read_text(encoding="utf-8"))
        if kind in ("claude", "check"):
            if name == "design" or check(name, carpeta, pj):
                mark.write_text(time.strftime("%Y-%m-%d %H:%M:%S")); print(f"{name}: ok"); continue
            print(f"STOP at {name}: {what}. Do it with the skill, then run again."); return 1
        gpu(kind, log)
        t0 = time.time(); log.write(f"\n== {name} {time.strftime('%H:%M:%S')}\n"); log.flush()
        r = subprocess.run([sys.executable, "-u", str(E / cmd[0]), str(carpeta), *cmd[1:]], stdout=log, stderr=subprocess.STDOUT,
                           env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ})
        log.write(f"== {name} {'OK' if r.returncode == 0 else 'FAIL ' + str(r.returncode)} in {time.time() - t0:.0f} s\n"); log.flush()
        if r.returncode:
            print(f"{name} failed (see {carpeta / 'factory.log'})"); return r.returncode
        mark.write_text(time.strftime("%Y-%m-%d %H:%M:%S")); print(f"{name}: ok ({time.time() - t0:.0f} s)", flush=True)
    return 0


def new(args):
    carpeta = marca_dir(args.brand, True) / "proyectos" / args.slug
    if (carpeta / "proyecto.json").exists():
        sys.exit(f"{carpeta} already exists")
    carpeta.mkdir(parents=True)
    tpl = json.loads((buscar("templates", args.template, args.brand) / "template.json").read_text(encoding="utf-8"))
    pj = dict(tpl["proyecto_base"], slug=args.slug, marca=args.brand, plantilla=args.template, estilo=args.style, personaje=args.character, tema=args.topic)
    if args.look:
        pj["look"] = args.look
    if tpl.get("campo_tema"):
        pj[tpl["campo_tema"]] = args.topic
    (carpeta / "proyecto.json").write_text(json.dumps(pj, indent=1, ensure_ascii=False), encoding="utf-8")
    (carpeta / "brief.md").write_text(f"# Brief: {args.topic}\n\n- template: {args.template}\n- character: {args.character}\n- style: {args.style}\n"
                                      f"- look: {args.look or '(choose one)'}\n\nNext: research (docs/templates/research.md), then script.\n", encoding="utf-8")
    print("new project:", carpeta)


def brand_new(args):
    d = marca_dir(args.slug, True)
    f = d / "brand.json"
    if f.exists():
        sys.exit(f"{f} already exists")
    b = {"slug": args.slug, "nombre": args.name, "handle": args.handle, "plataformas": args.platforms.split(","), "idioma": args.lang,
         "audiencia": "", "tono": "", "mensaje": "", "colores": {}, "fuentes": {}, "personaje": "", "estilo": "", "plantilla": "", "voz": {},
         "musica": None, "reglas": [], "figma": {"file_key": "", "url": ""}, "notas": []}
    f.write_text(json.dumps(b, indent=1, ensure_ascii=False), encoding="utf-8")
    print("new brand:", d)


def status(args):
    carpeta = carpeta_de(args.proyecto)
    for name, kind, what, _ in STAGES:
        print(f"{'x' if (carpeta / f'.done_{name}').exists() else ' '} {name:9s} {kind:10s} {what}")


ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sub = ap.add_subparsers(dest="cmd", required=True)
sub.add_parser("stages")
n = sub.add_parser("new"); n.add_argument("slug"); n.add_argument("--brand", default="_general"); n.add_argument("--topic", required=True); n.add_argument("--template", default="artist_short")
n.add_argument("--character", default="green_hair_presenter"); n.add_argument("--style", default="collage_v10c"); n.add_argument("--look")
r = sub.add_parser("run"); r.add_argument("proyecto"); r.add_argument("--from", dest="desde", choices=NAMES); r.add_argument("--to", dest="hasta", choices=NAMES)
r.add_argument("--only", choices=NAMES); r.add_argument("--force", action="store_true"); r.add_argument("--yes", action="store_true", help="accept the estimated cost of paid stages")
es = sub.add_parser("estimate"); es.add_argument("proyecto")
s = sub.add_parser("status"); s.add_argument("proyecto")
bn = sub.add_parser("brand-new"); bn.add_argument("slug"); bn.add_argument("--name", required=True); bn.add_argument("--handle", default="")
bn.add_argument("--platforms", default="youtube_shorts,tiktok,instagram_reels"); bn.add_argument("--lang", default="English")
a = ap.parse_args()
if a.cmd == "stages":
    for name, kind, what, _ in STAGES:
        print(f"{name:9s} {kind:10s} {what}")
elif a.cmd == "new":
    new(a)
elif a.cmd == "brand-new":
    brand_new(a)
elif a.cmd == "estimate":
    print(subprocess.run([sys.executable, str(E / "costo.py"), "proyecto", str(carpeta_de(a.proyecto))], capture_output=True, text=True).stdout)
elif a.cmd == "run":
    sys.exit(run(a))
else:
    status(a)
