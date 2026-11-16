"""Reaction format (test 2026-11-15): the narrator, cut out with no background, sits in a corner and reacts to a real news
story while the footage plays full screen behind him; he goes big for the hook and the verdict. Built frame by frame in
Python (PIL + numpy) and encoded with ffmpeg, so a 60 s Short renders in a few minutes without After Effects.

Everything comes from <project>/reaccion.json (see docs/REACTION_FORMAT.md):
  voz        the narration (one file, already at its final pace)
  musica     optional bed, with its gain in dB
  host       {"clips": [{"mate": "mates/R01.mov", "ini": s, "fin": s, "desde": s}], "alto": px, "margen": px,
              "grande": [[ini, fin], ...]}   the cut-out clips in order; "grande" = the spans where he fills the frame
  planos     [{"src", "ini", "fin", "desde", "vel", "modo": "full"|"caja", "zoom": [a, b], "foco": [fx, fy], "foco_fin": [fx, fy], "congelar": s,
              "audio": dB or null, "credito": "...", "marcas": [{"tipo": "circulo"|"flecha", "x", "y", "r", "t"}]}]
  tarjetas   [{"tipo": "comentario"|"titular"|"cita", "texto", "autor", "fuente", "ini", "fin", "y"}]
  y_sub      subtitle line centre (default 1140: above the host head, inside the clean area x 65-888, y 288-1248)
Every time is in seconds of the final video. Footage is never filtered: the tape texture goes on the frame and the host only.
Usage: python reaccion.py <project> [--hasta 12] [--cuadro 7.5 out.png]"""
import json, math, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from comun import duracion, palabras  # noqa: E402

W, H, FPS = 1080, 1920, 30
FONTS = Path("C:/Windows/Fonts")
F_IMPACT = str(FONTS / "impact.ttf")
F_MONO = str(FONTS / "courbd.ttf")
F_SERIF = str(FONTS / "InstrumentSerif-Italic.ttf")
TINTA, HUESO, AMARILLO, ROJO = (7, 22, 33), (232, 223, 200), (244, 224, 124), (186, 24, 51)


def bezier(p1x, p1y, p2x, p2y):
    """Cubic-bezier easing (Motion DNA tokens) as a function of t in [0, 1]."""
    def f(t):
        t = min(1.0, max(0.0, t)); lo, hi = 0.0, 1.0
        for _ in range(30):
            m = (lo + hi) / 2
            x = 3 * (1 - m) ** 2 * m * p1x + 3 * (1 - m) * m ** 2 * p2x + m ** 3
            lo, hi = (m, hi) if x < t else (lo, m)
        m = (lo + hi) / 2
        return 3 * (1 - m) ** 2 * m * p1y + 3 * (1 - m) * m ** 2 * p2y + m ** 3
    return f


LAND = bezier(0.12, 0.9, 0.28, 1)      # entrances (Arrive, 14 f)
POP = bezier(0.34, 1.45, 0.64, 1)      # cards: scale-up with a ~5 % overshoot
SETTLE = bezier(0.3, 0, 0.1, 1)        # general moves (host small <-> big)
ARRIVE, SWEEP = 14 / 30, 21 / 30


def fuente(path, size, _c={}):
    return _c.setdefault((path, size), ImageFont.truetype(path, size))


class Lector:
    """Frames of a video through an ffmpeg pipe, read in order (rgb or rgba), cropped/scaled by ffmpeg."""
    def __init__(self, src, desde, w, h, vf="", rgba=False, vel=1.0):
        self.w, self.h, self.c = w, h, 4 if rgba else 3
        chain = (f"setpts=PTS/{vel}," if vel != 1 else "") + (vf + "," if vf else "") + f"scale={w}:{h},fps={FPS}"
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{desde:.3f}", "-i", str(src), "-an", "-vf", chain,
                                   "-pix_fmt", "rgba" if rgba else "rgb24", "-f", "rawvideo", "-"], stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL)
        self.ultimo = None; self.n = 0

    def cuadro(self, i):
        """Frame i of this reader (i only grows); past the end the last frame holds."""
        while self.n <= i:
            b = self.p.stdout.read(self.w * self.h * self.c)
            if len(b) < self.w * self.h * self.c:
                break
            self.ultimo = np.frombuffer(b, np.uint8).reshape(self.h, self.w, self.c); self.n += 1
        return self.ultimo

    def cerrar(self):
        self.p.kill()


