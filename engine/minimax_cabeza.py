"""Reaction (news) format: the host's head animated with MiniMax H3 Max on fal, line by line, with everything the N04 tests taught
(2026-11-20, memory minimax-fal-cabezas):
  - every visible host clip (reaccion.json host.clips minus "fuera") is one generation with OUR ElevenLabs voice pinned
    (target_audio_url); a clip up to MAX_REF s goes to reference-to-video (first frame = the approved head, structured prompt:
    identity, the exact words, delivery + acting from minimax.json, "avoid: cuts, scene changes..."); longer clips, or a clip
    that fails its check twice, go to lip-sync/image-to-video (never breaks the look, less acting);
  - check of every clip: no scene cut inside (scene score), the background stays the head's own plain gradient (corners);
  - one CONCEPT shot per video (minimax.json "concepto": line, prompt, reference frame): reference-to-video with NO first
    frame, Image 1 = head, Image 2 = a frame of the real footage, 9:16; edited as a full plan (head hidden), credit AI-GENERATED;
  - cut-outs (mates/mm_Lxx.mov, InSPyReNet, local GPU) padded with the last frame; reaccion.minimax.json written for the edit
    (the jsx scales a big head whose clip touches its frame edges until those edges sit on the video's).
Cost USD 0.08/s at 768P (fal price, 2026-11-20), logged in costos.json. DRY BY DEFAULT: --pagar spends. Key from the brand .env.
Usage: python minimax_cabeza.py <project> [--pagar] [--solo L03,L09]     then  --montar  builds + renders <slug>_vN_minimax.mp4"""
import base64, json, re, shutil, subprocess, sys, time, urllib.error, urllib.request
from datetime import datetime
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from comun import MOTION_DNA, PY_PORTABLE, duracion, personaje, proyecto  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta); PJE = personaje(pj)
PAGAR, MONTAR = "--pagar" in sys.argv, "--montar" in sys.argv
SOLO = set(sys.argv[sys.argv.index("--solo") + 1].split(",")) if "--solo" in sys.argv else None
MM = json.loads((carpeta / "minimax.json").read_text(encoding="utf-8"))
R = json.loads((carpeta / "reaccion.json").read_text(encoding="utf-8"))
T = json.loads((carpeta / "vo" / "tiempos_reaccion.json").read_text(encoding="utf-8"))
VOZ = carpeta / "vo" / "voz_reaccion.wav"
GEN = carpeta / "minimax"; GEN.mkdir(exist_ok=True); (carpeta / "mates").mkdir(exist_ok=True)
MASTER = PJE["_dir"] / PJE["maestro"]
USD_S, MAX_REF = 0.08, 6.0
TXT = {l["id"]: l.get("texto") for l in pj["lineas"]}


def clave():
    for env in [carpeta.parent.parent / ".env", Path(r"D:\minimax\ccc\.env")]:
        if env.exists():
            for l in env.read_text(encoding="utf-8").splitlines():
                if l.startswith("FAL_KEY="):
                    return l.split("=", 1)[1].strip().strip('"')
    sys.exit("FAL_KEY not found")


def fal(m, url, body=None):
    r = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, method=m,
                               headers={"Authorization": f"Key {KEY}", "Content-Type": "application/json"})
    for intento in range(3):
        try:
            return json.load(urllib.request.urlopen(r, timeout=300))
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:600]
            if e.code < 500 or intento == 2:
                raise RuntimeError(f"fal {e.code}: {msg}")
        except (urllib.error.URLError, TimeoutError):
            if intento == 2:
                raise
        time.sleep(5)


def correr(endpoint, body, out):
    sub = fal("POST", f"https://queue.fal.run/{endpoint}", body)
    while True:
        time.sleep(8); st = fal("GET", sub["status_url"])
        if st.get("status") == "COMPLETED":
            break
        if st.get("status") not in ("IN_QUEUE", "IN_PROGRESS"):
            raise RuntimeError(f"status {st}")
    res = fal("GET", sub["response_url"])
    out.write_bytes(urllib.request.urlopen(res["video"]["url"], timeout=300).read())
    return res


