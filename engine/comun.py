"""Shared pieces of the engine: config (config/local.json), keys (.env named there), project file, ffmpeg/whisper helpers.
Every script takes a project folder (one video = one folder with proyecto.json). Comments in the engine are in Spanish,
the language it was built in; docs/ explains everything in English."""
import json, os, re, subprocess
from pathlib import Path

import numpy as np

MOTOR = Path(__file__).parent
REPO = MOTOR.parent
_cfg_file = REPO / "config" / "local.json"
CFG = json.loads((_cfg_file if _cfg_file.exists() else REPO / "config" / "local.example.json").read_text(encoding="utf-8"))
KIT = (REPO / "library" / "kit").as_posix() + "/"            # assets del estilo collage (texturas, cinta, mano de papel, marcos)
LIB = REPO / "library"
PY_PORTABLE = CFG["comfy_h3"]["python"]
H3 = CFG["comfy_h3"]["h3_script"]
PY_TOOLS = CFG.get("python_tools", "python")
MOTION_DNA = Path(CFG["motion_dna"])
ENV_KEY = Path(CFG["env_file"])
BRANDS = Path(CFG.get("brands_dir") or (REPO / "brands"))   # una carpeta por marca: brands/<marca>/{brand.json, characters, styles, kit, ...}
MARCA_SUB = ["characters", "styles", "kit", "music", "references", "research", "proyectos", "collects", "assets", "figma"]


def marca_dir(slug, crear=False):
    d = BRANDS / (slug or "_general")
    if crear:
        for sub in MARCA_SUB:
            (d / sub).mkdir(parents=True, exist_ok=True)
    return d


def buscar(tipo, nombre, marca=None):
    """Un personaje, estilo o plantilla: primero en la carpeta de la marca, luego en la libreria del repo."""
    for base in ([marca_dir(marca) / tipo] if marca else []) + [LIB / tipo]:
        if (base / nombre).exists() or (base / f"{nombre}.json").exists():
            return base / nombre if (base / nombre).exists() else base / f"{nombre}.json"
    raise FileNotFoundError(f"{tipo}/{nombre} not in brand {marca} nor in library/")


def clave(nombre):
    """Lee una clave del .env (nunca se imprime). Primero el entorno, luego el archivo."""
    if os.environ.get(nombre):
        return os.environ[nombre]
    for l in ENV_KEY.read_text(encoding="utf-8").splitlines():
        if l.startswith(nombre + "="):
            return l.split("=", 1)[1].strip().strip('"')
    raise KeyError(f"{nombre} no esta en {ENV_KEY} ni en el entorno")


def con_mesa(texto, pj):
    """The episode's own props on the table (proyecto.json "mesa") in place of the candles of the character's prompts, so the
    narrator's room changes between episodes (e.g. glowing crystal spheres instead of candles). With proyecto.json
    "escenario" ({"lugar": "<where he sits, its light>", "sonido": "<ambient sound>"}) the whole room changes too: every
    description of the character's ritual room and its CRT hum is replaced by the episode's place (e.g. a jungle at night)."""
    e = pj.get("escenario")
    if e:
        lugar, sonido = sin_niebla(e["lugar"]), e.get("sonido", "night ambience")
        texto = texto.replace("the dark ritual room with CRT televisions, plastic sheeting and candles, the red and blue light",
                              "the place: " + lugar)
        texto = re.sub(r"(?:sits )?(?:in )?(?:a |his )?dark ritual room[^.]*?glow from the other", "sits " + lugar, texto)
        texto = re.sub(r"same room: [^.]*?glow from the other", "same place: " + lugar, texto)
        texto = re.sub(r"in a room of CRT TVs, plastic sheets and candles", "in " + lugar, texto)
        texto = texto.replace("Low room tone, faint CRT hum, a candle crackle.", sonido + ".")
        texto = texto.replace("Low room tone and a faint CRT hum only.", sonido + " only.")
        texto = texto.replace("Low room tone and CRT hum", sonido)
    m = pj.get("mesa")
    if not m:
        return texto
    for v in ("a few melted candles", "melted candles", "a lit candle", "candles", "candle"):
        texto = re.sub(r"\b" + re.escape(v) + r"\b", m, texto)
    return texto



def sin_niebla(texto):
    """No mist, fog or smoke where the narrator is: H3 turned "mist" into smoke drifting across his mask (review 2026-11-12,
    ep09 "quita el humo de su cara"). Used on his places and start-frame prompts; evidence images keep their mist."""
    niebla = r"\b(?:thin |light |low |thick )?(?:mist|fog|smoke|haze|steam)\b(?: (?:in|on|over) the (?:water|light|beams|road|air))?"
    texto = re.sub(niebla + r" and ", "", texto)                 # "mist and one street lamp" -> "one street lamp"
    texto = re.sub(r",?\s*(?:and )?" + niebla, "", texto)        # ", mist" / "and fog in the beams"
    return re.sub(r"\s+([,.;])", r"\1", texto).replace(";,", ";").strip(" ,")