def tam_video(src):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0",
                        str(src)], capture_output=True, text=True).stdout.strip().split(",")
    return int(o[0]), int(o[1])


def caja_alfa(mate):
    """Union of the alpha bounding box over 6 frames of a cut-out clip -> (x, y, w, h) in its 1080x1920 frame."""
    d = duracion(mate); x0, y0, x1, y1 = W, H, 0, 0
    for k in range(6):
        b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{d * (k + 0.5) / 6:.2f}", "-i", str(mate), "-frames:v", "1",
                            "-vf", "alphaextract,scale=270:480", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
        a = np.frombuffer(b, np.uint8).reshape(480, 270) > 40
        ys, xs = np.nonzero(a)
        if len(xs):
            x0, y0, x1, y1 = min(x0, xs.min() * 4), min(y0, ys.min() * 4), max(x1, xs.max() * 4 + 4), max(y1, ys.max() * 4 + 4)
    pad = 24
    x0, y0, x1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad)
    return int(x0), int(y0), int(x1 - x0) // 2 * 2, int(H - y0) // 2 * 2   # down to the bottom edge: the cut-out sits on it


def pegar(base, img, x, y, alfa=1.0):
    """Alpha-composite an RGBA numpy image onto the RGB base at (x, y), clipped to the frame."""
    h, w = img.shape[:2]
    bx0, by0, bx1, by1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if bx1 <= bx0 or by1 <= by0:
        return
    sub = img[by0 - y:by1 - y, bx0 - x:bx1 - x].astype(np.float32)
    a = sub[..., 3:4] / 255.0 * alfa
    roi = base[by0:by1, bx0:bx1].astype(np.float32)
    base[by0:by1, bx0:bx1] = (roi * (1 - a) + sub[..., :3] * a).astype(np.uint8)


def texto_rgba(txt, font, color, borde=0, color_borde=(0, 0, 0)):
    f = font; l, t, r, b = f.getbbox(txt, stroke_width=borde)
    im = Image.new("RGBA", (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - l, 2 - t), txt, font=f, fill=color, stroke_width=borde, stroke_fill=color_borde)
    return im


def envolver(txt, font, ancho):
    lineas, cur = [], ""
    for w in txt.split():
        prueba = (cur + " " + w).strip()
        if font.getlength(prueba) > ancho and cur:
            lineas.append(cur); cur = w
        else:
            cur = prueba
    return lineas + ([cur] if cur else [])