def con_margen(p, k=0.68):
    """The approved head smaller (k) on its own background: MiniMax often leans in during a clip, and with the head at full size
    the ears/locks left the clip and showed cut when small (N06 33 s, N09 7 s). Only the HEAD is pasted (alpha of the character's
    placeholder_head.png): pasting the whole master left a visible rectangle that MiniMax copied (2026-11-20)."""
    from PIL import ImageFilter
    m = Image.open(p).convert("RGB"); w, h = m.size; a = np.asarray(m).astype(float)
    fila = (a[:, :6].mean(1) + a[:, -6:].mean(1)) / 2
    fondo = Image.fromarray(np.repeat(fila[:, None, :], w, 1).astype(np.uint8))
    alfa = Image.open(PJE["_dir"] / "placeholder_head.png").getchannel("A").resize((w, h), Image.LANCZOS)
    alfa = alfa.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2))
    peq, am = m.resize((int(w * k), int(h * k)), Image.LANCZOS), alfa.resize((int(w * k), int(h * k)), Image.LANCZOS)
    fondo.paste(peq, ((w - peq.size[0]) // 2, int((h - peq.size[1]) * 0.55)), am)
    out = GEN / "maestro_margen.jpg"; fondo.save(out, quality=95); return out


def jpg(p):
    b = BytesIO(); Image.open(p).convert("RGB").save(b, "JPEG", quality=93)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def audio(a, b, out, minimo=0.0):
    pad = f",apad=whole_dur={max(minimo, b - a):.3f}" if minimo else ""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", str(VOZ), "-af", f"afade=t=out:st={max(0, b - a - 0.08):.3f}:d=0.08{pad}",
                    "-ac", "1", "-b:a", "192k", str(out)], check=True)
    return "data:audio/mpeg;base64," + base64.b64encode(out.read_bytes()).decode()


def gasto(que, segs):
    cp = carpeta / "costos.json"; c = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else []
    if isinstance(c, dict):
        c = c.get("items", [])
    c.append({"fecha": datetime.now().isoformat(timespec="seconds"), "que": que, "segundos": round(segs, 2), "usd": round(segs * USD_S, 3)})
    cp.write_text(json.dumps(c, indent=1, ensure_ascii=False), encoding="utf-8")
    return segs * USD_S


def frames(v, n=12, w=96):
    d = duracion(v); out = []
    for k in range(n):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{d * (k + 0.5) / n:.2f}", "-i", str(v), "-frames:v", "1", "-vf", f"scale={w}:-2",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        h = len(raw) // (w * 3)
        if h:
            out.append(np.frombuffer(raw[:w * h * 3], np.uint8).reshape(h, w, 3).astype(float))
    return out


def revisar(v, cabeza=True):
    """(ok, why): no scene cut inside, and for a floating head the four corners keep the master's background colour."""
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(v), "-vf", "scale=270:-2,scdet=threshold=1:sc_pass=0", "-an", "-f", "null", "-"], capture_output=True, text=True)
    sc = [(float(t), float(s)) for s, t in re.findall(r"lavfi\.scd\.score:\s*([\d.]+),\s*lavfi\.scd\.time:\s*([\d.]+)", r.stderr)]
    cortes = [t for t, s in sc if s > 14 and 0.2 < t < duracion(v) - 0.2]
    if cortes:
        return False, f"scene cut at {cortes[0]:.2f} s"
    if cabeza:
        m = np.asarray(Image.open(MASTER).convert("RGB").resize((96, 172))).astype(float)
        ref = np.array([m[2:8, 2:8].mean((0, 1)), m[2:8, -8:-2].mean((0, 1)), m[-8:-2, 2:8].mean((0, 1)), m[-8:-2, -8:-2].mean((0, 1))])
        for k, f in enumerate(frames(v)):
            esq = np.array([f[2:8, 2:8].mean((0, 1)), f[2:8, -8:-2].mean((0, 1)), f[-8:-2, 2:8].mean((0, 1)), f[-8:-2, -8:-2].mean((0, 1))])
            dist = np.abs(esq - ref).mean(1).max()
            if dist > 45:
                return False, f"background changed (frame {k}, corner diff {dist:.0f})"
            # the head must never reach the clip's sides (it would show cut when small)
            h_ = f.shape[0]; col = np.asarray(Image.open(MASTER).convert("RGB").resize((96, h_))).astype(float)
            lados = max((np.abs(f[:, :2] - col[:, :2]).mean((1, 2)) > 40).mean(), (np.abs(f[:, -2:] - col[:, -2:]).mean((1, 2)) > 40).mean())
            if lados > 0.06:
                return False, f"head touches the clip side (frame {k}, {lados:.0%} of the edge)"
    return True, "ok"


