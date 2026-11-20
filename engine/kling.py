"""Stage "clips" with Kling 4.0 REFERENCE-TO-VIDEO on fal (kling/v4/reference-to-video), for the Cool Culture Club hosts.

Rule (user, 2026-11-17): reference, never first frame / end frame. The approved head goes in as @Element1 (frontal image +
up to 3 extra approved views); start_image_url / middle_image_urls / end_image_url are never sent.
The host's A lines are grouped in clips (proyecto.json "clips_kling", else each run of consecutive A lines, else the Seedance
default L01+L03+L05 / L08+L10), with timestamped beats and a short neutral pause between lines (the cut points), "Avoid:" last.
Kling's own voice gives the lip sync; sts.py then turns it into the series voice (ElevenLabs), as with Seedance.
Optional: a Kling voice made from the host's ElevenLabs reference take (character.json kling.voice_id_kling, created with
--crear-voz, USD 0.007, sends that synthetic sample to fal: only with the user's OK) is bound to @Element1 so the clip already
speaks close to the series voice.
Every clip is cut into one clip per line (clips/Lxx.mp4) by aligning Whisper's words with the script, so sts, montaje, mates
and build_collage run unchanged.
Cost: USD 0.157 a second at 720p, 0.235 at 1080p (fal price page, 2026-11-17). Logged in costos.json.
DRY BY DEFAULT: without --pagar it only writes the prompts and the request (prompts/kling_*.json) and prints the cost.
The key comes from the brand's own .env (FAL_KEY) and is never printed.
Usage: python kling.py <project> [--res 720p|1080p] [--pagar]
       python kling.py <project> --crear-voz <sample.mp3|wav>   (needs the user's OK; writes kling.voice_id_kling)
"""
import base64, difflib, json, math, re, subprocess, sys, time, urllib.error, urllib.request
from datetime import datetime
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import marca_dir, palabras, personaje, proyecto, fin_habla, inicio_habla  # noqa: E402

carpeta = Path(sys.argv[1]).resolve()
RES = sys.argv[sys.argv.index("--res") + 1] if "--res" in sys.argv else "720p"
PAGAR = "--pagar" in sys.argv
pj = proyecto(carpeta); PJE = personaje(pj)
MODEL = "kling/v4/reference-to-video"
USD_S = {"720p": 0.157, "1080p": 0.235}
KL = PJE.get("kling") or {}


def clave_fal():
    for env in ([marca_dir(pj["marca"]) / ".env"] if pj.get("marca") else []) + [carpeta.parent.parent / ".env"]:
        if env.exists():
            for l in env.read_text(encoding="utf-8").splitlines():
                if l.startswith("FAL_KEY="):
                    return l.split("=", 1)[1].strip().strip('"')
    raise SystemExit("kling: FAL_KEY not found in the brand's .env")


def fal(metodo, url, cuerpo=None, key=None):
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode() if cuerpo is not None else None, method=metodo,
                                 headers={"Authorization": f"Key {key}", "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=300))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"fal {e.code} on {url.split('?')[0]}: {e.read().decode(errors='replace')[:800]}")


def esperar(sub, key, nombre):
    while True:
        time.sleep(10)
        st = fal("GET", sub["status_url"], key=key)
        if st.get("status") == "COMPLETED":
            return fal("GET", sub["response_url"], key=key)
        if st.get("status") not in ("IN_QUEUE", "IN_PROGRESS"):
            raise SystemExit(f"[{nombre}] fal status {st.get('status')}: {str(st)[:300]}")


def uri_imagen(p):
    """Images go up as high-quality JPEG data URIs (a big PNG made Seedance requests slow)."""
    from PIL import Image
    b = BytesIO(); Image.open(p).convert("RGB").save(b, "JPEG", quality=95)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


# ---------- optional: a Kling voice from the host's ElevenLabs reference take ----------
if "--crear-voz" in sys.argv:
    muestra = Path(sys.argv[sys.argv.index("--crear-voz") + 1]).resolve()
    key = clave_fal()
    uri = f"data:audio/{muestra.suffix.lstrip('.')};base64," + base64.b64encode(muestra.read_bytes()).decode()
    res = esperar(fal("POST", "https://queue.fal.run/fal-ai/kling-video/create-voice", {"voice_url": uri}, key), key, "create-voice")
    cj = PJE["_dir"] / "character.json"
    d = json.loads(cj.read_text(encoding="utf-8"))
    d.setdefault("kling", {})["voice_id_kling"] = res["voice_id"]
    d["kling"]["voice_muestra"] = str(muestra)
    cj.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"kling voice {res['voice_id']} saved in {cj.name} (USD 0.007)")
    sys.exit()

