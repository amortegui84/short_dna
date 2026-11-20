"""Reaction format (test 2026-11-15): the narrator, cut out with no background, sits in a corner and reacts to a real news
story while the footage plays full screen behind him; he goes big for the hook and the verdict. Built frame by frame in
Python (PIL + numpy) and encoded with ffmpeg, so a 60 s Short renders in a few minutes without After Effects.

Everything comes from <project>/reaccion.json (see docs/REACTION_FORMAT.md):
  voz        the narration (one file, already at its final pace)
  musica     optional bed, with its gain in dB
  host       {"clips": [{"mate": "mates/R01.mov", "ini": s, "fin": s, "desde": s}], "alto": px, "margen": px,
              "grande": [[ini, fin], ...]}   the cut-out clips in order; "grande" = the spans where he fills the frame
  planos     [{"src", "ini", "fin", "desde", "vel", "modo": "full"|"caja", "zoom": [a, b], "foco": [fx, fy], "foco_fin": [fx, fy], "congelar": s,
              "audio": dB or null, "credito": "...", "marcas": [{"tipo": "circulo"|"flecha", "x", "y", "r", "t"}],
              "cabeza": false = the host ducks out for this plan}]
  tarjetas   [{"tipo": "comentario"|"titular"|"cita", "texto", "autor", "fuente", "ini", "fin", "y"}]
  titulo     {"texto": "THE ARK OF THE COVENANT", "y": 1130, "tam": 60} topic label on screen the whole video (hidden under cards)
  cambiar    [[heard, right], ...] fixes a single misheard word in the subtitles; juntar [[a, b, right]] merges two
  y_sub      subtitle line centre (default 1140: above the host head, inside the clean area x 65-888, y 288-1248)
  sub_bloque {"x": left px, "y": centre px, "ancho": px, "palabras": 9} a phrase as a block of lines beside a side host's
             head (CCC, 2026-11-16); while he is big or ducked out the single centred line takes over
Every time is in seconds of the final video. Footage is never filtered: the tape texture goes on the frame and the host only.
Usage: python reaccion.py <project> [--hasta 12] [--cuadro 7.5 out.png]"""
import json, math, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).parent))
from comun import duracion, palabras  # noqa: E402

W, H, FPS = 1080, 1920, 30
FONTS = Path("C:/Windows/Fonts")
F_IMPACT = str(FONTS / "impact.ttf")
F_MONO = str(FONTS / "courbd.ttf")
F_SERIF = str(FONTS / "InstrumentSerif-Italic.ttf")
TINTA, HUESO, AMARILLO, ROJO = (7, 22, 33), (232, 223, 200), (244, 224, 124), (186, 24, 51)
# the look of a brand: reaccion.json "estilo" overrides any of these (Cult Pixel = these defaults: VHS tape, Impact captions;
# Cool Culture Club = clean render, Poppins captions in amber, the head "lands big and settles" on every cut)
ESTILO = {"sub_fuente": "impact.ttf", "sub_tam": 78, "sub_mayus": True, "sub_color": HUESO, "sub_activa": AMARILLO,
          "sub_barra": (5, 5, 8, 215), "sub_borde": 3, "tinta": TINTA, "papel": HUESO, "acento": AMARILLO, "rojo": ROJO,
          "titular_fuente": "impact.ttf", "mono_fuente": "courbd.ttf", "cita_fuente": "InstrumentSerif-Italic.ttf",
          "textura": True, "cabecera": True, "corte": "punch"}