def prompt_cabeza(lid):
    d = MM.get("acting", {}).get(lid, "Expressive and natural, small head bobs, natural blinks.")
    nunca = ", ".join(PJE.get("nunca", []))
    return f"""subject_definitions:
Image 1 is the host: {PJE.get('descripcion', '')} {PJE.get('identidad_fija', '')}

summary:
One continuous locked-off vertical shot, no cuts: the host's floating head, exactly as in Image 1, talks straight to the lens over the same plain gradient background as Image 1.

detailed_description:
The head stays small in the frame with wide empty background on every side, exactly as in the first frame: it never moves closer to the camera, never grows, the whole head, ears and hair always inside the frame. Only the head, no neck, no body, no hands. Personality: {PJE.get('voz', {}).get('descripcion', '') if isinstance(PJE.get('voz'), dict) else ''}. {PJE.get('mirada', '')}
Acting: {d}
The host says in English, lips matching every word of the soundtrack: "{TXT[lid]}"

avoid:
cuts, scene changes, a different background, {nunca}, camera movement, zoom, subtitles, on-screen text"""


def mate(src, lid, cola=0.4):
    """1080x1920 cut-out with alpha (last frame held `cola` s)."""
    tmp = GEN / f"{lid}_1080.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", f"tpad=stop_mode=clone:stop_duration={cola},"
                    "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920", "-r", "24", "-an", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(tmp)], check=True)
    out = carpeta / "mates" / f"mm_{lid}.mov"
    subprocess.run([PY_PORTABLE, str(MOTION_DNA / "tools" / "video_matte.py"), str(tmp), str(out), "--size", "1080x1920", "--fps", "24"],
                   check=True, stdout=subprocess.DEVNULL)
    return out


def linea_de(c):
    """The line a host clip belongs to: the last line starting at or before the clip (a long line can have two slots)."""
    ids = sorted(T["ini"], key=lambda k: T["ini"][k])
    return [k for k in ids if T["ini"][k] <= c["ini"] + 0.05][-1]


def visible(c):
    seg = c["fin"] - c["ini"]
    for a, b in R["host"].get("fuera", []):
        seg -= max(0, min(c["fin"], b) - max(c["ini"], a))
    return seg > 0.3


# ---------------- plan ----------------
fin_voz = T.get("fin") or duracion(VOZ)
trabajo = []
con = MM.get("concepto")
for c in R["host"]["clips"]:
    if not visible(c):
        continue
    lid = linea_de(c); a, b = c["ini"], min(c["fin"], fin_voz + 0.3)
    if trabajo and trabajo[-1]["lid"] == lid:   # two slots of one line: one generation
        trabajo[-1]["fin"] = b
    else:
        trabajo.append({"lid": lid, "ini": a, "fin": b})
for t in trabajo:
    t["tipo"] = "concepto" if con and con["linea"] == t["lid"] else ("ref" if t["fin"] - t["ini"] <= MAX_REF else "lipsync")
total = sum(max(5.0, t["fin"] - t["ini"]) if t["tipo"] == "lipsync" else t["fin"] - t["ini"] for t in trabajo)
print(f"{carpeta.name}: {len(trabajo)} clips, {total:.1f} s generated, about USD {total * USD_S:.2f} (+ retries)")
for t in trabajo:
    print(f"  {t['lid']} {t['ini']:.2f}-{t['fin']:.2f} ({t['fin'] - t['ini']:.2f} s) {t['tipo']}")

if PAGAR:
    KEY = clave(); head = jpg(MASTER); head_m = jpg(con_margen(MASTER)); usd = 0.0; estado = {}
    ep = GEN / "estado.json"
    if ep.exists():
        estado = json.loads(ep.read_text(encoding="utf-8"))
    for t in trabajo:
        lid = t["lid"]
        if SOLO and lid not in SOLO:
            continue
        if estado.get(lid, {}).get("ok") and not SOLO:
            continue
        dur = round(t["fin"] - t["ini"], 3)
        out = GEN / f"{lid}.mp4"
        hecho, motivo, tipo = False, "", t["tipo"]
        if tipo == "concepto":
            aud = audio(t["ini"], t["fin"], GEN / f"{lid}.mp3")
            ref2 = jpg(carpeta / con["ref"]) if not Path(con["ref"]).is_absolute() else jpg(con["ref"])
            for intento in range(2):
                body = {"prompt": con["prompt"].replace("{TEXTO}", TXT[lid]), "prompt_expansion_mode": "disabled", "reference_image_urls": [head, ref2],
                        "target_audio_url": aud, "duration": dur, "resolution": "768P", "aspect_ratio": "9:16"}
                correr("minimax/h3-max/reference-to-video", body, out); usd += gasto(f"minimax concept {lid}", dur)
                hecho, motivo = revisar(out, cabeza=False)
                print(f"  {lid} concept try {intento + 1}: {motivo}", flush=True)
                if hecho:
                    break
            if hecho:
                shutil.copy2(out, carpeta / "clips" / f"mm_concepto_{lid}.mp4")
        else:
            if tipo == "ref":
                aud = audio(t["ini"], t["fin"], GEN / f"{lid}.mp3")
                for intento in range(2):
                    body = {"prompt": prompt_cabeza(lid), "prompt_expansion_mode": "disabled", "image_url": head_m, "reference_image_urls": [head],
                            "target_audio_url": aud, "duration": dur, "resolution": "768P"}
                    correr("minimax/h3-max/reference-to-video", body, out); usd += gasto(f"minimax ref {lid}", dur)
                    hecho, motivo = revisar(out)
                    print(f"  {lid} ref try {intento + 1}: {motivo}", flush=True)
                    if hecho:
                        break
            if not hecho:   # long line, or reference-to-video broke the look twice
                tipo = "lipsync"
                aud = audio(t["ini"], t["fin"], GEN / f"{lid}_ls.mp3", minimo=5.0)
                correr("minimax/h3-max/lip-sync/image-to-video", {"image_url": head_m, "audio_url": aud, "resolution": "768P"}, out)
                usd += gasto(f"minimax lipsync {lid}", max(5.0, dur))
                hecho, motivo = revisar(out)
                print(f"  {lid} lipsync: {motivo}", flush=True)
            mate(out, lid)
        estado[lid] = {"ok": hecho, "tipo": tipo, "motivo": motivo, "ini": t["ini"], "fin": t["fin"]}
        ep.write_text(json.dumps(estado, indent=1), encoding="utf-8")
    print(f"spent about USD {usd:.2f}")