# ---------- the clips ----------
lineas = {l["id"]: l for l in pj["lineas"]}
if pj.get("clips_kling"):
    grupos = pj["clips_kling"]
elif any((l.get("ab") or l.get("tipo")) == "A" for l in pj["lineas"]):   # each run of consecutive A lines is one clip
    grupos, run = [], []
    for l in pj["lineas"]:
        if (l.get("ab") or l.get("tipo")) == "A":
            run.append(l["id"])
        elif run:
            grupos.append(run); run = []
    if run:
        grupos.append(run)
else:
    grupos = pj.get("clips_seedance") or [["L01", "L03", "L05"], ["L08", "L10"]]
grupos = [[g for g in grupo if g in lineas] for grupo in grupos]

ELLA = PJE.get("pronombre", "she")
IDENT = PJE.get("descripcion") or PJE.get("identidad_fija", "")
VOZ = KL.get("voz") or PJE["voz"].get("descripcion", "")
WPS = float(KL.get("wps") or PJE.get("kling_wps") or 2.6)   # for the beat timestamps only
PAUSA, COLA = 0.8, 1.2
nunca = PJE.get("nunca") or []
AVOID = "Avoid: " + ", ".join(dict.fromkeys(nunca + ["camera movement", "zoom", "cropping", "subtitles", "on-screen text"])) + "."
VOICE_K = KL.get("voice_id_kling")


def prompt(grupo, ultimo=False):
    """@Element1 = the head. Identity, voice, the lines, performance, timestamped beats (one per line + a pause), Avoid last."""
    habla = "@Element1 speaks with @Voice1" if VOICE_K else f"@Element1 speaks in English, {VOZ}"
    txt = [f"Vertical 9:16 shot of @Element1, a floating hyperreal 3D art-toy head, exactly as in its reference images: {IDENT} "
           f"Only the head: no body, no neck, no hands. Smooth gradient background as in the reference. Locked-off camera that never "
           f"zooms or moves: the head keeps the same size and stays centered and fully in frame, top of the head included.",
           f"{habla}, straight to camera, with precise lip sync. {len(grupo)} separate lines, said exactly as written, word for word, "
           f"nothing added or repeated, each followed by a short pause:", ""]
    for i, lid in enumerate(grupo, 1):
        if lineas[lid].get("mudo"):
            txt.append(f"Line {i}: (silent, no words at all, mouth closed: {lineas[lid].get('accion', 'a held expression')})")
            continue
        txt.append(f"Line {i}: \"{re.sub(r'\s*\[[^\]]*\]\s*', ' ', lineas[lid].get('tts') or lineas[lid]['texto']).strip()}\"")
    txt += ["", "Exaggerated, cartoonishly expressive art-toy performance: big eyebrow moves, cheeks squashing, wide clear mouth "
            "shapes. Faces the lens with small bobs; turns the head only when the beat calls for it, then back to the lens for each "
            "punchline. Natural blinks every 2-4 s. Hair moves with weight and settles."]
    t = 0.0
    for lid in grupo:
        d = float(lineas[lid].get("dur_mudo", 3.0)) if lineas[lid].get("mudo") else len(lineas[lid]["texto"].split()) / WPS
        acc = lineas[lid].get("accion", "").strip().rstrip(".")
        txt.append(f"[{t:.1f}-{t + d:.1f}s] {acc[0].upper() + acc[1:] if acc else 'Delivers the line to the lens'}.")
        t += d
        txt.append(f"[{t:.1f}-{t + PAUSA:.1f}s] Pause: silent, settles to a neutral face looking into the lens, one blink.")
        t += PAUSA
    if ultimo:
        txt.append(f"[{t:.1f}-{t + COLA:.1f}s] Holds eye contact with a smug closed-mouth smile, then a satisfied smile.")
        t += COLA
    return "\n".join(txt + [AVOID]), min(30, max(3, math.ceil(t)))


