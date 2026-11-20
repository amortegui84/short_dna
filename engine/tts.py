"""Voz unica del video con ElevenLabs v3 en modo Natural (stability 0.5: el modo Creative 0.0 hacia oscilar la entonacion).
Una linea por llamada -> vo/<id>.mp3. QC con Whisper contra el guion; hasta 3 tomas y se queda la MEJOR (los nombres propios
como "Hilma af Klint" Whisper los oye mal aunque esten bien dichos, asi que nunca se borra todo). La clave no se imprime.
Uso: python tts.py <carpeta>"""
import base64, json, re, sys, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import clave_eleven, parecido, personaje, proyecto, texto_oido  # noqa: E402

carpeta = Path(sys.argv[1])
pj = proyecto(carpeta)
vo = carpeta / "vo"
vo.mkdir(exist_ok=True)
VOZ = personaje(pj).get("voz", {}) if pj.get("personaje") else {}
# per-video override of the character's voice settings (2026-11-20, N04: Buns at speed 0.9 natively instead of 1.15 then a
# 22 % rubberband stretch, which sounded "raro"): proyecto.json "voz_ajustes": {"speed": 0.9}
VOZ = dict(VOZ, **pj.get("voz_ajustes", {}))
# "motor_voz": "qwen3" (2026-11-19, out of ElevenLabs credit): a local clone of the same voice (engine/tts_local.py), from
# brands/<brand>/voces/<voice id>.wav + .txt; everything after (blocks, cuts, qa_lineas) is the same
MOTOR = pj.get("motor_voz") or VOZ.get("motor") or "eleven"
H = {"xi-api-key": clave_eleven(pj), "Content-Type": "application/json"} if MOTOR == "eleven" else {}


def pedir_local(texto):
    import os, tempfile
    from comun import marca_dir
    ref = marca_dir(pj.get("marca")) / "voces" / f"{pj['voz']}.wav"
    if not ref.exists():
        sys.exit(f"motor_voz qwen3: no reference clip {ref} (+ .txt with its words)")
    fd, out = tempfile.mkstemp(suffix=".mp3"); os.close(fd)
    py = r"D:\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\python_embeded\python.exe"
    subprocess.run([py, "-I", str(Path(__file__).with_name("tts_local.py")), str(ref), str(ref.with_suffix(".txt")), out, texto],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    datos = Path(out).read_bytes(); os.remove(out)
    return datos


def pedir_tts(texto):
    if MOTOR == "qwen3":
        return pedir_local(texto)
    modelo = VOZ.get("modelo", "eleven_v3")
    if modelo != "eleven_v3":   # solo v3 entiende [etiquetas]; en v2 se quitan (si no, las lee)
        texto = re.sub(r"\s*\[[^\]]+\]\s*", " ", texto).strip()
    ajustes = {"stability": VOZ.get("stability", 0.5)}
    for k in ("speed", "similarity_boost", "style"):
        if k in VOZ:
            ajustes[k] = VOZ[k]
    body = {"text": texto, "model_id": modelo, "voice_settings": ajustes}
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{pj['voz']}/with-timestamps?output_format=mp3_44100_128",
        data=json.dumps(body).encode(), headers=H), timeout=180))
    return base64.b64decode(r["audio_base64"])


# by blocks (review 2026-11-12: "the voice is very flat"; research: generating line by line makes every sentence start fresh and
# fall the same way): proyecto.json "bloques_voz": [["L01","L02","L03"], ...] sends each block in one call, so the intonation
# flows across the lines; Whisper's word times cut it back into vo/<id>.mp3 at the gaps between lines (nothing else changes).
import re, subprocess  # noqa: E402
import numpy as np  # noqa: E402
from comun import palabras  # noqa: E402