def tarjeta_img(t):
    """A comment / headline / quote card as RGBA (paper card, tape strip, red rule), pre-rendered once."""
    ancho = 860
    if t["tipo"] == "titular":
        f = fuente(F_IMPACT, 64); lineas = envolver(t["texto"].upper(), f, ancho - 80); lh = 70
        cab = (t.get("fuente") or "").upper(); fc = fuente(F_MONO, 30)
        alto = 70 + len(lineas) * lh + 60
        im = Image.new("RGBA", (ancho, alto), HUESO + (255,)); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, ancho, 54], fill=TINTA); d.text((28, 12), cab, font=fc, fill=HUESO)
        for k, ln in enumerate(lineas):
            d.text((40, 76 + k * lh), ln, font=f, fill=TINTA)
    else:
        f = fuente(F_SERIF, 58) if t["tipo"] == "cita" else fuente(F_MONO, 40)
        lh = 64 if t["tipo"] == "cita" else 50
        texto = ("\u201c" + t["texto"] + "\u201d") if t["tipo"] == "cita" else t["texto"]
        lineas = envolver(texto, f, ancho - 90); fa = fuente(F_MONO, 30)
        alto = 50 + len(lineas) * lh + 80
        im = Image.new("RGBA", (ancho, alto), (250, 246, 236, 255) if t["tipo"] == "comentario" else TINTA + (255,))
        d = ImageDraw.Draw(im); col = TINTA if t["tipo"] == "comentario" else HUESO
        d.rectangle([0, 0, 10, alto], fill=ROJO)
        for k, ln in enumerate(lineas):
            d.text((44, 34 + k * lh), ln, font=f, fill=col)
        d.text((44, alto - 58), "\u2014 " + (t.get("autor") or ""), font=fa, fill=ROJO if t["tipo"] == "comentario" else AMARILLO)
    # tape strip on the top edge, slightly rotated card
    tape = Image.new("RGBA", (190, 46), (244, 224, 124, 190))
    im2 = Image.new("RGBA", (im.width + 40, im.height + 60), (0, 0, 0, 0))
    sombra = Image.new("RGBA", im.size, (0, 0, 0, 150)).filter(ImageFilter.GaussianBlur(6))
    im2.alpha_composite(sombra, (28, 40)); im2.alpha_composite(im, (20, 30)); im2.alpha_composite(tape, (im2.width // 2 - 95, 8))
    return np.array(im2.rotate(t.get("giro", -1.5), resample=Image.BICUBIC, expand=True))


class Plano:
    def __init__(self, p, carpeta):
        self.p = p; src = carpeta / p["src"]; self.src = src
        self.dur = p["fin"] - p["ini"]; self.z = p.get("zoom", [1.0, 1.06]); self.foco = p.get("foco", [0.5, 0.5])
        sw, sh = tam_video(src) if src.suffix.lower() not in (".jpg", ".png", ".jpeg", ".webp") else Image.open(src).size
        self.foto = src.suffix.lower() in (".jpg", ".png", ".jpeg", ".webp")
        self.modo = p.get("modo") or ("full" if sh / sw > 1.2 else "caja")
        zmax = max(self.z)
        if self.modo == "full":   # cover the frame, room for the zoom
            s = max(W / sw, H / sh) * zmax
        else:                     # fit the width; a blurred copy fills the frame behind
            s = W / sw * zmax
        self.tw, self.th = int(sw * s) // 2 * 2, int(sh * s) // 2 * 2
        if self.foto:
            self.img = np.array(Image.open(src).convert("RGB").resize((self.tw, self.th), Image.LANCZOS)); self.lec = None
        else:
            self.lec = Lector(src, p.get("desde", 0), self.tw, self.th, vel=p.get("vel", 1.0))
        self.fondo = None

    def cuadro(self, t):
        u = t - self.p["ini"]
        if self.p.get("congelar") is not None:
            u = min(u, self.p["congelar"])
        src = self.img if self.foto else self.lec.cuadro(int(u * FPS))
        k = u / max(self.dur, 0.01); z = self.z[0] + (self.z[1] - self.z[0]) * SETTLE(k)
        zmax = max(self.z); cw, ch = (W, H) if self.modo == "full" else (W, int(self.th / zmax))
        vw, vh = int(cw * zmax / z), int(ch * zmax / z)   # the window inside the big frame that shows at this zoom
        vw, vh = min(vw, self.tw), min(vh, self.th)
        f1 = self.p.get("foco_fin", self.foco)   # the focus can travel with the object (linear over the plan)
        fx, fy = self.foco[0] + (f1[0] - self.foco[0]) * k, self.foco[1] + (f1[1] - self.foco[1]) * k
        cx, cy = fx * self.tw, fy * self.th
        # the focus lands in the upper part of the frame ("y_obj", default 0.30 for full-frame clips): the selfie host covers
        # the lower half, so what we talk about must sit above him
        yo = self.p.get("y_obj", 0.22 if self.modo == "full" else 0.5)
        x0 = int(min(max(cx - vw / 2, 0), self.tw - vw)); y0 = int(min(max(cy - vh * yo, 0), self.th - vh))
        ven = Image.fromarray(src[y0:y0 + vh, x0:x0 + vw]).resize((cw, ch), Image.BILINEAR)
        if self.modo == "full":
            # a vertical clip at low zoom cannot pan its object up: lift the whole picture instead and fill the strip it
            # leaves at the bottom (behind the host) with a dark blurred copy
            obj_y = (cy - y0) / vh * H; sube = int(max(0, obj_y - yo * H)) if self.p.get("subir", True) else 0
            if sube < 12:
                return np.array(ven), (0, 0, W, H)
            sube = min(sube, int(H * 0.4))
            relleno = np.array(ven.resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR)).astype(np.float32) * 0.4
            base = relleno.astype(np.uint8)
            base[:H - sube] = np.array(ven)[sube:]
            y1 = H - sube; g = np.linspace(1, 0, 120)[:, None, None]   # soft edge where the lifted picture meets the fill
            base[y1 - 120:y1] = (base[y1 - 120:y1] * g + relleno[y1 - 120:y1] * (1 - g)).astype(np.uint8)
            return base, (0, 0, W, H - sube)
        # boxed: blurred, darkened copy behind (fills the 9:16), the clip centred in the footage zone
        fondo = Image.fromarray(src).resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR)
        base = (np.array(fondo).astype(np.float32) * 0.45).astype(np.uint8)
        y = int(self.p.get("y", 540 - ch / 2))
        base[max(0, y):y + ch] = np.array(ven)[max(0, -y):H - y][:max(0, min(ch, H - y))]
        return base, (0, y, W, ch)