maestro = PJE.get("maestro") or PJE.get("maestro_provisional")
# the episode's own head (the approved still + its thematic accessory, accesorio.py), proyecto.json "maestro_episodio"
MAESTRO_P = (carpeta / pj["maestro_episodio"]) if pj.get("maestro_episodio") else (PJE["_dir"] / maestro if maestro else None)
if not MAESTRO_P:
    raise SystemExit("kling: the character has no approved still (maestro)")
if not PJE.get("maestro") and not pj.get("maestro_episodio"):
    print(f"WARNING: {PJE['slug']} uses the provisional board still ({maestro}): not approved, low resolution", flush=True)
refs = [r for r in (KL.get("referencias") or []) if r.lower().endswith((".png", ".jpg", ".jpeg"))][:3]
REF_DIR = PJE["_dir"]
if pj.get("maestro_episodio"):   # the character's own views lack the accessory: only the episode's views go in
    refs, REF_DIR = (pj.get("referencias_episodio") or [])[:3], carpeta
if not refs:   # fal: an element needs a frontal image AND 1-3 reference images
    raise SystemExit("kling: the head element needs 1-3 reference views (character kling.referencias or proyecto.json referencias_episodio)")

key = clave_fal() if PAGAR else None
log_p = carpeta / "costos.json"
log = json.loads(log_p.read_text(encoding="utf-8")) if log_p.exists() else {"clips": []}
log["motor"] = "kling 4.0 reference-to-video (fal)"
(carpeta / "clips").mkdir(exist_ok=True); (carpeta / "prompts").mkdir(exist_ok=True)
total = 0.0
for gi, grupo in enumerate(grupos):
    nombre = f"kling_{chr(65 + gi)}"
    out = carpeta / "clips" / f"{nombre}.mp4"
    texto, dur = prompt(grupo, gi == len(grupos) - 1)
    elem = {"frontal_image_url": f"<{MAESTRO_P.name}>", "reference_image_urls": [f"<{r}>" for r in refs] or None}
    if VOICE_K:
        elem["voice_id"] = VOICE_K
    cuerpo = {"prompt": texto, "duration": dur, "elements": [elem], "resolution": RES, "aspect_ratio": "9:16"}
    if VOICE_K:
        cuerpo["voice_ids"] = [VOICE_K]
    (carpeta / "prompts" / f"{nombre}.json").write_text(json.dumps(cuerpo, indent=1, ensure_ascii=False), encoding="utf-8")
    usd = dur * USD_S[RES]
    total += usd
    print(f"[{nombre}] {'+'.join(grupo)} {dur} s at {RES}: USD {usd:.2f} (720p {dur * 0.157:.2f}, 1080p {dur * 0.235:.2f})", flush=True)
    if not PAGAR or out.exists():
        continue
    elem["frontal_image_url"] = uri_imagen(MAESTRO_P)
    elem["reference_image_urls"] = [uri_imagen(REF_DIR / r) for r in refs]
    t0 = time.time()
    res = esperar(fal("POST", f"https://queue.fal.run/{MODEL}", cuerpo, key), key, nombre)
    out.write_bytes(urllib.request.urlopen(res["video"]["url"], timeout=300).read())
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                         "-of", "json", str(out)], capture_output=True, text=True)
    meta = json.loads(pr.stdout); vd = float(meta["format"]["duration"])
    rec = {"clip": nombre, "lineas": grupo, "pedido_s": dur, "resolucion": RES, "w": meta["streams"][0]["width"],
           "h": meta["streams"][0]["height"], "duracion_s": round(vd, 2), "usd": round(usd, 3),
           "generacion_s": round(time.time() - t0, 1), "hora": datetime.now().isoformat(timespec="seconds")}
    log["clips"].append(rec); log_p.write_text(json.dumps(log, indent=1), encoding="utf-8")
    print(f"[{nombre}] done in {rec['generacion_s']:.0f} s: {rec['w']}x{rec['h']}, {vd:.1f} s, USD {usd:.2f}", flush=True)
print(f"kling total USD {total:.2f} at {RES}{'' if PAGAR else ' (dry run: nothing sent, add --pagar after the OK)'}")
if not PAGAR and "--recortar" not in sys.argv:
    sys.exit()