def toma(texto, pj, lid=None):
    """con_mesa for one line: a line may bring its own place and camera (proyecto.json lineas[i] "toma": {"lugar", "sonido",
    "mesa", "camara", "verbo"}), e.g. a selfie walk through the ship while the rest of the episode stays in the cabin
    (review 2026-11-10: "shots of him holding the camera and walking, for more dynamism"). "camara" replaces the static
    camera of the character's prompts; "verbo" replaces "sits" in front of the place (e.g. "walks")."""
    ln = next((l for l in pj.get("lineas", []) if l.get("id") == lid), {}) if lid else {}
    t = ln.get("toma") or {}
    if not t:
        return con_mesa(texto, pj)
    q = dict(pj)
    if t.get("lugar"):
        t = dict(t, lugar=sin_niebla(t["lugar"]))
        q["escenario"] = {"lugar": t["lugar"], "sonido": t.get("sonido", (pj.get("escenario") or {}).get("sonido", "night ambience"))}
    if "mesa" in t:
        q["mesa"] = t["mesa"]
    texto = con_mesa(texto, q)
    if t.get("camara"):
        texto = re.sub(r"static camera at eye level, medium shot", t["camara"], texto)
    if t.get("verbo") and t.get("lugar"):
        texto = texto.replace("sits " + t["lugar"], t["verbo"] + " " + t["lugar"])
    return texto

def escena_de(pj, carpeta):
    """Imagen de partida del video: proyecto "escena" (ruta del proyecto) > el look del personaje ("look") > su escena base."""
    c = personaje(pj)
    if pj.get("escena") and (Path(carpeta) / pj["escena"]).exists():
        return Path(carpeta) / pj["escena"]
    if pj.get("look"):
        return c["_dir"] / c["looks"][pj["look"]]["imagen"]
    return c["_dir"] / c["escena_base"]


def personaje(pj):
    """character.json del personaje del proyecto (library/characters/<slug>/)."""
    d = buscar("characters", pj["personaje"], pj.get("marca"))
    c = json.loads((d / "character.json").read_text(encoding="utf-8"))
    c["_dir"] = d
    return c


def proyecto(carpeta):
    pj = json.loads((Path(carpeta) / "proyecto.json").read_text(encoding="utf-8"))
    if not pj.get("voz") and pj.get("personaje"):   # la voz del personaje si el video no pide otra
        pj["voz"] = json.loads((buscar("characters", pj["personaje"], pj.get("marca")) / "character.json").read_text(encoding="utf-8"))["voz"].get("voice_id")
    return pj


def clave_eleven(pj=None):
    """ElevenLabs key: the brand's own .env first (brands/<marca>/.env, where its voices live; CCC since 2026-11-17),
    then the environment / the shared .env. Never printed."""
    if pj and pj.get("marca"):
        env = marca_dir(pj["marca"]) / ".env"
        if env.exists():
            for l in env.read_text(encoding="utf-8").splitlines():
                if l.startswith("ELEVENLABS_API_KEY="):
                    return l.split("=", 1)[1].strip().strip('"')
    return clave("ELEVENLABS_API_KEY")


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, **kw)


def duracion(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                                capture_output=True, text=True).stdout)


def pcm16k(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


_whisper = None


def whisper():
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        _whisper = WhisperModel("small", device="cpu", compute_type="int8")
    return _whisper


def palabras(path, language="en"):
    """[(palabra, ini, fin)] de Whisper con tiempos por palabra."""
    segs, _ = whisper().transcribe(pcm16k(path), language=language, word_timestamps=True)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]


def texto_oido(path):
    segs, info = whisper().transcribe(pcm16k(path))
    return " ".join(s.text.strip() for s in segs), info.language


norm_palabras = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower().replace("-", " ")).split()


def parecido(a, b):
    import difflib
    return difflib.SequenceMatcher(None, norm_palabras(a), norm_palabras(b)).ratio()