def dibujar_marca(base, m, t):
    """A red hand-drawn circle (or arrow) that draws itself on in 0.45 s at m["t"], on the footage."""
    u = (t - m["t"]) / 0.45
    if u <= 0 or t > m.get("hasta", m["t"] + 3.0):
        return
    im = Image.fromarray(base); d = ImageDraw.Draw(im); k = LAND(u)
    if m["tipo"] == "circulo":
        r = m.get("r", 120); pts = []
        for i in range(int(64 * k) + 1):
            a = -1.9 + i / 64 * 2 * math.pi * 1.08
            rr = r * (1 + 0.06 * math.sin(i * 0.7))
            pts.append((m["x"] + rr * math.cos(a), m["y"] + rr * 0.86 * math.sin(a)))
        if len(pts) > 1:
            d.line(pts, fill=ROJO, width=12, joint="curve")
    else:
        x0, y0 = m["x"] - m.get("dx", -220), m["y"] - m.get("dy", 220); x1 = x0 + (m["x"] - x0) * k; y1 = y0 + (m["y"] - y0) * k
        d.line([(x0, y0), (x1, y1)], fill=ROJO, width=14)
        if k > 0.95:
            ang = math.atan2(m["y"] - y0, m["x"] - x0)
            for s in (2.6, -2.6):
                d.line([(x1, y1), (x1 + 60 * math.cos(ang + s), y1 + 60 * math.sin(ang + s))], fill=ROJO, width=14)
    base[:] = np.array(im)


def subtitulos(voz, carpeta):
    cache = carpeta / "vo" / "palabras_reaccion.json"
    if cache.exists() and cache.stat().st_mtime > Path(voz).stat().st_mtime:
        ws = json.loads(cache.read_text(encoding="utf-8"))
    else:
        ws = [list(w) for w in palabras(voz)]; cache.write_text(json.dumps(ws), encoding="utf-8")
    pequenas = {"a", "an", "the", "at", "of", "to", "in", "on", "is", "was", "and", "but", "or", "with", "into", "her", "it", "be"}
    grupos, cur = [], []
    for w in ws:   # chunks of up to 3 words, broken at punctuation; a chunk never ends on a small word (it carries on)
        cur.append(w)
        corta = len(cur) >= 3 or w[0][-1:] in ".,?!:;" or len(" ".join(x[0] for x in cur)) > 18
        pequena = w[0].lower().strip(".,?!:;") in pequenas and w[0][-1:] not in ".,?!:;"
        if corta and (not pequena or len(cur) >= 4):
            grupos.append(cur); cur = []
    if cur:
        grupos.append(cur)
    return grupos