def mono16k(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def valle(x, a, b, sr=16000, win=0.01):
    """The quietest 10 ms between a and b seconds: the cut point between two lines of one block (review 2026-11-13)."""
    i0, i1, w = max(0, int(a * sr)), min(len(x), int(b * sr)), int(win * sr)
    if i1 - i0 <= w:
        return round((a + b) / 2, 3)
    e = np.convolve(x[i0:i1] ** 2, np.ones(w) / w, mode="valid")
    return round((i0 + int(np.argmin(e)) + w // 2) / sr, 3)
# blocks are for ElevenLabs only: Qwen3 runs lines together without a pause, so a cut fell inside "preaching" (R22, 2026-11-19);
# the local clone speaks each line alone (the per-line loop below)
for bloque in (pj.get("bloques_voz", []) if MOTOR == "eleven" else []):
    lns = [l for l in pj["lineas"] if l["id"] in bloque]
    if all((vo / f"{l['id']}.mp3").exists() for l in lns):
        continue
    mejor = None
    previas = sorted(vo.glob(f"bloque_{lns[0]['id']}_t*.mp3"))   # an earlier take is reused (re-cutting costs nothing)
    for intento in range(3):
        toma = previas[0] if previas and intento == 0 else vo / f"bloque_{lns[0]['id']}_t{intento}.mp3"
        if not (previas and intento == 0):
            # tone tags first (character "voz.etiquetas", review 2026-11-13: "too whispered, make it more normal"), and a closing
            # [pause]: eleven_v3 stopped mid-syllable at the end of 12 of 16 takes
            texto = " ".join(l.get("tts", l["texto"]) for l in lns)
            # "voz.etiquetas" is a description of the host's tags, not text to read (2026-11-17: the block started with
            # "Reactions, ha ha ha"): only its first [tag], and only when the block does not open with its own tag
            tags = re.findall(r"\[[^\]]+\]", VOZ.get("etiquetas", ""))
            pre = tags[0] if tags and not texto.lstrip().startswith("[") else ""
            toma.write_bytes(pedir_tts((pre + " " + texto).strip() + " [pause]"))
        ws = palabras(toma)
        oido = " ".join(w for w, _, _ in ws)
        p = parecido(" ".join(l["texto"] for l in lns), oido)
        print(f"block {lns[0]['id']}-{lns[-1]['id']} take {intento} {p:.2f} | {oido}", flush=True)
        if not mejor or p > mejor[0]:
            mejor = (p, toma, ws)
        if p >= 0.88:
            break
    p, toma, ws = mejor
    # cut points: align Whisper's words to the script's words (difflib), then cut halfway into the gap after each line's last
    # word; counting words failed where Whisper splits "take-off" or writes "$200,000" (ep13, 2026-11-12)
    import difflib
    norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
    guion, dueno = [], []
    for i, l in enumerate(lns):
        for w in re.sub(r"[^\w\s'-]", " ", l["texto"]).split():
            guion.append(norm(w)); dueno.append(i)
    oidas = [norm(w) for w, _, _ in ws]
    mapa = {}
    for blq in difflib.SequenceMatcher(None, guion, oidas, autojunk=False).get_matching_blocks():
        for j in range(blq.size):
            mapa[blq.a + j] = blq.b + j
    senal = mono16k(toma)
    cortes = [0.0]
    for i in range(len(lns) - 1):
        ultimos = [k for k, d in enumerate(dueno) if d == i and k in mapa]
        primeros = [k for k, d in enumerate(dueno) if d == i + 1 and k in mapa]
        fin_w = mapa[ultimos[-1]] if ultimos else None
        ini_w = mapa[primeros[0]] if primeros else None
        if fin_w is None and ini_w is not None:
            fin_w = ini_w - 1
        if ini_w is None and fin_w is not None:
            ini_w = fin_w + 1
        if fin_w is None:   # neither side of the join was recognised (ep14 L03/L04): split by the share of script words
            k = sum(1 for d in dueno if d <= i)
            fin_w = max(0, min(len(ws) - 2, round(k / len(dueno) * len(ws)) - 1))
            ini_w = fin_w + 1
        fin, ini = ws[fin_w][2], ws[min(ini_w, len(ws) - 1)][1]
        cortes.append(valle(senal, min(fin, ini) - 0.25, max(fin, ini) + 0.25))   # wider: Whisper word times are off by up to ~0.2 s (ep13 L06 cut into "Then")
    cortes.append(None)
    for i, l in enumerate(lns):
        a, b = cortes[i], cortes[i + 1]
        # no click at a cut; the take's own end gets a longer fade: eleven_v3 often stops mid-syllable (2026-11-13: 12 of 16 takes)
        # a block's first line starts at the take's t=0, and multilingual_v2 at speed 0.9 voices the first consonant from sample 0
        # (A04 "Nine", 2026-11-20: 5 takes failed qa_lineas "cut at start" with the word whole): 60 ms of air in front
        bordes = ("adelay=60:all=1," if a < 0.01 else "") + "afade=t=in:d=0.01," + (f"afade=t=out:st={max(0.0, b - a - 0.02):.3f}:d=0.02" if b else "areverse,afade=t=in:d=0.06,areverse")
        # seek on the input (-ss/-to before -i) so the cut starts at t=0: with output seeking the fade-out "st" was read on the take's
        # clock and every line after a block's first came out silent (ep13 L05/L06, 2026-11-13)
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}"] + (["-to", f"{b:.3f}"] if b else []) + ["-i", str(toma), "-af", bordes, "-c:a", "libmp3lame", "-b:a", "192k", str(vo / f"{l['id']}.mp3")]
        subprocess.run(cmd, check=True)
    for t in vo.glob(f"bloque_{lns[0]['id']}_t*.mp3"):
        if t != toma:
            t.unlink(missing_ok=True)

for ln in pj["lineas"]:
    # with Seedance the host lines' voice comes from the clip itself (then speech-to-speech): no TTS for them
    if pj.get("motor_clips") in ("seedance", "kling") and ln["tipo"] == "A":
        continue
    mp3 = vo / f"{ln['id']}.mp3"
    if mp3.exists():
        continue
    tomas = []
    for intento in range(3):
        toma = vo / f"{ln['id']}_t{intento}.mp3"
        toma.write_bytes(pedir_tts(ln.get("tts", ln["texto"])))   # same request as before; pedir_tts strips tags for non-v3
        oido, lang = texto_oido(toma)
        p = parecido(ln["texto"], oido) if lang == "en" else 0.0
        print(f"{ln['id']} toma {intento} {p:.2f} {lang} | {oido}", flush=True)
        tomas.append((p, toma))
        if p >= 0.85:
            break
    mejor = max(tomas)[1]
    mejor.replace(mp3)
    if VOZ.get("procesado") in ("ultratumba", "claro", "limpio"):   # voz procesada en local (voz_ultratumba.py): "claro" = entendible, "ultratumba" = cripta
        from voz_ultratumba import procesar
        crudo = mp3.with_name(mp3.stem + "_crudo.mp3"); mp3.replace(crudo); procesar(crudo, mp3, VOZ.get("semitonos", 2.0), VOZ["procesado"])
    for _, t in tomas:
        t.unlink(missing_ok=True)


# gate (review 2026-11-13: "the audio cuts at 2, 14 and 35 s... this happens very often"): every line is checked alone (silent,
# cut mid-sound, missing first/last words, Whisper match); a failing line throws away its block's take and the block is asked
# again, up to 4 more rounds; then the stage fails, so a broken line never reaches the edit (engine/qa_lineas.py).
import os  # noqa: E402
from qa_lineas import revisar  # noqa: E402
fallas = revisar(carpeta)
for f in fallas:
    print("qa_lineas FAIL", f, flush=True)
if fallas:
    ronda = int(os.environ.get("TTS_RONDA", "0"))
    malas = {f.split(":")[0] for f in fallas}
    for bloque in pj.get("bloques_voz", []) or [[l["id"]] for l in pj["lineas"]]:
        if malas & set(bloque):
            for t in list(vo.glob(f"bloque_{bloque[0]}_t*.mp3")):
                t.unlink()
            for lid in bloque:
                (vo / f"{lid}.mp3").unlink(missing_ok=True)
    if ronda >= 4:
        sys.exit(f"qa_lineas: {len(fallas)} line(s) still fail after 5 rounds")
    print(f"qa_lineas: round {ronda + 1}, asking again for", sorted(malas), flush=True)
    r = subprocess.run([sys.executable, "-u", __file__, str(carpeta)], env={**os.environ, "TTS_RONDA": str(ronda + 1)})
    sys.exit(r.returncode)
print("qa_lineas: every line ok", flush=True)
