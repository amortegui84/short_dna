"""Reaction format (news) assembled in After Effects with Motion DNA: the delivered edit (CCC rule 2026-11-17: every video is
built in AE; engine/reaccion.py is only a Python preview). Reads the same <project>/reaccion.json as the preview, so the
framing, cuts, cards and caption timing match it; ae/ccc_reaccion.jsx builds the comp, Motion DNA adds the sound cues and
check_layout runs on the result. Writes ae/<slug>.aep and datos_ae.json (comp name), so engine/render_ae.py renders it.
Usage: python build_reaccion_ae.py <project> [--render]"""
import json, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import reaccion as RX  # noqa: E402
from comun import duracion, proyecto  # noqa: E402

W, H, FPS = RX.W, RX.H, RX.FPS
carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta)
R = json.loads((carpeta / "reaccion.json").read_text(encoding="utf-8"))
RX.ESTILO.update({k: (tuple(v) if isinstance(v, list) else v) for k, v in R.get("estilo", {}).items()})
E = RX.ESTILO
slug = pj["slug"]; COMP = f"{slug} reaction"
voz = carpeta / R["voz"]; total = R.get("duracion") or duracion(voz) + R.get("cola", 1.2)
media = carpeta / "ae" / "media"; media.mkdir(parents=True, exist_ok=True)
avisos = []

