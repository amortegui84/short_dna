"""Stage "clips" with Seedance 2.5 (fal.ai) instead of MiniMax H3, following the Cool Culture Club recipe (brands/ccc/prompts/
PROMPTS.md): image-to-video from the host's approved still, the host lines grouped in a few long clips (default A = L01+L03+L05,
B = L08+L10), timestamped beats per line, a short neutral pause between lines (the cut points), "Avoid:" last. Seedance's own
voice gives the lip sync; sts.py then turns it into the series voice, as with H3.
Every clip is cut into one clip per line (clips/Lxx.mp4) by aligning Whisper's words with the script, so the rest of the
pipeline (sts, montaje, mates, build_collage) runs unchanged.
Cost: fal bills Seedance 2.5 by tokens = width x height x seconds x 24 / 1024 at USD 0.0214 per 1,000 (no audio surcharge);
each clip's real size and length are logged in costos.json with the price at 480p, 720p and 1080p, and the wall-clock times.
The key comes from the brand's own .env (FAL_KEY) and is never printed.
Usage: python seedance.py <project> [--res 480p|720p|1080p] [--dry]"""
import base64, difflib, json, math, re, subprocess, sys, time, urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import palabras, personaje, proyecto  # noqa: E402

carpeta = Path(sys.argv[1]).resolve()
RES = sys.argv[sys.argv.index("--res") + 1] if "--res" in sys.argv else "480p"
SECO = "--dry" in sys.argv
pj = proyecto(carpeta); PJE = personaje(pj)
MODEL = "bytedance/seedance-2.5/image-to-video"
USD_PER_KTOK = 0.0214
DIMS = {"480p": (480, 854), "720p": (720, 1280), "1080p": (1080, 1920)}


def clave_fal():
    for env in (PJE["_dir"].parent.parent / ".env", carpeta.parent.parent / ".env"):
        if env.exists():
            for l in env.read_text(encoding="utf-8").splitlines():
                if l.startswith("FAL_KEY="):
                    return l.split("=", 1)[1].strip().strip('"')
    raise SystemExit("seedance: FAL_KEY not found in the brand's .env")


def costo(w, h, seg):
    return w * h * seg * 24 / 1024 / 1000 * USD_PER_KTOK


lineas = {l["id"]: l for l in pj["lineas"]}
grupos = pj.get("clips_seedance") or [["L01", "L03", "L05"], ["L08", "L10"]]
grupos = [[g for g in grupo if g in lineas] for grupo in grupos]
IDENT = PJE.get("seedance_identidad") or (
    "a stylized 3D art-toy floating head, no body, no neck, no hands. Keep her identity exactly as in the image for the whole clip: "
    "backwards 5-panel cap dyed orange to magenta-fuchsia, long dark hair floating below the head, huge icy blue-gray eyes, heavy "
    "smudged eyeliner, freckles, a thin silver septum ring, one ear stud. Static smooth green gradient background, lighter at the top. "
    "Locked-off camera, head centered and fully in frame, hair fully visible.")
VOZ = PJE.get("seedance_voz") or "young American woman's voice, bright, quick, gossipy and sarcastic, the same voice throughout"
AVOID = ("Avoid: body, neck, shoulders, hands, arms, extra limbs, camera movement, zoom, cropping, head leaving the frame, hair cut off "
         "by the frame, cap changing or disappearing, piercings disappearing, face morphing, identity drift, static frozen face, stiff "
         "mouth, subtitles, on-screen text.")
WPS, PAUSA, COLA = 2.6, 0.8, 1.2


def prompt(grupo, ultimo=False):
    """The recipe: identity, voice, the lines, performance notes, timestamped beats (one per line + a pause), Avoid last."""
    txt = [f"Image-to-video. Animate this exact character: {IDENT}",
           f"She speaks to camera in English, {VOZ}, with precise lip sync. {len(grupo)} separate lines, each followed by a short pause:", ""]
    for i, lid in enumerate(grupo, 1):
        txt.append(f"Line {i}: \"{lineas[lid]['texto']}\"")
    txt += ["", "Exaggerated, cartoonishly expressive art-toy performance: big eyebrow moves, cheeks squashing, wide clear mouth shapes. "
            "She mostly faces the lens with small bobs; turns her head only when the beat calls for it, then returns to the lens for each "
            "punchline. Natural blinks every 2-4 s, quick blinks on emphasis. Her hair swings with weight and momentum on every head "
            "movement and settles naturally afterwards. Cheeky, sarcastic attitude."]
    t = 0.0
    for lid in grupo:
        d = len(lineas[lid]["texto"].split()) / WPS
        acc = re.sub(r"\s*She keeps her face toward the lens.*$", "", lineas[lid].get("accion", "")).strip().rstrip(".")
        txt.append(f"[{t:.1f}-{t + d:.1f}s] {acc[0].upper() + acc[1:] if acc else 'She delivers the line to the lens'}.")
        t += d
        txt.append(f"[{t:.1f}-{t + PAUSA:.1f}s] Pause: silent, she settles to a neutral face looking into the lens, one blink.")
        t += PAUSA
    if ultimo:   # the video's ending: a real, generated hold (no loop in the edit)
        txt.append(f"[{t:.1f}-{t + COLA:.1f}s] Holds eye contact with a smug closed-mouth smile, a slow playful wink, then a satisfied smile.")
        t += COLA
    return "\n".join(txt + [AVOID]), min(30, max(4, math.ceil(t)))