def ruta_fuente(nombre):
    for d in (FONTS, Path.home() / "AppData/Local/Microsoft/Windows/Fonts"):
        if (d / nombre).exists():
            return str(d / nombre)
    return str(FONTS / nombre)


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
        TINTA, HUESO, AMARILLO, ROJO = ESTILO["tinta"], ESTILO["papel"], ESTILO["acento"], ESTILO["rojo"]
        f = fuente(ruta_fuente(ESTILO["titular_fuente"]), 64); lineas = envolver(t["texto"].upper(), f, ancho - 80); lh = 70
        cab = (t.get("fuente") or "").upper(); fc = fuente(ruta_fuente(ESTILO["mono_fuente"]), 30)
        alto = 70 + len(lineas) * lh + 60
        im = Image.new("RGBA", (ancho, alto), HUESO + (255,)); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, ancho, 54], fill=TINTA); d.text((28, 12), cab, font=fc, fill=HUESO)
        for k, ln in enumerate(lineas):
            d.text((40, 76 + k * lh), ln, font=f, fill=TINTA)
    else:
        TINTA, HUESO, AMARILLO, ROJO = ESTILO["tinta"], ESTILO["papel"], ESTILO["acento"], ESTILO["rojo"]
        f = fuente(ruta_fuente(ESTILO["cita_fuente"]), 58) if t["tipo"] == "cita" else fuente(ruta_fuente(ESTILO["mono_fuente"]), 40)
        lh = 64 if t["tipo"] == "cita" else 50
        texto = ("\u201c" + t["texto"] + "\u201d") if t["tipo"] == "cita" else t["texto"]
        lineas = envolver(texto, f, ancho - 90); fa = fuente(ruta_fuente(ESTILO["mono_fuente"]), 30)
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


def titulo_img(tit):
    """The topic label: Impact caps in bone white with a thick black stroke on a red tape strip (stays on screen)."""
    f = fuente(ruta_fuente(ESTILO["titular_fuente"]), tit.get("tam", 60))
    txt = texto_rgba(tit["texto"].upper(), f, tuple(ESTILO["papel"][:3]) + (255,), 5)
    im = Image.new("RGBA", (txt.width + 56, txt.height + 26), tuple(ESTILO["rojo"][:3]) + (235,))
    im.alpha_composite(txt, (28, 13))
    return np.array(im.rotate(tit.get("giro", -1.0), resample=Image.BICUBIC, expand=True))