def para_ae(src):
    """After Effects reads no VP9 or AV1 (it imports them as audio only): an H.264 copy for AE in ae/media/footage, the
    original stays as it is."""
    if src.suffix.lower() in (".jpg", ".png", ".jpeg", ".webp"):
        return src
    cod = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "csv=p=0", str(src)],
                         capture_output=True, text=True).stdout.strip()
    if cod in ("h264", "hevc", "prores", "mpeg4", "mjpeg"):
        return src
    out = media / "footage" / f"{src.stem}_h264.mp4"; out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        print("H.264 copy for AE:", src.name, f"({cod})", flush=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-c:v", "libx264", "-crf", "16", "-preset", "fast",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(out)], check=True)
    return out


# ---------- footage: per plan, the window the preview shows, sampled every 5 frames (scale + top-left offset in AE)
planos = []
for p in sorted(R["planos"], key=lambda p: p["ini"]):
    if p.get("tipo") == "mapa" or p.get("marcas") or p.get("congelar") is not None:
        avisos.append(f"plan at {p['ini']}: mapa/marcas/congelar not built in AE yet")
    src = (carpeta / p["src"]).resolve()
    src = para_ae(src)
    foto = src.suffix.lower() in (".jpg", ".png", ".jpeg", ".webp")
    sw, sh = ImageOps.exif_transpose(Image.open(src)).size if foto else RX.tam_video(src)
    modo = p.get("modo") or ("full" if sh / sw > 1.2 else "caja")
    z = p.get("zoom", [1.0, 1.06]); zmax = max(z); foco = p.get("foco", [0.5, 0.5]); f1 = p.get("foco_fin", foco)
    s = max(W / sw, H / sh) * zmax if modo == "full" else W / sw * zmax
    tw, th = sw * s, sh * s
    cw, ch = (W, H) if modo == "full" else (W, int(th / zmax))
    yo = p.get("y_obj", 0.22 if modo == "full" else 0.5)
    dur = p["fin"] - p["ini"]; claves = []
    n = max(2, int(dur * FPS / 5) + 1)
    for i in range(n + 1):
        k = min(1.0, i / n); zz = z[0] + (z[1] - z[0]) * RX.SETTLE(k)
        vw, vh = min(cw * zmax / zz, tw), min(ch * zmax / zz, th)
        fx, fy = foco[0] + (f1[0] - foco[0]) * k, foco[1] + (f1[1] - foco[1]) * k
        cx, cy = fx * tw, fy * th
        x0 = min(max(cx - vw / 2, 0), tw - vw); y0 = min(max(cy - vh * yo, 0), th - vh)
        esc = cw / vw * s   # displayed px per source px
        if modo == "full" and p.get("subir", True):
            sube = (cy - y0) / vh * H - yo * H
            if sube >= 12:
                avisos.append(f"plan at {p['ini']}: 'subir' lift not built in AE (set subir false or check the frame)")
        claves.append([round(p["ini"] + k * dur, 4), round(esc * 100, 4), round(-x0 / s * esc, 2), round(-y0 / s * esc, 2)])
    planos.append({"src": src.as_posix(), "ini": p["ini"], "fin": p["fin"], "desde": p.get("desde", 0), "vel": p.get("vel", 1.0),
                   "modo": modo, "ch": ch, "y": int(p.get("y", 540 - ch / 2)), "claves": claves, "foto": foto,
                   "audio": p.get("audio"), "fondo_esc": round(max(W / sw, H / sh) * 100, 3)})

# credits: runs of the same text
creditos = []
for p in sorted(R["planos"], key=lambda p: p["ini"]):
    c = p.get("credito")
    if not c:
        continue
    if creditos and creditos[-1]["txt"] == c.upper() and abs(creditos[-1]["fin"] - p["ini"]) < 0.05:
        creditos[-1]["fin"] = p["fin"]
    else:
        creditos.append({"txt": c.upper(), "ini": p["ini"], "fin": p["fin"]})

# ---------- cards (pre-drawn paper cards, animated in AE)
tarjetas = []
for i, t in enumerate(R.get("tarjetas", [])):
    img = RX.tarjeta_img(t); f = media / f"card_{i + 1:02d}.png"; Image.fromarray(img).save(f)
    tarjetas.append({"img": f.as_posix(), "ini": t["ini"], "fin": t["fin"], "y": t.get("y", 560), "w": img.shape[1], "h": img.shape[0]})
tit = None
if R.get("titulo"):
    ti = RX.titulo_img(R["titulo"]); f = media / "titulo.png"; Image.fromarray(ti).save(f)
    tit = {"img": f.as_posix(), "y": R["titulo"].get("y", 1130), "desde": R["titulo"].get("desde", 0), "hasta": R["titulo"].get("hasta", total)}

# ---------- host
host = R["host"]; alto_p, alto_g = host.get("alto", 1000), host.get("alto_grande", 1500)
spans = sorted([list(s) for s in host.get("fuera", [])] + [[p["ini"], p["fin"]] for p in R["planos"] if p.get("cabeza") is False])
fuera = []
for a, b in spans:
    if fuera and a <= fuera[-1][1] + 0.05:
        fuera[-1][1] = max(fuera[-1][1], b)
    else:
        fuera.append([a, b])
clips = []
for c in host.get("clips", []):
    mate = (carpeta / c["mate"]).resolve()
    if mate.suffix.lower() == ".png":   # the host still (edit-first placeholder): its alpha box down to the bottom edge
        _a = np.array(Image.open(mate).convert("RGBA"))[..., 3] > 40; _ys, _xs = np.nonzero(_a)
        bx, by = max(0, int(_xs.min()) - 24), max(0, int(_ys.min()) - 24); bw = (min(W, int(_xs.max()) + 24) - bx) // 2 * 2; bh = (H - by) // 2 * 2
    else:
        bx, by, bw, bh = RX.caja_alfa(mate)
    bh = int(bh * host.get("pecho", 0.62)) // 2 * 2
    clips.append({"mate": mate.as_posix(), "ini": c["ini"], "fin": c["fin"], "desde": c.get("desde", 0), "caja": [bx, by, bw, bh]})


def nivel_grande(t):
    v = 0.0
    for a, b in host.get("grande", []):
        if a - RX.SWEEP <= t <= b + RX.SWEEP:
            v = max(v, RX.SETTLE((t - (a - RX.SWEEP)) / RX.SWEEP) if t < a else (RX.SETTLE(((b + RX.SWEEP) - t) / RX.SWEEP) if t > b else 1.0))
    return v


def nivel_fuera(t):
    return 1.0 if any(a <= t < b for a, b in fuera) else 0.0


# ---------- captions: the preview's choice per frame (block beside the small head, else the centred chunk), merged in runs
grupos = RX.subtitulos(voz, carpeta)
frases = RX.bloques(grupos, R.get("sub_bloque", {}).get("palabras", 9))
bq = R.get("sub_bloque"); subs = []
for n in range(int(total * FPS)):
    t = n / FPS; g, f = nivel_grande(t), nivel_fuera(t); item = None
    if bq and g < 0.5 and f < 0.5:
        fr = next((b for b in frases if b[0][1] - 0.05 <= t < b[-1][2] + 0.25), None)
        if fr:
            item = ("bloque", id(fr), fr)
    else:
        gr = next((gp for gp in grupos if gp[0][1] - 0.05 <= t < gp[-1][2] + 0.12), None)
        if gr:
            ys = R.get("y_sub", 860) + (R.get("y_sub_grande", 1560) - R.get("y_sub", 860)) * g * (1 - f)
            xs = 0.5 if f >= 0.5 else R.get("x_sub", 0.5) + (0.5 - R.get("x_sub", 0.5)) * g   # head gone: centred
            # QA 2026-11-19 (X01 v1 21 s and 46 s): a card on screen sat on the caption; the caption drops below the card
            for tj in tarjetas:
                if tj["ini"] - 0.3 <= t < tj["fin"] + 0.3 and tj["y"] - 70 < ys < tj["y"] + tj["h"] + 70:   # y = the card's top
                    ys = tj["y"] + tj["h"] + 80
            item = ("linea", id(gr), gr, round(xs, 3), round(ys))
    if item is None:
        continue
    if subs and subs[-1]["key"] == item[:2] + item[3:] and abs(subs[-1]["fin"] - t) < 1.5 / FPS:
        subs[-1]["fin"] = round(t + 1 / FPS, 4)
    else:
        ws = [{"w": (w[0].upper() if E["sub_mayus"] else w[0]).strip(";:" if item[0] == "bloque" else ".,;:"), "s": round(w[1], 3)} for w in item[2]]
        d = {"key": item[:2] + item[3:], "tipo": item[0], "ini": round(t, 4), "fin": round(t + 1 / FPS, 4), "words": ws}
        if item[0] == "linea":
            d.update(x=item[3] * W, y=item[4])
        else:
            d.update(x=bq.get("x", 540) + 10, y=bq.get("y", 1450), ancho=bq.get("ancho", 480))
        subs.append(d)
for s_ in subs:
    s_.pop("key")

# After Effects keeps the old length of a re-recorded wav at the same path (2026-11-20: N04/N09 voice cut at the old 43.6/41.1 s):
# AE gets a copy named after the file's size+mtime, so a new voice is always a new file to it
import shutil  # noqa: E402
_st = voz.stat(); voz_ae = voz.with_name(f"{voz.stem}_ae_{_st.st_size}_{int(_st.st_mtime)}{voz.suffix}")
if not voz_ae.exists():
    for _old in voz.parent.glob(f"{voz.stem}_ae_*{voz.suffix}"):
        _old.unlink(missing_ok=True)
    shutil.copy2(voz, voz_ae)
col = lambda c: "#%02X%02X%02X" % tuple(c[:3])
DATA = {"comp": COMP, "total": round(total, 3), "planos": planos, "creditos": creditos, "tarjetas": tarjetas, "titulo": tit,
        "clips": clips, "alto_p": alto_p, "alto_g": alto_g, "host_x": host.get("x", 0.30), "grande": host.get("grande", []),
        "sweep": RX.SWEEP, "fuera": fuera, "salto": E.get("corte") == "salto", "subs": subs,
        "voz": voz_ae.as_posix(), "musica": (carpeta / R["musica"]).as_posix() if R.get("musica") else None, "musica_db": R.get("musica_db", -6),
        "estilo": {"sub_tam": E["sub_tam"], "bloque_tam": E.get("bloque_tam", E["sub_tam"]), "sub_color": col(E["sub_color"]),
                   "sub_activa": col(E["sub_activa"]), "sub_borde": E["sub_borde"], "papel": col(E["papel"])}}
(carpeta / "datos_ae.json").write_text(json.dumps(DATA, indent=1), encoding="utf-8")
print(COMP, "|", len(planos), "plans |", len(clips), "host clips |", len(tarjetas), "cards |", len(subs), "caption layers | total", total)
for a in avisos:
    print("WARNING:", a)
if "--solo-datos" in sys.argv:
    sys.exit()

# ---------- build in After Effects
sys.path.insert(0, r"D:\motion category ai library\tools\mcp")
import ss_motion_mcp as M  # noqa: E402
_r = M.run_jsx
M.run_jsx = lambda body, *a, **k: _r("app.beginSuppressDialogs();\ntry {\n" + body + "\n} finally { app.endSuppressDialogs(false); }", *a, **k)
AEP = (carpeta / "ae" / f"{slug}.aep").as_posix()
print(M.run_jsx(f"""var f = new File("{AEP}");
if (app.project.file && app.project.file.fsName.replace(/\\\\/g, "/") === f.fsName.replace(/\\\\/g, "/")) return "ya abierto";
if (app.project.dirty && app.project.file) app.project.save();
if (f.exists) app.open(f); else {{ app.newProject(); app.project.save(f); }}
try {{ app.project.gpuAccelType = GpuAccelType.SOFTWARE; }} catch (e) {{}}
return app.project.file.fsName;""", timeout=240))
r = M.run_jsx((HERE.parent / "ae" / "ccc_reaccion.jsx").read_text(encoding="utf-8") + chr(10) +
              f"var r = REACCION.build({json.dumps(DATA)}); app.project.save(); return r;", timeout=1800, includes=())
print(r.splitlines()[0])
for ln in r.splitlines()[1:]:
    if ln.startswith("WARN"):
        print(ln)
SON = json.loads((carpeta.parents[1] / "styles" / "ccc_bricolage.json").read_text(encoding="utf-8")).get("sonidos", {}) \
    if (carpeta.parents[1] / "styles" / "ccc_bricolage.json").exists() else {}
cues = []
for ln in r.splitlines()[1:]:
    q = ln.split(";")
    if len(q) == 5 and q[0] == "CUE":
        cues.append({"t": float(q[1]), "sfx": SON.get(q[2], q[2]), "gain": float(q[3]), "why": q[4]})
cues.sort(key=lambda c: c["t"])
print(str(M.t_add_sound(cues=cues, comp=COMP, auto=False))[:160])
print(M.t_check_layout(comps=[COMP]))
print(M.run_jsx('app.project.save(); return "guardado";', includes=()))
if "--render" in sys.argv:
    subprocess.run([sys.executable, str(HERE / "render_ae.py"), str(carpeta)], check=True)