def fal(metodo, url, cuerpo=None, key=None):
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode() if cuerpo is not None else None, method=metodo,
                                 headers={"Authorization": f"Key {key}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=180))


def alinear(clip, ids):
    """Each line's window in a clip: Whisper's words matched in order against the script words."""
    ws = palabras(clip)                                    # [(word, start, end), ...]
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


key = None if SECO else clave_fal()
log_p = carpeta / "costos.json"
log = json.loads(log_p.read_text(encoding="utf-8")) if log_p.exists() else {"motor": "seedance 2.5 (fal)", "clips": []}
(carpeta / "clips").mkdir(exist_ok=True); (carpeta / "prompts").mkdir(exist_ok=True)
maestro = PJE["_dir"] / PJE["maestro"]
# the still goes up as a high-quality JPEG (a 6.6 MB PNG made the request slow)
from io import BytesIO
from PIL import Image
_b = BytesIO(); Image.open(maestro).convert("RGB").save(_b, "JPEG", quality=95)
img_uri = "data:image/jpeg;base64," + base64.b64encode(_b.getvalue()).decode()
for gi, grupo in enumerate(grupos):
    nombre = f"seedance_{chr(65 + gi)}"
    out = carpeta / "clips" / f"{nombre}.mp4"
    texto, dur = prompt(grupo, gi == len(grupos) - 1)
    (carpeta / "prompts" / f"{nombre}.txt").write_text(texto, encoding="utf-8")
    w, h = DIMS[RES]
    print(f"[{nombre}] {'+'.join(grupo)} {dur} s at {RES}: ~USD {costo(w, h, dur):.2f} (720p {costo(720, 1280, dur):.2f}, 1080p {costo(1080, 1920, dur):.2f})", flush=True)
    if SECO or out.exists():
        continue
    t0 = time.time()
    sub = fal("POST", f"https://queue.fal.run/{MODEL}", {"prompt": texto, "image_url": img_uri, "resolution": RES, "duration": str(dur),
                                                          "generate_audio": True, "aspect_ratio": "auto"}, key)
    st_url, rs_url = sub["status_url"], sub["response_url"]
    while True:
        time.sleep(10)
        st = fal("GET", st_url, key=key)
        if st.get("status") == "COMPLETED":
            break
        if st.get("status") not in ("IN_QUEUE", "IN_PROGRESS"):
            raise SystemExit(f"[{nombre}] fal status {st.get('status')}: {str(st)[:300]}")
    res = fal("GET", rs_url, key=key)
    out.write_bytes(urllib.request.urlopen(res["video"]["url"], timeout=300).read())
    t1 = time.time()
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                         "-of", "json", str(out)], capture_output=True, text=True)
    meta = json.loads(pr.stdout); vw, vh = meta["streams"][0]["width"], meta["streams"][0]["height"]; vd = float(meta["format"]["duration"])
    rec = {"clip": nombre, "lineas": grupo, "pedido_s": dur, "resolucion": RES, "w": vw, "h": vh, "duracion_s": round(vd, 2),
           "usd": round(costo(vw, vh, dur), 3), "usd_si_720p": round(costo(720, 1280, dur), 3), "usd_si_1080p": round(costo(1080, 1920, dur), 3),
           "seed": res.get("seed"), "generacion_s": round(t1 - t0, 1), "hora": datetime.now().isoformat(timespec="seconds")}
    log["clips"].append(rec); log_p.write_text(json.dumps(log, indent=1), encoding="utf-8")
    print(f"[{nombre}] done in {t1 - t0:.0f} s: {vw}x{vh}, {vd:.1f} s, USD {rec['usd']:.2f}", flush=True)

# one clip per line, cut at the pauses between lines
for gi, grupo in enumerate(grupos):
    src = carpeta / "clips" / f"seedance_{chr(65 + gi)}.mp4"
    if not src.exists():
        continue
    ven = alinear(src, grupo)
    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout)
    for j, lid in enumerate(grupo):
        s, e, r = ven[lid]
        a = max(0.0, s - 0.35)
        b = min(total, (ven[grupo[j + 1]][0] - 0.15) if j + 1 < len(grupo) else total)
        dst = carpeta / "clips" / f"{lid}.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(src), "-c:v", "libx264", "-crf", "14",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(dst)], check=True)
        print(f"{lid}: {a:.2f}-{b:.2f} s of {src.name} (match {r:.2f})", flush=True)
if log["clips"]:
    tot = sum(c["usd"] for c in log["clips"])
    log["total_usd"] = round(tot, 3); log["total_si_720p"] = round(sum(c["usd_si_720p"] for c in log["clips"]), 3)
    log["total_si_1080p"] = round(sum(c["usd_si_1080p"] for c in log["clips"]), 3)
    log_p.write_text(json.dumps(log, indent=1), encoding="utf-8")
    print(f"seedance total USD {tot:.2f} (720p {log['total_si_720p']:.2f}, 1080p {log['total_si_1080p']:.2f})")