def sub_img(grupo, t):
    f = fuente(F_IMPACT, 78)
    piezas = [(w[0].upper().strip(".,;:"), w[1] <= t + 0.02) for w in grupo]
    ancho = sum(f.getlength(p + " ") for p, _ in piezas) + 40
    im = Image.new("RGBA", (int(ancho) + 20, 116), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 10, im.width, 106], fill=(5, 5, 8, 215))
    x = 30; actual = max([i for i, (_, on) in enumerate(piezas) if on] or [0])
    for i, (p, on) in enumerate(piezas):
        d.text((x, 14), p, font=f, fill=AMARILLO if i == actual else HUESO, stroke_width=3, stroke_fill=(0, 0, 0))
        x += f.getlength(p + " ")
    return np.array(im)


def textura(base, n, zona, mascara=None):
    """Tape texture on the host (only inside his silhouette when a mask is given: on the whole box it drew a dark
    rectangle around him, review 2026-11-15) and the frame edges: scanlines, a little noise, a rolling tracking line."""
    x, y, w, h = zona
    orig = base[y:y + h, x:x + w].copy()
    roi = base[y:y + h, x:x + w].astype(np.int16)
    roi[::3] -= 10
    rng = np.random.default_rng(n)
    roi += rng.integers(-9, 10, (h, w, 1), dtype=np.int16)
    if n % 97 < 4:   # a tracking line rolls through for 4 frames
        ty = (n * 37) % max(1, h - 30); roi[ty:ty + 18] += 38
    nuevo = np.clip(roi, 0, 255).astype(np.uint8)
    if mascara is not None:
        m = mascara[..., None]; nuevo = (nuevo * m + orig * (1 - m)).astype(np.uint8)
    base[y:y + h, x:x + w] = nuevo


def borde_suave(arr, px=2):
    """Choke the cut-out alpha by ~1 px and feather it, so no hard or dark rim shows against bright footage."""
    a = Image.fromarray(arr[..., 3]).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(px))
    out = arr.copy(); out[..., 3] = np.array(a); return out