# ---------------- edit (reaccion.minimax.json) + render ----------------
if MONTAR:
    estado = json.loads((GEN / "estado.json").read_text(encoding="utf-8"))
    M = json.loads(json.dumps(R))
    for c in M["host"]["clips"]:
        lid = linea_de(c); e = estado.get(lid)
        if e and e["tipo"] != "concepto" and (carpeta / "mates" / f"mm_{lid}.mov").exists():
            c["mate"] = f"mates/mm_{lid}.mov"; c["desde"] = round(c["ini"] - e["ini"], 3)
    for lid, e in estado.items():
        if e["tipo"] == "concepto" and e["ok"]:
            a, b = e["ini"], e["fin"]; pl = []
            for p in M["planos"]:
                if p["fin"] <= a or p["ini"] >= b:
                    pl.append(p); continue
                if p["ini"] < a:
                    q = dict(p); q["fin"] = a; pl.append(q)
                if p["fin"] > b:
                    q = dict(p); q["desde"] = round(p["desde"] + (b - p["ini"]), 3); q["ini"] = b; pl.append(q)
            pl.append({"src": f"clips/mm_concepto_{lid}.mp4", "ini": a, "fin": b, "desde": 0.0, "credito": "AI-GENERATED", "modo": "full",
                       "subir": False, "zoom": [1.0, 1.04], "foco": [0.5, 0.5], "y_obj": 0.5})
            pl = sorted(pl, key=lambda p: p["ini"])
            # a sliver (< 1.2 s) left by the cut goes to its neighbour: N01 had a 0.4 s flash before the concept shot (QA 2026-11-20)
            k = 0
            while k < len(pl):
                p = pl[k]
                if p["fin"] - p["ini"] < 1.2 and "mm_concepto" not in p["src"]:
                    nxt = pl[k + 1] if k + 1 < len(pl) else None
                    prv = pl[k - 1] if k else None
                    if prv is not None and "mm_concepto" not in prv["src"]:
                        prv["fin"] = p["fin"]
                    elif nxt is not None and "mm_concepto" not in nxt["src"] and nxt["desde"] >= p["fin"] - p["ini"]:
                        nxt["desde"] = round(nxt["desde"] - (p["fin"] - p["ini"]), 3); nxt["ini"] = p["ini"]
                    else:
                        k += 1; continue
                    pl.pop(k); continue
                k += 1
            M["planos"] = pl
            M["host"]["fuera"] = sorted(M["host"].get("fuera", []) + [[a, b]])
    (carpeta / "reaccion.minimax.json").write_text(json.dumps(M, indent=1, ensure_ascii=False), encoding="utf-8")
    base = carpeta / "reaccion.json"; guard = carpeta / "reaccion.antes_minimax.json"
    shutil.copy2(base, guard); shutil.copy2(carpeta / "reaccion.minimax.json", base)
    try:
        subprocess.run([sys.executable, str(Path(__file__).parent / "build_reaccion_ae.py"), str(carpeta), "--render"], check=True)
    finally:
        shutil.copy2(guard, base); guard.unlink()
    v = max((p for p in carpeta.glob(f"{pj['slug']}_v*.mp4") if "minimax" not in p.name), key=lambda p: p.stat().st_mtime)
    dest = v.with_name(v.stem + "_minimax.mp4"); v.replace(dest); print("rendered", dest)