def clip_roto(path, n=12, acerca=False):
    """None if a generated clip holds up, else the reason. H3 sometimes collapses mid-clip (ep05 L10_cont1: the picture went
    dark and smeared and every QC passed it). Measured at a quarter of the resolution so the VHS grain does not count:
    sharpness of the later frames against the first (broken clips fell to 0.49-0.60, good ones never below 0.90) and
    brightness (a collapse darkens). Not for endings where he is meant to dissolve."""
    import cv2
    cap = cv2.VideoCapture(str(path)); total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fs = []
    for i in np.linspace(0, max(total - 1, 0), n).astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i)); ok, f = cap.read()
        if ok:
            fs.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32))
    cap.release()
    if len(fs) < 3:
        return "unreadable"
    def nitidez(g):
        s = cv2.resize(g, (g.shape[1] // 4, g.shape[0] // 4), interpolation=cv2.INTER_AREA)
        return float(cv2.Laplacian(s, cv2.CV_32F).var())
    s0, l0 = nitidez(fs[0]) or 1e-6, float(fs[0].mean()) or 1e-6
    sharp = float(np.median([nitidez(f) / s0 for f in fs[1:]]))
    luma = min(float(f.mean()) / l0 for f in fs[1:])
    # a shot that moves toward him (push-in, lean into the lens) loses background detail by design: only a collapse counts
    # (ep13 L10/L12, 2026-11-12: three good seeds each were thrown away as "smeared" at 0.7)
    if sharp < (0.45 if acerca else 0.75):
        return f"smeared (sharpness {sharp:.2f} of the first frame)"
    if luma < 0.7:
        return f"went dark (brightness {luma:.2f} of the first frame)"
    return None


def energia(src, fps=20):
    """Loudness of a clip's sound in dB, one value per 1/fps s (mono 8 kHz)."""
    import numpy as np
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(b, np.int16).astype(float); n = 8000 // fps
    return [20 * np.log10(np.sqrt((a[i:i + n] ** 2).mean()) + 1) for i in range(0, len(a) - n + 1, n)]


def fin_habla(src, t, umbral=35.0, hueco=0.15, maximo=1.2, fps=20):
    """Where speech really ends after Whisper's last word end t: Whisper often ends a trailing word early ("...dollars",
    "reporters", review 2026-11-17: the voice was cut at 12 s and 47 s). Scans forward until the sound stays under the
    threshold for `hueco` s (at most `maximo` s after t)."""
    e = energia(src, fps); i = int(t * fps); quiet = 0
    while i < len(e) and i < int((t + maximo) * fps):
        quiet = quiet + 1 if e[i] < umbral else 0
        if quiet >= int(hueco * fps):
            return (i - quiet + 1) / fps
        i += 1
    return min(len(e) / fps, t + maximo)


def inicio_habla(src, t, umbral=40.0, fps=20, hasta=None):
    """First moment at or after t where the sound rises over the threshold (speech onset)."""
    e = energia(src, fps); i = int(t * fps); fin = int((hasta if hasta is not None else len(e) / fps) * fps)
    while i < min(len(e), fin):
        if e[i] >= umbral:
            return i / fps
        i += 1
    return t


def inicio_real(src, t, umbral=35.0, maximo=1.0, fps=20):
    """Where speech really starts before Whisper's first word start t (a soft first word is often heard late): walks back
    while the sound stays over the threshold (at most `maximo` s)."""
    e = energia(src, fps); i = min(int(t * fps), len(e) - 1)
    while i > 0 and i > int((t - maximo) * fps) and e[i - 1] >= umbral:
        i -= 1
    return max(0.0, i / fps)


def apretar_pausas(src, dst, coma=0.08, punto=0.20, otra=0.10, umbral=46.0):
    """The 90 % rule (VOICES.md §3.8-9, user 2026-11-16/17: "word, space, word, no rhythm"): the pause between two words is
    cut down to `coma` after a comma, `punto` after a sentence end and `otra` elsewhere. A cut only happens inside Whisper's
    gap between two heard words, only over quiet sound (< `umbral` dB: silence and breaths), and never over the soft start of
    the next word (s, f, h: walked back while the sound stays over 30 dB; review 2026-11-17: "Seoul" lost its S and became
    "oh"). The speech itself is untouched (no speed-up). Returns (old length, new length)."""
    fps = 100; e = energia(src, fps); ws = palabras(src); n = len(e)
    if not ws:
        __import__("shutil").copy2(src, dst); return 0.0, 0.0
    i0 = max(0, int(inicio_real(src, ws[0][1], umbral=30.0) * fps) - 6)
    i1 = min(n, int(fin_habla(src, ws[-1][2]) * fps) + 15)
    keep, a = [], i0
    for k in range(len(ws) - 1):
        g0 = int((ws[k][2] + 0.03) * fps)
        g1 = int(ws[k + 1][1] * fps)
        while g1 > g0 and e[g1 - 1] >= 30.0:   # protect the next word's soft onset
            g1 -= 1
        g1 -= 4
        # the quiet run inside the gap (Whisper's word ends can be early: speech still loud there is kept)
        q0 = g0
        while q0 < g1 and e[q0] >= umbral:
            q0 += 1
        q1 = q0
        while q1 < g1 and e[q1] < umbral:
            q1 += 1
        fin = ws[k][0][-1:]
        lim = punto if fin in ".?!\"" else (coma if fin in ",;:" else otra)
        if (q1 - q0) / fps > lim + 0.04:
            m = int(lim * fps / 2)
            keep.append((a / fps, (q0 + m) / fps)); a = q1 - m
    keep.append((a / fps, i1 / fps))
    sel = "+".join(f"between(t,{x:.3f},{y:.3f})" for x, y in keep)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", f"aselect='{sel}',asetpts=N/SR/TB,afade=t=in:d=0.01", str(dst)], check=True)
    return round((i1 - i0) / fps, 2), round(sum(y - x for x, y in keep), 2)


def ultimo_render(carpeta, slug):
    """The delivered render: the highest <slug>_vN.mp4 (renders are versioned since 2026-11-17), else <slug>.mp4."""
    import re as _re
    carpeta = Path(carpeta)
    vs = sorted(((int(m.group(1)), f) for f in carpeta.glob(f"{slug}_v*.mp4")
                 if (m := _re.fullmatch(rf"{_re.escape(slug)}_v(\d+)\.mp4", f.name))), key=lambda x: x[0])
    return vs[-1][1] if vs else carpeta / f"{slug}.mp4"