def main():
    carpeta = Path(sys.argv[1]).resolve()
    R = json.loads((carpeta / "reaccion.json").read_text(encoding="utf-8"))
    voz = carpeta / R["voz"]; total = R.get("duracion") or duracion(voz) + R.get("cola", 1.2)
    hasta = float(sys.argv[sys.argv.index("--hasta") + 1]) if "--hasta" in sys.argv else total
    cuadro_t = float(sys.argv[sys.argv.index("--cuadro") + 1]) if "--cuadro" in sys.argv else None
    grupos = subtitulos(voz, carpeta)
    host = R["host"]; alto_p, margen = host.get("alto", 1000), host.get("margen", 24); alto_g = host.get("alto_grande", 1500)
    planos = sorted(R["planos"], key=lambda p: p["ini"]); abiertos = {}
    tarjetas = [dict(t, img=tarjeta_img(t)) for t in R.get("tarjetas", [])]
    clips = []
    for c in host["clips"]:
        mate = carpeta / c["mate"]
        if not mate.exists():   # stills before the cut-outs exist: footage and cards only
            print("no cut-out yet:", c["mate"]); continue
        bx, by, bw, bh = caja_alfa(mate)
        bh = int(bh * host.get("pecho", 0.62)) // 2 * 2   # selfie framing: head and chest only (the table and lap are cut off)
        s = alto_g / bh; gw, gh = int(bw * s) // 2 * 2, alto_g // 2 * 2
        clips.append(dict(c, caja=(bx, by, bw, bh), gw=gw, gh=gh, lec=None, k=len(clips)))
    grande = host.get("grande", [])

    def nivel_grande(t):   # 0 = small in the corner, 1 = big; animated over SWEEP at the span edges
        v = 0.0
        for a, b in grande:
            if a - SWEEP <= t <= b + SWEEP:
                v = max(v, SETTLE((t - (a - SWEEP)) / SWEEP) if t < a else (SETTLE(((b + SWEEP) - t) / SWEEP) if t > b else 1.0))
        return v

    fuera = host.get("fuera", [])

    def nivel_fuera(t):   # 0 = on screen, 1 = gone below the frame: he ducks out in 0.3 s and comes back up in 0.4 s
        v = 0.0
        for a, b in fuera:
            if a <= t <= b:
                v = max(v, min(SETTLE((t - a) / 0.3), SETTLE((b - t) / 0.4)))
        return v

    out = carpeta / f"{R['slug']}_reaccion.mp4" if cuadro_t is None else None
    tmp = carpeta / "_reaccion_video.mp4"
    enc = None if cuadro_t is not None else subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", str(tmp)], stdin=subprocess.PIPE)
    n0 = int(cuadro_t * FPS) if cuadro_t is not None else 0
    n1 = n0 + 1 if cuadro_t is not None else int(hasta * FPS)
    for n in range(n0, n1):
        t = n / FPS
        base = np.zeros((H, W, 3), np.uint8); base[:] = (11, 17, 22)
        # 1. footage (the plan that covers t; the incoming one cross-dissolves in its first 0.25 s)
        vivos = [p for p in planos if p["ini"] <= t < p["fin"]]
        for p in vivos[-2:]:
            key = id(p)
            if key not in abiertos:
                abiertos[key] = Plano(p, carpeta)
                if cuadro_t is not None and not abiertos[key].foto:   # one still: seek straight to it
                    abiertos[key].lec = Lector(abiertos[key].src, p.get("desde", 0) + (t - p["ini"]) * p.get("vel", 1.0),
                                               abiertos[key].tw, abiertos[key].th, vel=p.get("vel", 1.0))
                    abiertos[key].p = dict(p, ini=t)
            img, _ = abiertos[key].cuadro(t)
            a = min(1.0, (t - p["ini"]) / 0.25) if p is not vivos[0] or len(vivos) == 1 and p["ini"] > 0.01 and p.get("disolver") else 1.0
            base[:] = img if a >= 1 else (base * (1 - a) + img * a).astype(np.uint8)
            for m in p.get("marcas", []):
                dibujar_marca(base, m, t)
            if p.get("congelar") is not None and 0 <= t - p["ini"] - p["congelar"] < 4 / FPS:   # 4-frame flash on the freeze
                base[:] = (base.astype(np.float32) * 0.35 + 255 * 0.65).astype(np.uint8)
        for key in [k for k, pl in abiertos.items() if pl.p["fin"] <= t]:
            if abiertos[key].lec:
                abiertos[key].lec.cerrar()
            del abiertos[key]
        # credit of the footage on screen (top, small)
        cred = next((p.get("credito") for p in reversed(vivos) if p.get("credito")), None)
        if cred:
            pegar(base, np.array(texto_rgba(cred.upper(), fuente(F_MONO, 26), HUESO + (235,), 3)), 40, 250)
        # 2. cards
        for c in tarjetas:
            if c["ini"] <= t < c["fin"]:
                k = POP((t - c["ini"]) / (8 / 30)); salida = min(1.0, (c["fin"] - t) / 0.2)
                img = c["img"]; sc = 0.86 + 0.14 * k
                im = Image.fromarray(img).resize((int(img.shape[1] * sc), int(img.shape[0] * sc)), Image.BILINEAR)
                pegar(base, np.array(im), W // 2 - im.width // 2, int(c.get("y", 560) + (1 - min(k, 1)) * 60), min(max(k, 0) * 1.4, 1.0) * salida)
        # 3. host (cut-out), small in the corner or big
        g = nivel_grande(t)
        clip = next((c for c in clips if c["ini"] <= t < c["fin"]), None)
        # jump cut between clips: a hard cut, every other clip punched in 7 % (the talking-head edit). A cross-dissolve
        # showed two masks at once (review 2026-11-15: "the fades from one background to the other look odd"). Where a
        # cut would jar, the host leaves the frame ("fuera" spans) and the footage plays alone, then he comes back.
        f = nivel_fuera(t)
        def dibujar_host(c):
            fr = c["lec"].cuadro(n - c["n0"])
            if fr is None:
                return
            alto = int((alto_p + (alto_g - alto_p) * g) * (1.07 if c["k"] % 2 else 1.0))
            im = Image.fromarray(fr).resize((int(c["gw"] * alto / c["gh"]), alto), Image.BILINEAR)
            x_peq, x_gr = int(W * host.get("x", 0.30)) - im.width // 2, W // 2 - im.width // 2
            x = int(x_peq + (x_gr - x_peq) * g); y = H - alto + int(alto * f)
            arr = borde_suave(np.array(im)); pegar(base, arr, x, y)
            x0, x1 = max(0, x), min(W, x + arr.shape[1]); h = min(alto, H - y)
            if h > 0:
                textura(base, n, (x0, y, x1 - x0, h), arr[:h, x0 - x:x1 - x, 3].astype(np.float32) / 255)
        if g > 0 and clip:   # big: darken the footage behind him so he reads
            base[:] = (base.astype(np.float32) * (1 - 0.55 * g * (1 - f))).astype(np.uint8)
        if clip:
            if clip["lec"] is None:
                bx, by, bw, bh = clip["caja"]
                d0 = clip.get("desde", 0) + (t - clip["ini"] if cuadro_t is not None else 0)
                clip["lec"] = Lector(carpeta / clip["mate"], d0, clip["gw"], clip["gh"], vf=f"crop={bw}:{bh}:{bx}:{by}", rgba=True)
                clip["n0"] = n
            for c in clips:
                if c is not clip and c["lec"]:
                    c["lec"].cerrar(); c["lec"] = None
            if f < 0.999:
                dibujar_host(clip)
        # 4. subtitles
        gr = next((gp for gp in grupos if gp[0][1] - 0.05 <= t < gp[-1][2] + 0.12), None)
        if gr:
            si = sub_img(gr, t); ys = R.get("y_sub", 860) + (1560 - R.get("y_sub", 860)) * nivel_grande(t) * (1 - nivel_fuera(t))   # big host: below the mask
            pegar(base, si, W // 2 - si.shape[1] // 2, int(ys) - 58)
        # 5. tape header: REC dot + tape counter, top-left, always
        hdr = f"\u25cf REC  {R.get('cinta', 'CULT PIXEL REACTS')}  {int(t // 60):02d}:{int(t % 60):02d}:{n % FPS:02d}"
        pegar(base, np.array(texto_rgba(hdr, fuente(F_MONO, 28), (255, 70, 80, 230) if n % 30 < 18 else HUESO + (200,), 3)), 40, 205)
        textura(base, n, (0, 0, W, 40)); textura(base, n, (0, H - 24, W, 24))
        if cuadro_t is not None:
            Image.fromarray(base).save(sys.argv[sys.argv.index("--cuadro") + 2]); print("frame", t); return
        enc.stdin.write(base.tobytes())
        if n % 150 == 0:
            print(f"{t:.1f}/{hasta:.1f} s", flush=True)
    enc.stdin.close(); enc.wait()
    # audio: voice + footage sound (ducked by default) + music
    ins, fil, k = ["-i", str(tmp), "-i", str(voz)], ["[1:a]aresample=48000,volume=1.0[v0]"], 2
    mezcla = ["[v0]"]
    for p in planos:
        if p.get("audio") is None or Path(p["src"]).suffix.lower() in (".jpg", ".png", ".jpeg", ".webp"):
            continue
        ins += ["-ss", f"{p.get('desde', 0):.3f}", "-t", f"{(p['fin'] - p['ini']) * p.get('vel', 1.0):.3f}", "-i", str(carpeta / p["src"])]
        tempo = f",atempo={max(0.5, p.get('vel', 1.0))}" if p.get("vel", 1.0) != 1 else ""
        fil.append(f"[{k}:a]aresample=48000{tempo},volume={p['audio']}dB,adelay={int(p['ini'] * 1000)}:all=1[a{k}]"); mezcla.append(f"[a{k}]"); k += 1
    if R.get("musica"):
        ins += ["-stream_loop", "-1", "-i", str(carpeta / R["musica"])]
        fil.append(f"[{k}:a]aresample=48000,volume={R.get('musica_db', -6)}dB,atrim=0:{hasta:.2f}[m]"); mezcla.append("[m]")
    fil.append("".join(mezcla) + f"amix=inputs={len(mezcla)}:normalize=0:duration=longest,atrim=0:{hasta:.2f}[aout]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fil), "-map", "0:v", "-map", "[aout]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)], check=True)
    tmp.unlink()
    print("ok", out)


if __name__ == "__main__":
    main()
