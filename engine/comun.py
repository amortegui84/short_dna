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
    narrator's room changes between episodes (e.g. glowing crystal spheres instead of candles)."""
    m = pj.get("mesa")
    if not m:
        return texto
    for v in ("a few melted candles", "melted candles", "a lit candle", "candles", "candle"):
        texto = re.sub(r"\b" + re.escape(v) + r"\b", m, texto)
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


def clave_eleven():
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