def alinear(clip, ids):
    """Each line's window in a clip: Whisper's words matched in order against the script words."""
    ws = palabras(clip)
    oido = [re.sub(r"[^a-z0-9']", "", w[0].lower()) for w in ws]
    out, k = {}, 0
    for lid in ids:
        guion = [re.sub(r"[^a-z0-9']", "", w.lower()) for w in lineas[lid]["texto"].split()]
        best = (0, k, k + len(guion))
        for a in range(k, max(k + 1, len(oido) - 2)):
            for b in range(a + max(2, len(guion) // 2), min(len(oido), a + len(guion) * 2) + 1):
                r = difflib.SequenceMatcher(None, guion, oido[a:b]).ratio()
                if r > best[0]:
                    best = (r, a, b)
        r, a, b = best
        out[lid] = (ws[a][1], ws[b - 1][2], r)
        k = b
    return out


for gi, grupo in enumerate(grupos):
    src = carpeta / "clips" / f"kling_{chr(65 + gi)}.mp4"
    if not src.exists():
        continue
    habladas = [g for g in grupo if not lineas[g].get("mudo")]
    ven = alinear(src, habladas)
    for j, lid in enumerate(grupo):   # a silent line takes the span after the previous spoken line (or the clip start)
        if lineas[lid].get("mudo"):
            prev = [ven[g][1] for g in grupo[:j] if g in ven]
            ven[lid] = ((prev[-1] + 0.35) if prev else 0.35, None, 1.0)
    largo = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                                 capture_output=True, text=True).stdout)
    # Kling cuts its own camera (wide <-> close) between lines: a per-line cut that crosses one shows 2-10 frames of the
    # other framing (review 2026-11-17: "saltos raros en el avatar"). Scene changes in the take, so the cuts snap to them
    sc = subprocess.run(["ffmpeg", "-v", "info", "-i", str(src), "-vf", "select='gt(scene,0.25)',showinfo", "-an", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    cambios = [float(x) for x in re.findall(r"pts_time:([\d.]+)", sc)]
    if cambios:
        print(f"{src.name}: Kling camera cuts at " + ", ".join(f"{c:.2f}" for c in cambios), flush=True)
    for j, lid in enumerate(grupo):
        s, e, r = ven[lid]
        # cut points by sound (review 2026-11-17: "reporters" lost its end at 47 s): a line ends where its speech goes
        # quiet after Whisper's last word, the next starts where speech rises again after that (Whisper put a phantom "and"
        # 2 s early, so the next clip started with the previous word's tail)
        if j > 0 and not lineas[lid].get("mudo") and ven[grupo[j - 1]][1] is not None:
            fp = fin_habla(src, ven[grupo[j - 1]][1])
            on = inicio_habla(src, fp + 0.15, hasta=max(s, fp) + 3.0)
            s = on if on > fp + 0.15 else s
        a = max(0.0, s - 0.35)
        if j + 1 < len(grupo) and e is not None:
            # the next line starts where the sound rises again after this line's quiet (Whisper's next start can be early,
            # a phantom word, or late, a soft first word): the sound wins when there is one
            fe = fin_habla(src, e); sn = ven[grupo[j + 1]][0]
            on = inicio_habla(src, fe + 0.15, hasta=max(sn, fe) + 3.0)
            sn = on if on > fe + 0.15 else sn
            b = min(largo, max(fe + 0.2, min(sn - 0.15, fe + 0.6)))
        else:
            b = largo
        # snap to a camera cut: a clip never holds the first frames of the next framing nor the last ones of the previous
        for c in cambios:
            if a < c <= a + 0.7 and (s is None or c <= s):
                a = c + 0.01
            if b - 0.7 <= c < b and (e is None or c >= e - 0.2):   # Kling may cut on the last syllable
                b = c - 0.01
        # the sound runs on to the real end of the speech even when the picture stops at a camera cut (the last frame holds
        # under the last syllable), so the voice is never cut with the picture
        ba = max(b, min(largo, fin_habla(src, e) + 0.2)) if e is not None else b
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-filter_complex",
                        f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={ba - b:.3f}[v];"
                        f"[0:a]atrim={a:.3f}:{ba:.3f},asetpts=PTS-STARTPTS[s]", "-map", "[v]", "-map", "[s]", "-c:v", "libx264",
                        "-crf", "14", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(carpeta / "clips" / f"{lid}.mp4")],
                       check=True)
        print(f"{lid}: {a:.2f}-{b:.2f} s of {src.name} (match {r:.2f})", flush=True)
log["total_usd"] = round(sum(c["usd"] for c in log["clips"]), 3)
log_p.write_text(json.dumps(log, indent=1), encoding="utf-8")