class Mapa:
    """A continuous zoom into a place from Google Maps screenshots (engine/mapa_capturas.py), all centred on the place:
    {"tipo": "mapa", "ini", "fin", "capturas": [{"img": "mapa/mapa_mapa_z3.png", "z": 3}, ...], "z": [3, 17],
     "etiqueta": "ISLA DE LAS MUNECAS", "sub": "Xochimilco, Mexico City", "credito": "MAP DATA (C) GOOGLE"}
    The zoom level runs from z[0] to z[1] (Settle ease); the frame shown is the nearest screenshot below the current
    zoom, scaled by 2^(z - its zoom), cross-fading into the next one; a red pin lands on the centre, then the label."""
    foto = True; lec = None

    def __init__(self, p, carpeta):
        self.p = p; self.dur = p["fin"] - p["ini"]
        self.caps = []
        for c in sorted(p["capturas"], key=lambda c: c["z"]):
            im = Image.open(carpeta / c["img"]).convert("RGB")
            w, h = im.size; mx, my = int(w * 0.12), int(h * 0.12)   # trim the map UI on the edges, same ratio both axes
            im = im.crop((mx, my, w - mx, h - my)).resize((W, H), Image.LANCZOS)
            self.caps.append((c["z"], np.array(im)))

    def vista(self, z):
        i = max([k for k, (zz, _) in enumerate(self.caps) if zz <= z] or [0])
        zz, img = self.caps[i]; s = 2 ** (z - zz)
        cw, ch = int(W / s), int(H / s)
        crop = img[(H - ch) // 2:(H - ch) // 2 + ch, (W - cw) // 2:(W - cw) // 2 + cw]
        out = np.array(Image.fromarray(crop).resize((W, H), Image.BILINEAR))
        if i + 1 < len(self.caps):   # cross-fade into the next screenshot over its last 0.6 zoom levels
            zn = self.caps[i + 1][0]; a = min(1.0, max(0.0, (z - (zn - 0.6)) / 0.6))
            if a > 0:
                sn = 2 ** (z - zn); cw2, ch2 = int(W / sn), int(H / sn)
                big = Image.fromarray(self.caps[i + 1][1]).resize((int(W * sn), int(H * sn)), Image.BILINEAR) if sn > 1 else None
                if big is None:   # zoomed out from the next image: shrink it into the frame over the current one
                    sm = np.array(Image.fromarray(self.caps[i + 1][1]).resize((max(2, int(W * sn)), max(2, int(H * sn))), Image.BILINEAR))
                    y0, x0 = (H - sm.shape[0]) // 2, (W - sm.shape[1]) // 2
                    nxt = out.copy(); nxt[y0:y0 + sm.shape[0], x0:x0 + sm.shape[1]] = sm
                else:
                    nxt = np.array(big)[(big.height - H) // 2:(big.height - H) // 2 + H, (big.width - W) // 2:(big.width - W) // 2 + W]
                out = (out * (1 - a) + nxt * a).astype(np.uint8)
        return out

    def cuadro(self, t):
        u = min(1.0, max(0.0, (t - self.p["ini"]) / max(self.dur * 0.85, 0.01)))
        z0, z1 = self.p.get("z", [self.caps[0][0], self.caps[-1][0]])
        z = z0 + (z1 - z0) * SETTLE(u)
        base = self.vista(z)
        if u > 0.8:   # the pin drops on the place
            k = LAND(min(1.0, (u - 0.8) / 0.2)); im = Image.fromarray(base); d = ImageDraw.Draw(im)
            cx, cy = W // 2, int(H / 2 - 40 * (1 - k)) ; r = 34
            d.ellipse([cx - r, cy - 2 * r - 30, cx + r, cy - 30], fill=ESTILO["rojo"], outline=(255, 255, 255), width=5)
            d.polygon([(cx - r * 0.7, cy - r - 22), (cx + r * 0.7, cy - r - 22), (cx, cy)], fill=ESTILO["rojo"])
            d.ellipse([cx - 10, cy - r - 40, cx + 10, cy - r - 20], fill=(255, 255, 255))
            if self.p.get("etiqueta"):
                f = fuente(ruta_fuente(ESTILO["titular_fuente"]), 56); f2 = fuente(ruta_fuente(ESTILO["mono_fuente"]), 30)
                tw = max(f.getlength(self.p["etiqueta"]), f2.getlength(self.p.get("sub", ""))) + 60
                y = cy - 2 * r - 210
                d.rectangle([cx - tw / 2, y, cx + tw / 2, y + 130], fill=tuple(ESTILO["tinta"]))
                d.text((cx - tw / 2 + 30, y + 14), self.p["etiqueta"], font=f, fill=tuple(ESTILO["papel"]))
                d.text((cx - tw / 2 + 30, y + 82), self.p.get("sub", ""), font=f2, fill=tuple(ESTILO["acento"]))
            base = np.array(im)
        return base, (0, 0, W, H)


class Plano:
    def __init__(self, p, carpeta):
        self.p = p; src = carpeta / p["src"]; self.src = src
        self.dur = p["fin"] - p["ini"]; self.z = p.get("zoom", [1.0, 1.06]); self.foco = p.get("foco", [0.5, 0.5])
        sw, sh = tam_video(src) if src.suffix.lower() not in (".jpg", ".png", ".jpeg", ".webp") else ImageOps.exif_transpose(Image.open(src)).size   # phone photos carry their rotation in EXIF
        self.foto = src.suffix.lower() in (".jpg", ".png", ".jpeg", ".webp")
        self.modo = p.get("modo") or ("full" if sh / sw > 1.2 else "caja")
        zmax = max(self.z)
        if self.modo == "full":   # cover the frame, room for the zoom
            s = max(W / sw, H / sh) * zmax
        else:                     # fit the width; a blurred copy fills the frame behind
            s = W / sw * zmax
        self.tw, self.th = int(sw * s) // 2 * 2, int(sh * s) // 2 * 2
        if self.foto:
            self.img = np.array(ImageOps.exif_transpose(Image.open(src)).convert("RGB").resize((self.tw, self.th), Image.LANCZOS)); self.lec = None
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
    for par in json.loads((carpeta / "reaccion.json").read_text(encoding="utf-8")).get("cambiar", []):
        # one misheard word: [heard, right] ("Lie." -> "Live."), punctuation kept
        for w in ws:
            if w[0].strip(".,?!").lower() == par[0].lower():
                w[0] = par[1] + w[0][len(w[0].rstrip(".,?!")):]
    for a, b, junto in json.loads((carpeta / "reaccion.json").read_text(encoding="utf-8")).get("juntar", []):
        # names Whisper splits or mishears ("Sochi milko" -> "Xochimilco"): [first, second, replacement]
        for i in range(len(ws) - 1):
            if ws[i] and ws[i + 1] and ws[i][0].strip(".,").lower() == a.strip(".,").lower() and ws[i + 1][0].strip(".,").lower() == b.strip(".,").lower():
                ws[i] = [junto + ws[i + 1][0][len(ws[i + 1][0].rstrip(".,")):], ws[i][1], ws[i + 1][2]]; ws[i + 1] = None
        ws = [w for w in ws if w]
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


def bloques(ws_grupos, n_max=9):
    """Phrases for the block layout: the 3-word chunks re-joined into phrases of up to n_max words, broken at sentence
    ends (or a comma once the phrase has 5 words), never ending on a small word."""
    ws = [w for g in ws_grupos for w in g]
    pequenas = {"a", "an", "the", "at", "of", "to", "in", "on", "is", "was", "and", "but", "or", "with", "into", "her", "it", "be"}
    out, cur = [], []
    for w in ws:
        cur.append(w); fin = w[0][-1:]
        corta = fin in ".?!" or len(cur) >= n_max or (fin in ",;:" and len(cur) >= 5)
        if corta and (w[0].lower().strip(".,?!:;") not in pequenas or fin in ".,?!:;"):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def bloque_img(grupo, t, ancho):
    """A phrase as a left-aligned block of lines (review 2026-11-16: "un bloque de líneas al lado derecho de la cabeza"):
    words already said in the subtitle colour, the one being said in the accent, the ones still to come dimmed."""
    E = ESTILO; tam = E.get("bloque_tam", E["sub_tam"]); f = fuente(ruta_fuente(E["sub_fuente"]), tam)
    piezas = [((w[0].upper() if E["sub_mayus"] else w[0]).strip(";:"), w[1] <= t + 0.02) for w in grupo]
    actual = max([i for i, (_, on) in enumerate(piezas) if on] or [-1])
    lineas, cur = [], []
    for i, (p, _) in enumerate(piezas):
        if cur and f.getlength(" ".join(piezas[j][0] for j in cur + [i])) > ancho:
            lineas.append(cur); cur = []
        cur.append(i)
    if cur:
        lineas.append(cur)
    alto_l = int(tam * 1.18)
    im = Image.new("RGBA", (ancho + 40, alto_l * len(lineas) + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k, ln in enumerate(lineas):
        x = 10
        for i in ln:
            p, on = piezas[i]
            col = tuple(E["sub_activa"]) if i == actual else tuple(E["sub_color"]) if on else tuple(E["sub_color"])[:3] + (95,)
            capa = Image.new("RGBA", im.size, (0, 0, 0, 0)); dc = ImageDraw.Draw(capa)
            dc.text((x, 10 + k * alto_l), p, font=f, fill=col[:3] + (255,), stroke_width=E["sub_borde"], stroke_fill=(0, 0, 0))
            if len(col) == 4:
                capa.putalpha(capa.getchannel("A").point(lambda a: a * col[3] // 255))
            im.alpha_composite(capa)
            x += f.getlength(p + " ")
    return np.array(im)


def sub_img(grupo, t):
    E = ESTILO; f = fuente(ruta_fuente(E["sub_fuente"]), E["sub_tam"])
    piezas = [((w[0].upper() if E["sub_mayus"] else w[0]).strip(".,;:"), w[1] <= t + 0.02) for w in grupo]
    ancho = sum(f.getlength(p + " ") for p, _ in piezas) + 40
    im = Image.new("RGBA", (int(ancho) + 20, 116), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if E["sub_barra"]:
        d.rectangle([0, 10, im.width, 106], fill=tuple(E["sub_barra"]))
    x = 30; actual = max([i for i, (_, on) in enumerate(piezas) if on] or [0])
    for i, (p, on) in enumerate(piezas):
        d.text((x, 14), p, font=f, fill=tuple(E["sub_activa"]) if i == actual else tuple(E["sub_color"]), stroke_width=E["sub_borde"], stroke_fill=(0, 0, 0))
        x += f.getlength(p + " ")
    return np.array(im)


def textura(base, n, zona, mascara=None):
    """Tape texture on the host (only inside his silhouette when a mask is given: on the whole box it drew a dark
    rectangle around him, review 2026-11-15) and the frame edges: scanlines, a little noise, a rolling tracking line."""
    if not ESTILO["textura"]:
        return
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
    ESTILO.update({k: (tuple(v) if isinstance(v, list) else v) for k, v in R.get("estilo", {}).items()})
    voz = carpeta / R["voz"]; total = R.get("duracion") or duracion(voz) + R.get("cola", 1.2)
    hasta = float(sys.argv[sys.argv.index("--hasta") + 1]) if "--hasta" in sys.argv else total
    cuadro_t = float(sys.argv[sys.argv.index("--cuadro") + 1]) if "--cuadro" in sys.argv else None
    grupos = subtitulos(voz, carpeta)
    frases = bloques(grupos, R.get("sub_bloque", {}).get("palabras", 9))
    host = R["host"]; alto_p, margen = host.get("alto", 1000), host.get("margen", 24); alto_g = host.get("alto_grande", 1500)
    planos = sorted(R["planos"], key=lambda p: p["ini"]); abiertos = {}
    tarjetas = [dict(t, img=tarjeta_img(t)) for t in R.get("tarjetas", [])]
    clips = []
    for c in host.get("clips", []):
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

    # hidden head: "fuera" spans plus every plan marked "cabeza": false (review 2026-11-16: "la cabeza no todo el tiempo,
    # en algunos casos esconderla y en otros sacarla"); touching spans are merged so the head does not pop up between them
    spans = sorted([list(s) for s in host.get("fuera", [])] + [[p["ini"], p["fin"]] for p in R["planos"] if p.get("cabeza") is False])
    fuera = []
    for a, b in spans:
        if fuera and a <= fuera[-1][1] + 0.05:
            fuera[-1][1] = max(fuera[-1][1], b)
        else:
            fuera.append([a, b])

    def nivel_fuera(t):   # 0 = on screen, 1 = gone. Default a hard cut (review 2026-11-16: "se va de una forma rara, debería
        # ser un corte seco"); estilo "salida": "deslizar" keeps the old duck out (0.3 s) and back up (0.4 s)
        v = 0.0
        for a, b in fuera:
            if a <= t < b:
                v = 1.0 if ESTILO.get("salida", "corte") == "corte" else max(v, min(SETTLE((t - a) / 0.3), SETTLE((b - t) / 0.4)))
        return v

    # PREVIEW ONLY: CCC rule, every delivered video is assembled in After Effects with Motion DNA
    out = carpeta / f"{R['slug']}_PREVIEW_python.mp4" if cuadro_t is None else None
    if cuadro_t is None:
        print("WARNING: Python preview only. The delivered edit must be built in After Effects with Motion DNA.")
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
                abiertos[key] = Mapa(p, carpeta) if p.get("tipo") == "mapa" else Plano(p, carpeta)
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
            pegar(base, np.array(texto_rgba(cred.upper(), fuente(ruta_fuente(ESTILO['mono_fuente']), 26), tuple(ESTILO['papel'][:3]) + (235,), 3)), 40, 250)
        # 2. cards
        for c in tarjetas:
            if c["ini"] <= t < c["fin"]:
                k = POP((t - c["ini"]) / (8 / 30)); salida = min(1.0, (c["fin"] - t) / 0.2)
                img = c["img"]; sc = 0.86 + 0.14 * k
                im = Image.fromarray(img).resize((int(img.shape[1] * sc), int(img.shape[0] * sc)), Image.BILINEAR)
                pegar(base, np.array(im), W // 2 - im.width // 2, int(c.get("y", 560) + (1 - min(k, 1)) * 60), min(max(k, 0) * 1.4, 1.0) * salida)
        # 2b. topic label that stays on screen the whole video (the talking-head news genre: "EL ARCA DE LA ALIANZA" under
        # the picture; review 2026-11-16). {"texto", "y", "tam", "desde", "hasta"}; it hides while a card is up
        tit = R.get("titulo")
        if tit and tit.get("desde", 0) <= t < tit.get("hasta", 1e9) and not any(c["ini"] <= t < c["fin"] for c in tarjetas):
            if "_img" not in tit:
                tit["_img"] = titulo_img(tit)
            ti = tit["_img"]; pegar(base, ti, W // 2 - ti.shape[1] // 2, int(tit.get("y", 1130) - ti.shape[0] / 2))
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
            if ESTILO["corte"] == "salto":   # lands 9 % big and settles to 2 % in 4 frames, then holds (CCC "salto_avatar")
                esc = 1.02 + 0.07 * (1 - SETTLE(min((n - c["n0"]) / 4, 1.0)))
            else:                            # every other clip punched in 7 %
                esc = 1.07 if c["k"] % 2 else 1.0
            alto = int((alto_p + (alto_g - alto_p) * g) * esc)
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
        bq = R.get("sub_bloque"); gb = nivel_grande(t)
        if bq and gb < 0.5 and nivel_fuera(t) < 0.5:   # block of lines beside the head ({"x", "y", "ancho", "palabras"})
            fr = next((b for b in frases if b[0][1] - 0.05 <= t < b[-1][2] + 0.25), None)
            if fr:
                bi = bloque_img(fr, t, bq.get("ancho", 480))
                pegar(base, bi, bq.get("x", 540), int(bq.get("y", 1450) - bi.shape[0] / 2))
        elif gr:
            si = sub_img(gr, t); ys = R.get("y_sub", 860) + (R.get("y_sub_grande", 1560) - R.get("y_sub", 860)) * nivel_grande(t) * (1 - nivel_fuera(t))   # big host: below the mask
            xs = R.get("x_sub", 0.5) + (0.5 - R.get("x_sub", 0.5)) * nivel_grande(t)   # side host: subtitles beside him
            xi = min(max(int(W * xs) - si.shape[1] // 2, 40), W - 40 - si.shape[1])   # a long chunk never runs off the edge
            pegar(base, si, xi, int(ys) - 58)
        # 5. tape header: REC dot + tape counter, top-left, always
        hdr = f"\u25cf REC  {R.get('cinta', 'CULT PIXEL REACTS')}  {int(t // 60):02d}:{int(t % 60):02d}:{n % FPS:02d}"
        if ESTILO["cabecera"]:
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
        if p.get("audio") is None or p.get("tipo") == "mapa" or Path(p["src"]).suffix.lower() in (".jpg", ".png", ".jpeg", ".webp"):
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
