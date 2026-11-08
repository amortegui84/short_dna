"""Builds the art-collage Short in After Effects (style "collage_v10c") from a project folder: sections, subtitles, labels, sound
cues and render. Everything specific to a video comes from proyecto.json (see docs/PROJECT_SCHEMA.md):
  momentos_a {line: [[kind, value, word], ...]}  kind = obra | etq | cta | lapiz | flecha  (what enters on which spoken word)
  obras_b    {line: [[obra, word], ...]}         artworks of the voice-over lines, on the word that names them
  titulos    {obra: [title, date]}               cards of the artworks
  juntas     [[w1, w2], ...]                     word pairs a subtitle line never splits (names)
Usage: python build_collage.py <project> [--solo-datos] [--render]
History of the format (v4 -> v10c) and every rule behind it: docs/STYLE_COLLAGE.md and docs/LEARNINGS.md."""
import json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from comun import CFG, KIT, MOTION_DNA, buscar, marca_dir  # noqa: E402

carpeta = Path(sys.argv[1]).resolve()
HERE = Path(__file__).parent
pj = json.loads((carpeta / "proyecto.json").read_text(encoding="utf-8"))
tl = json.loads((carpeta / "timeline.json").read_text(encoding="utf-8"))
CAJAS = json.loads((carpeta / "cajas_cabeza.json").read_text(encoding="utf-8"))
from comun import personaje as _pers  # noqa: E402
SIN_BOCA = bool(pj.get("personaje") and _pers(pj).get("sin_boca"))   # narrador sin boca: el clip va y vuelve en vez de congelarse
(carpeta / "ae").mkdir(exist_ok=True)
AEP = (carpeta / "ae" / f"{pj['slug']}.aep").as_posix()   # un proyecto de After por video
G = KIT
COMP = pj.get("comp") or f"{pj['numero']:02d} {pj['artista']} {pj['slug']}"
MUSICA = (carpeta / "musica" / "elegida.wav").as_posix() if (carpeta / "musica" / "elegida.wav").exists() else ""   # musica.py la deja ahi (-27 LUFS)
FZ = 1.8
W, H = 1080, 1920
SEGURA = (40, 150, 950, 1330)
Y_BARRA = 1400

# ---------- datos del video (proyecto.json); los recortes y loops son del kit (decoracion opcional)
RECORTES = pj.get("recortes", ["alfa3/" + n for n in ("tubo_1", "pincel_1", "paleta", "carboncillos", "frasco", "compas")])
LOOPS = [("libro", "paleta")]
TITULOS = {k: tuple(v) for k, v in pj.get("titulos", {}).items()}
INTER = {k: [tuple(x) for x in v] for k, v in pj.get("momentos_a", {}).items()}
MARCOS = ["marco_barroco", "marco_oval", "marco_simple"]
OBRAS_B = {k: [tuple(x) for x in v] for k, v in pj.get("obras_b", {}).items()}
MIN_OBRA = 1.8

# ---------- linea de tiempo (igual que build_collage.py: la ficha entra antes de la primera B)
segs, off, fz0 = [], 0.0, None
primera_b = next(s["id"] for s in tl["segmentos"] if s["tipo"] == "B")
for s in tl["segmentos"]:
    d = dict(s)
    if s["id"] == primera_b:
        fz0, off = s["start"], FZ
    d["start"] = round(d["start"] + off, 3)
    d["words"] = [dict(w, s=round(w["s"] + off, 3), e=round(w["e"] + off, 3)) for w in d["words"]]
    segs.append(d)
total = round(tl["total"] + FZ, 3)
# the ending breathes: the reference holds ~1.5-2 s after the last word (button, host still alive); the style asks for it
_est = Path(__file__).parent.parent / "brands" / str(pj.get("marca", "")) / "styles" / f"{pj.get('estilo', '')}.json"
if pj.get("marca") and _est.exists():
    total = round(total + float(json.loads(_est.read_text(encoding="utf-8")).get("cola_final_s", 0)), 3)


def tiempo(seg, palabra):
    for w in seg["words"]:
        if w["w"].lower().strip(".,?!:;\"'\u201c\u201d").startswith(palabra.lower()):
            return max(seg["start"], round(w["s"] - 0.08, 3))
    return seg["start"] + 0.4


def aspecto(img):
    w, h = Image.open(img).size
    return w / h


def muestras(img, n=4):
    im = Image.open(img).convert("RGB"); im.thumbnail((200, 200))
    cnt = sorted(im.quantize(colors=10, method=Image.Quantize.MEDIANCUT).convert("RGB").getcolors(40000), reverse=True)
    sel = []
    for _, c in cnt:
        if sum(c) < 90 or any(sum(abs(a - b) for a, b in zip(c, s)) < 110 for s in sel):
            continue
        sel.append(c)
        if len(sel) == n:
            break
    return ["#%02X%02X%02X" % c for c in sel]


def abertura(png):
    from scipy.ndimage import label
    a = np.asarray(Image.open(png).convert("RGBA"))[..., 3] < 40
    h, w = a.shape
    lab, _ = label(a); k = lab[h // 2, w // 2]
    ys, xs = np.nonzero(lab == k)
    return [round(xs.min() / w, 3), round(ys.min() / h, 3), round((xs.max() + 1) / w, 3), round((ys.max() + 1) / h, 3)]


def ancho_etq(txt, size):
    return len(txt) * size * 0.5 + 104, size * 1.2 + 70


# ---------- secciones con su maquetacion en coordenadas de pantalla
HEAD_A = {"x": 540, "y": 1100, "s": 100}   # v10: busto de la presentadora; baja un poco para que el pelo no toque el gancho   # v7: enorme, la cara ~60 % del ancho, como el ejemplo del usuario
HEAD_B = {"x": 860, "y": 1110, "s": 30}
SLOTS_OBRA = [(255, 500), (255, 1000)]
CAND_ETQ = [(300, 250), (720, 250), (300, 420), (720, 420), (540, 330), (540, 500), (300, 580), (720, 580)]   # sobre la obra de arriba, lejos de la cara
secciones, ult_mate, n_rec, n_loop = [], None, 0, 0
# the matte of the clip + its new footage (engine/continuar.py) wins when it exists
mate_de = {s["id"]: next(m for m in (carpeta / "mates" / f"{s['id']}_full.mov", carpeta / "mates" / f"{s['id']}.mov") if m.exists() or m.name.endswith(f"{s['id']}.mov")).as_posix()
           for s in segs if s["tipo"] == "A"}


def rec(k=0):
    global n_rec
    n_rec += 1
    return G + RECORTES[(n_rec + k) % len(RECORTES)] + ".png"


def loop():
    global n_loop
    n_loop += 1
    return LOOPS[n_loop % len(LOOPS)]


for s in segs:
    fin = s["start"] + s["dur"] + tl["gap"]
    if s["tipo"] == "A":
        n = len(secciones)
        sec = {"tipo": "cabeza", "id": s["id"], "ini": s["start"], "fin": fin, "mate": mate_de[s["id"]], "t0base": round(s["start"] - s["t0"], 3), "sin_boca": SIN_BOCA,
               "head": dict(HEAD_A), "obras": [], "etqs": [], "lapiz": [], "flechas": [], "cta": None}
        libres = list(CAND_ETQ)
        if s is segs[0]:   # apertura: la cabeza grande y centrada es el eje; gancho arriba; una sola obra de avance
            sec["tipo"] = "gancho"; sec["head"] = dict(HEAD_A)
            sec["etqs"].append({"txt": pj["gancho"], "x": 540, "y": 250, "t": 0.35, "rot": -3, "size": 64})
            libres = [c for c in libres if c[1] > 400]
        for it in INTER.get(s["id"], []):
            t = tiempo(s, it[-1])
            if it[0] == "obra" and len(sec["obras"]) < 2:
                img = (carpeta / "obras" / f"{it[1]}.jpg").as_posix(); x, y = SLOTS_OBRA[len(sec["obras"])] if sec["tipo"] != "gancho" else (205, 1160)
                sec["obras"].append({"img": img, "stem": it[1], "marco": MARCOS[(n + len(sec["obras"])) % 3], "x": x, "y": y, "w": 300 if sec["tipo"] == "gancho" else 380, "t": t,
                                     "rot": -2 if len(sec["obras"]) else 2})
            elif it[0] == "cta":
                sec["etqs"].append({"txt": it[1], "t": t, "rot": -2, "size": 62, "x": 540, "y": 250, "cta": True})
                libres = [c for c in libres if c[1] > 400]
            elif it[0] == "etq" and sec["tipo"] == "gancho":
                continue   # apertura con orden claro: solo el gancho; la cabeza centrada no deja sitio a mas etiquetas
            elif it[0] == "etq":
                sec["etqs"].append({"txt": it[1], "t": t, "rot": [-4, 3, -3, 4][len(sec["etqs"]) % 4], "size": 58, "cand": True})
            elif it[0] == "lapiz":
                o = sec["obras"][-1] if sec["obras"] else {"x": SLOTS_OBRA[0][0], "y": SLOTS_OBRA[0][1]}
                sec["lapiz"].append({"x": o["x"], "y": o["y"], "a": 470, "b": 470, "t": t})
            elif it[0] == "flecha":
                sec["flechas"].append({"x": 520, "y": 1180, "rot": -40, "t": t})
        sec["libres"] = libres
        sec["deco"] = [{"p": rec(), "x": 930, "y": 400, "w": 250, "rot": 8, "t": s["start"] + 0.2, "k": 0.94},
                       {"p": rec(3), "x": 320, "y": 1660, "w": 300, "rot": -6, "t": s["start"], "k": 1.04}]
        sec["loop"] = dict(zip(("n", "quieto"), loop()), x=780, y=1640, w=260, k=1.06)
        sec["muestras"] = muestras(sec["obras"][0]["img"]) if sec["obras"] else []
        secciones.append(sec)
        ult_mate = sec["mate"]
        continue
    fin_b = s["start"] + s["dur"] + tl["gap"]
    if s["obras"] == ["__cita__"]:
        secciones.append({"tipo": "cita", "ini": s["start"], "fin": fin_b, "cita": pj["cita"]["lineas"], "autor": pj["cita"]["autor"],
                          "palabras": [[w["w"], w["s"]] for w in s["words"]], "clave": pj["cita"].get("clave", "")})   # v10c: la cita aparece palabra a palabra con la voz
        continue
    lista = OBRAS_B.get(s["id"]) or [(o, None) for o in s["obras"][:1]]
    tiempos = [s["start"] if (i == 0 and s["id"] != primera_b) or not pal else tiempo(s, pal) for i, (o, pal) in enumerate(lista)]
    if s["id"] == primera_b:   # la ficha cubre el silencio y el principio de la linea, hasta que se nombra la obra
        # without works on the first B line (CCC: the portrait card is the whole line) the card covers the line to its end
        secciones.append({"tipo": "ficha", "ini": s["start"] - FZ, "fin": tiempos[0] if tiempos else fin_b, "img": (carpeta / "obras" / f"{pj['retrato']}.jpg").as_posix(),
                          "deco": [{"p": rec(), "x": 920, "y": 1660, "w": 260, "rot": 10, "t": s["start"] - FZ, "k": 1.04}]})
    # cada obra al menos MIN_OBRA s: si no cabe, la siguiente se quita
    pares = []
    for i, (o, pal) in enumerate(lista):
        ini = tiempos[i]; fin = tiempos[i + 1] if i + 1 < len(lista) else fin_b
        if pares and ini - pares[-1][1] < MIN_OBRA:
            continue
        pares.append((o, ini))
    for i, (o, ini) in enumerate(pares):
        fin = pares[i + 1][1] if i + 1 < len(pares) else fin_b
        n = len(secciones)
        img = (carpeta / "obras" / f"{o}.jpg").as_posix(); ti, fe = TITULOS.get(o, (o, ""))
        sec = {"tipo": "obra", "ini": ini, "fin": fin, "img": img, "stem": o, "aspecto": round(aspecto(img), 3), "titulo": ti, "fecha": fe,
               "trat": ["lupa", "reflecto", "craquelado"][n % 3], "vista": ["marco", "circulo", "pincelada"][n % 3], "muestras": muestras(img), "etqs": [],
               "deco": [{"p": rec(), "x": 920, "y": 215, "w": 210, "rot": -10, "t": ini + 0.25, "k": 0.95},
                        {"p": rec(5), "x": 330, "y": 1660, "w": 300, "rot": 8, "t": ini, "k": 1.04}]}
        sec["loop"] = dict(zip(("n", "quieto"), loop()), x=800, y=1650, w=260, k=1.06)
        for lid, palabra, txt in pj["palabras_clave"]:
            if lid == s["id"] and ini <= tiempo(s, palabra) < fin:
                sec["etqs"].append({"txt": txt, "t": tiempo(s, palabra), "x": 280, "y": 228, "rot": 4 if n % 2 else -4, "size": 56})
        secciones.append(sec)

# v10c: con "pausa_b" la voz termina antes de que empiece la siguiente seccion: la seccion dura hasta la siguiente (si no, quedaba papel vacio ~1 s)
for _a, _b in zip(secciones, secciones[1:]):
    _a["fin"] = max(_a["fin"], _b["ini"])

# ---------- v8: cuando ella nombra la obra, la obra entra a sangre y la cabeza se va (como en el ejemplo del usuario)
for sec in secciones:   # v9: en el gancho, la obra que nombra entra a sangre como inserto y la cabeza vuelve para cerrar la frase
    sec["inserto"] = None
    if sec["tipo"] == "gancho" and sec.get("obras"):
        o = sec["obras"][0]; t0 = max(o["t"], sec["ini"] + 0.7); t1 = min(t0 + 2.4, sec["fin"] - 1.0)
        if t1 - t0 >= 1.6:
            sec["inserto"] = {"img": o["img"], "t0": round(t0, 3), "t1": round(t1, 3)}
            sec["obras"] = []
for sec in secciones:
    if sec is secciones[-1]:
        sec["corte"] = None   # la ultima linea la cierra ella (llamada a comentar): sin corte, las obras como tarjetas
        continue
    if sec["tipo"] == "cabeza" and sec.get("obras"):
        c0 = max(sec["obras"][0]["t"], sec["ini"] + 1.2)
        sec["corte"] = round(c0, 3) if c0 < sec["fin"] - 0.8 else None
    else:
        sec["corte"] = None

# ---------- v10b (revision 2026-11-05: "la misma pintura partida por una transicion"): una seccion de obra que sigue a una linea suya
# con corte ya no es una seccion aparte (sin camara ni franjas): la obra que estaba a sangre sigue, o la nueva entra con un fundido.
# Si la ultima obra de la linea se veria menos de MIN_VISTA s, sigue esa obra en vez de cambiar.
MIN_VISTA = 1.8
i = 0
while i < len(secciones) - 1:
    sec, nx = secciones[i], secciones[i + 1]
    if sec["tipo"] == "cabeza" and sec.get("corte") and sec.get("obras") and nx["tipo"] == "obra":
        ult = sec["obras"][-1]; vista = nx["ini"] - max(ult["t"], sec["corte"] + 0.8)
        for e in sec.get("etqs", []):
            e.setdefault("fin", round(nx["ini"], 3))   # las etiquetas de la linea se van cuando empieza la voz en off
        if ult["img"] == nx["img"] or vista < MIN_VISTA:
            ti, fe = TITULOS.get(ult["stem"], (ult["stem"], ""))   # sigue la misma obra
        else:
            sec["obras"].append({"img": nx["img"], "stem": nx["stem"], "t": nx["ini"], "marco": ult.get("marco"), "x": ult.get("x"), "y": ult.get("y"), "w": ult.get("w")})
            ti, fe = nx["titulo"], nx["fecha"]
        sec.setdefault("cartelas", []).append({"titulo": ti, "fecha": fe, "t": round(nx["ini"] + 0.95, 3)})   # despues del fundido de 0.9 s
        for e in nx.get("etqs", []):
            sec["etqs"].append(dict(e, cand=True))
        print("v10b: seccion de obra", nx["stem"], "unida a", sec["id"], "->", ti)
        sec["fin"] = nx["fin"]; del secciones[i + 1]
        continue
    i += 1

# the ending tail (style "cola_final_s"): the last host section runs to the end, so engine/continuar.py generates new footage
# for it instead of the edit looping the clip
if secciones and secciones[-1].get("tipo") in ("gancho", "cabeza"):
    secciones[-1]["fin"] = total

# ---------- movimiento ambiente (v5): piezas de la obra para corrientes, profundidad y contornos por obra, tubos para reordenar
CORRIENTE, ENJAMBRE = [], []   # piezas recortadas de las obras (formato v5-v7; el estilo v10c no interviene las obras)
TUBOS = [G + f"alfa3/{n}.png" for n in ("tubo_1", "pincel_1", "tubo_2", "frasco", "tubo_3", "pincel_2")]
nP = 0


def piezas(lista, k):
    global nP
    nP += 1
    return [lista[(nP * 5 + i * 3) % len(lista)] for i in range(k)] if lista else []


def recursos(stem):
    pr, co = Path(G, "profundidad3", f"{stem}.png"), Path(G, "contornos4", f"{stem}.json")
    lineas = json.loads(co.read_text())["lineas"] if co.exists() else []
    return (pr.as_posix() if pr.exists() else None), lineas[:4]


def vivas(stem, n=8):   # figuras de la obra recortadas con SAM3 y su sitio (piezas_pos/<obra>/posiciones.json), las mas grandes primero
    f = Path(G, "piezas_pos", stem, "posiciones.json")
    if not f.exists():
        return []
    lst = [q for q in json.loads(f.read_text()) if Path(q["png"]).exists()]
    lst.sort(key=lambda q: (q["caja"][2] - q["caja"][0]) * (q["caja"][3] - q["caja"][1]), reverse=True)
    return lst[:n]


def clara(img):   # obra clara: lapiz oscuro; obra oscura (el infierno): lapiz claro
    im = Image.open(img).convert("L"); im.thumbnail((200, 200))
    return float(np.asarray(im).mean()) / 255 > 0.42


for sec in secciones:
    sec["corriente"] = piezas(CORRIENTE, 7)
    if sec["tipo"] == "obra":
        sec["prof"], sec["contornos"] = recursos(sec["stem"]); sec["clara"] = clara(sec["img"]); sec["vivas"] = vivas(sec["stem"])
        sec["enjambre"] = piezas(ENJAMBRE, 5)
        sec["tubos"] = TUBOS
    for o in sec.get("obras", []):
        o["prof"], o["contornos"] = recursos(o["stem"]); o["clara"] = clara(o["img"]); o["vivas"] = vivas(o["stem"])

# puntos del tablero: zigzag de 3 columnas, separados lo bastante para que un punto no se vea desde otro
COLS, DX, DY = 3, 1400, 2200
for n, sec in enumerate(secciones):
    fila, col = n // COLS, n % COLS
    if fila % 2:
        col = COLS - 1 - col
    sec["spot"] = [col * DX, fila * DY]


# ---------- etiquetas: posicion libre lejos de la cabeza y de otros textos
def caja_cabeza(sec, t):
    """Caja de la cabeza de una seccion en pantalla en el tiempo t (None si no hay)."""
    if sec["tipo"] in ("cabeza", "gancho"):
        lst = CAJAS[sec["id"]]; tc = t - sec["t0base"]
    else:
        return None
    if tc is None:   # cabeza pequena en bucle: la caja mas grande de su clip
        cs = [q["caja"] for q in lst if q["caja"]]; b = [min(c[0] for c in cs), min(c[1] for c in cs), max(c[2] for c in cs), max(c[3] for c in cs)]
    else:
        q = min(lst, key=lambda q: abs(q["t"] - tc)); b = q["caja"] or [540, 960, 540, 960]
    hd = sec["head"]; e = hd["s"] / 100
    return [(b[0] - 540) * e + hd["x"], (b[1] - 960) * e + hd["y"], (b[2] - 540) * e + hd["x"], (b[3] - 960) * e + hd["y"]]


def choca(r, sec, t0, t1, otros):
    x0, y0, x1, y1 = r
    if x0 < SEGURA[0] or y0 < SEGURA[1] or x1 > SEGURA[2] or y1 > SEGURA[3]:
        return "fuera de la zona segura"
    for t in np.arange(t0, t1, 0.2):
        if sec.get("corte") and t >= sec["corte"]:
            break   # despues del corte ya no hay cabeza
        c = caja_cabeza(sec, t)
        if c and x0 < c[2] + 40 and x1 > c[0] - 40 and y0 < c[3] + 40 and y1 > c[1] - 40:
            return f"toca la cabeza en t={t:.1f}"
    for o in otros:
        if x0 < o[2] + 20 and x1 > o[0] - 20 and y0 < o[3] + 20 and y1 > o[1] - 20:
            return "toca otro texto"
    return None


avisos = []
for sec in secciones:
    puestos = []
    sec["etqs"] = sorted(sec.get("etqs", []), key=lambda e: 0 if e.get("cta") or not e.get("cand") else 1)
    if sec["tipo"] in ("cabeza", "gancho"):
        continue   # v7: en las lineas de la cabeza las palabras van gigantes detras de ella (fondo), no como etiquetas
    for e in sec["etqs"]:
        w, h = ancho_etq(e["txt"], e["size"])
        cands = [(e["x"], e["y"])] if not e.get("cand") else sec["libres"]
        cands = [(max(x, SEGURA[0] + 12 + w / 2), y) for x, y in cands]   # que no se salga por la izquierda
        ok = None
        for (x, y) in cands:
            r = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
            if not choca(r, sec, e["t"], sec["fin"] + 0.3, puestos):
                ok = (x, y, r); break
        if ok is None:   # ultimo recurso: mas pequena en el primer hueco
            e["size"] = 46; w, h = ancho_etq(e["txt"], 46)
            for (x, y) in [(max(x, SEGURA[0] + 12 + w / 2), y) for x, y in cands]:
                r = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
                if not choca(r, sec, e["t"], sec["fin"] + 0.3, puestos):
                    ok = (x, y, r); break
        if ok is None:
            r0 = [cands[0][0] - w / 2, cands[0][1] - h / 2, cands[0][0] + w / 2, cands[0][1] + h / 2]
            avisos.append(f"{sec.get('id', sec['tipo'])} '{e['txt']}': sin hueco libre ({choca(r0, sec, e['t'], sec['fin'] + 0.3, puestos)})"); e["x"], e["y"] = cands[0]; continue
        e["x"], e["y"] = ok[0], ok[1]; puestos.append(ok[2])
    sec.pop("libres", None)


# ---------- subtitulos por frase (la regla de armar2.py), sin la cita
DEBIL = set("a an the to of in on at for and or but with by is my your our his her its their he she it they we i you".split())


JUNTAS = {tuple(j) for j in pj.get("juntas", [])} | {("do", "you"), ("five", "hundred"), ("hundred", "years")}   # pares que una linea de subtitulo no parte


def limpio(w):
    return re.sub(r"[^\w']", "", w["w"]).lower()


def trozos(words):
    """Por clausula (corte tras . ? ! , ; :); una clausula larga se reparte en lineas parejas de hasta 4 palabras o 24 letras;
    ninguna linea termina en palabra debil; una clausula de una palabra se une a la siguiente si cabe."""
    clas, cur = [], []
    for w in words:
        cur.append(w)
        if w["w"][-1] in ".?!,;:":
            clas.append(cur); cur = []
    if cur:
        clas.append(cur)
    unidas = []
    for c in clas:
        if unidas and len(unidas[-1]) == 1 and unidas[-1][-1]["w"][-1] not in ".?!" and len(c) <= 5:
            unidas[-1] = unidas[-1] + c
        else:
            unidas.append(c)
    out = []
    for c in unidas:
        letras = sum(len(w["w"]) + 1 for w in c)
        n = max(1, -(-len(c) // 4), -(-letras // 24))
        L = min(23, max(letras / n * 1.25, 10))   # 22-23 letras de Impact 74 ~ 800 px: no entra en la columna de botones
        lineas, cur = [], []
        for w in c:
            if cur and (sum(len(q["w"]) + 1 for q in cur) + len(w["w"]) > L or len(cur) >= 4):
                corte = len(cur)   # el ultimo punto de corte permitido: no tras palabra debil ni dentro de un nombre
                while corte > 0 and (limpio(cur[corte - 1]) in DEBIL or (limpio(cur[corte - 1]), limpio(cur[corte] if corte < len(cur) else w)) in JUNTAS):
                    corte -= 1
                if corte > 0:   # sin un corte permitido, la linea sigue (mejor algo larga que partida)
                    lineas.append(cur[:corte]); cur = cur[corte:]
            cur.append(w)
        if cur:
            lineas.append(cur)
        if len(lineas) > 1 and len(lineas[-1]) == 1:   # una palabra sola al final: se une, o se le pasa una palabra de la linea anterior
            if len(lineas[-2]) <= 2:
                ultima = lineas.pop(); lineas[-1] = lineas[-1] + ultima
            else:
                lineas[-1].insert(0, lineas[-2].pop())
        out += lineas
    return out


citas = [(c["ini"], c["fin"]) for c in secciones if c["tipo"] == "cita"]
subs = []
for s in segs:
    ws = [w for w in s["words"] if not any(a <= (w["s"] + w["e"]) / 2 < b for a, b in citas)]
    for t in trozos(ws):
        subs.append({"words": t, "ini": round(max(0, t[0]["s"] - 0.04), 3)})
for i, s in enumerate(subs):
    nxt = subs[i + 1]["ini"] if i + 1 < len(subs) else total
    s["fin"] = round(min(nxt, s["words"][-1]["e"] + 0.5, total), 3)

marcos = {m: abertura(Path(G) / "alfa3" / f"{m}.png") for m in MARCOS}
RETRATO = (carpeta / "retrato_recorte.png").as_posix()
ESTILO = json.loads(buscar("styles", pj.get("estilo", "collage_v10c"), pj.get("marca")).read_text(encoding="utf-8"))   # colores, glitch, sonidos
_est = marca_dir(pj.get("marca")) / "kit" / "fondo_estatica.png"
ESTATICA = _est.as_posix() if _est.exists() else ""
# relleno de la ficha: piezas con alfa del kit de la marca (si el estilo lo pide); si no, las herramientas de pintor del kit del repo
_kit = marca_dir(pj.get("marca")) / "kit"
RELLENO = [(_kit / f"{n}.png").as_posix() for n in ESTILO.get("relleno_ficha", []) if (_kit / f"{n}.png").exists()]   # el retrato del artista recortado (etapa "retrato")
OBRAS_ARTISTA = [(carpeta / "obras" / f).as_posix() for f in sorted(os.listdir(carpeta / "obras")) if f.endswith(".jpg") and not f.startswith("00_")
                 and aspecto(carpeta / "obras" / f) >= 0.8]   # sin obras muy altas: dentro de la silueta suben hasta la cara
DATA = {"retrato": RETRATO, "obrasArtista": OBRAS_ARTISTA, "piezasRelleno": piezas(ENJAMBRE, 18) + piezas(CORRIENTE, 8), "comp": COMP, "total": total, "secciones": secciones, "subs": subs, "yBarra": Y_BARRA, "marcos": marcos, "numero": f"{pj['numero']:02d}",
        "artista": pj["artista"], "fechas": pj["fechas"], "lema": pj["lema"], "barrido": fz0, "musica": MUSICA,
        "voces": [{"id": s["id"], "wav": (Path(s["wav"]) if Path(s["wav"]).is_absolute() else Path.cwd() / s["wav"]).resolve().as_posix(), "start": s["start"]} for s in segs], "desaturar": 0, "kit": KIT,
        "estilo": ESTILO, "estatica": ESTATICA, "relleno": RELLENO, "marcas_docs": pj.get("marcas_docs", {}), "autodestruccion": (pj.get("autodestruccion") or {}).get("tipo")}
(carpeta / "datos_ae.json").write_text(json.dumps(DATA, indent=1), encoding="utf-8")
print(COMP, "|", len(secciones), "secciones |", len(subs), "subtitulos | total", total)
print("subtitulos:", " / ".join(" ".join(w["w"] for w in s["words"]) for s in subs))
print("etiquetas:", avisos or "todas con hueco libre")
if "--solo-datos" in sys.argv:
    sys.exit()

# ---------- armado en After
sys.path.insert(0, r"D:\motion category ai library\tools\mcp")
import ss_motion_mcp as M  # noqa: E402
_r = M.run_jsx
M.run_jsx = lambda body, *a, **k: _r("app.beginSuppressDialogs();\ntry {\n" + body + "\n} finally { app.endSuppressDialogs(false); }", *a, **k)
print(M.run_jsx(f"""var f = new File("{AEP}");
if (app.project.file && app.project.file.fsName.replace(/\\\\/g, "/") === f.fsName.replace(/\\\\/g, "/")) return "ya abierto";
if (app.project.dirty && app.project.file) app.project.save();
if (f.exists) app.open(f); else {{ app.newProject(); app.project.save(f); }}
try {{ app.project.gpuAccelType = GpuAccelType.SOFTWARE; }} catch (e) {{}}
return app.project.file.fsName;""", timeout=240))
if ESTILO.get("builder") in ("cinta", "ccc"):   # "Night Transmission" (ae/cinta.jsx) or Cool Culture Club (ae/ccc.jsx): own look, same timeline and data
    BUILDER = ESTILO["builder"]
    _mk = marca_dir(pj.get("marca")) if pj.get("marca") else None
    _fx = lambda n: ((_mk / "kit" / "fx" / f"{n}.mp4").as_posix() if _mk and (_mk / "kit" / "fx" / f"{n}.mp4").exists() else "")
    _brand = json.loads((_mk / "brand.json").read_text(encoding="utf-8")) if _mk and (_mk / "brand.json").exists() else {}
    DATA.update({"claves": [k[1] for k in pj.get("palabras_clave", []) if len(k) > 1], "titulos": pj.get("titulos", {}), "handle": _brand.get("handle", ""),
                 "fx_humo": _fx("humo_volutas"), "fx_estatica": _fx("estatica_rafaga")})
    _fin = carpeta / "final" / "autodestruccion.mp4"   # the generated self-destruct (engine/final.py)
    if _fin.exists():
        _d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(_fin)], capture_output=True, text=True).stdout.strip() or 5.17)
        DATA.update({"final_clip": _fin.as_posix(), "final_dur": round(_d, 3)})
    for sec in DATA["secciones"]:
        if sec.get("mate"):
            sec["clip"] = str(sec["mate"]).replace("/mates/", "/clips/").rsplit(".", 1)[0] + ".mp4"
            _full = Path(sec["clip"][:-4] + "_full.mp4")   # the talking clip + its new footage (engine/continuar.py)
            if _full.exists():
                sec["clip"] = _full.as_posix()
        # zoom jumps (ep05 v2 review: "reframes, the jumps we used"): while he is on screen the edit cuts between framings at
        # sentence ends (at least SALTO_MIN s apart), punching in toward his head (median head box of his talking clip)
        if sec.get("tipo") in ("gancho", "cabeza"):
            SALTO_MIN, NIV = 2.4, [1.0, 1.3, 1.12, 1.4]
            fins = sorted(w["e"] for g in tl["segmentos"] for i, w in enumerate(g["words"])
                          if w["w"][-1:] in ".?!:" and i < len(g["words"]) - 1 or (i == len(g["words"]) - 1))
            cortes, ult = [], sec["ini"]
            for e in fins:
                if sec["ini"] + 1.5 < e < sec["fin"] - 1.6 and e - ult >= SALTO_MIN:
                    cortes.append(round(e + 0.05, 3)); ult = e
            sec["saltos"] = [[sec["ini"], NIV[0]]] + [[t, NIV[(i + 1) % len(NIV)]] for i, t in enumerate(cortes)]
            cj = sorted(CAJAS.get(sec.get("id"), []), key=lambda c: c["caja"][1])
            if cj:
                x0, y0, x1, y1 = cj[len(cj) // 2]["caja"]
                sec["cabeza_xy"] = [round((x0 + x1) / 2), round(y0 + (y1 - y0) * 0.14)]
    if BUILDER == "ccc":   # the bricolage kit, the type wall, the artist's photocopy cutout and the magnifier details (word -> time)
        _words = [w for g in tl["segmentos"] for w in g["words"]]
        _off = {g["id"]: next((x["start"] for x in segs if x["id"] == g["id"]), g["start"]) - g["start"] for g in tl["segmentos"]}
        def _t(pal, desde=0.0):
            for g in tl["segmentos"]:
                for w in g["words"]:
                    if w["w"].lower().strip(".,?!:;\"'").startswith(pal.lower()) and w["s"] + _off[g["id"]] >= desde:
                        return round(w["s"] + _off[g["id"]], 3)
            return None
        _det = {}
        for stem, ds in (pj.get("detalles") or {}).items():
            _det[stem] = [dict(d, t=_t(d["palabra"])) for d in ds]
        DATA.update({"kit": (_mk / "kit" / "bricolage").as_posix(), "type_wall": (_mk / "kit" / "loops" / "kinetic_type_wall.mp4").as_posix(),
                     "retrato_bricolage": (carpeta / "retrato_bricolage.png").as_posix(), "detalles": _det, "etiqueta": pj.get("etiqueta_nombre", pj["artista"])})
    (carpeta / "datos_ae.json").write_text(json.dumps(DATA, indent=1), encoding="utf-8")
    _obj = "CCC" if BUILDER == "ccc" else "CINTA"
    r = M.run_jsx((HERE.parent / "ae" / f"{BUILDER}.jsx").read_text(encoding="utf-8") + chr(10) + f"var r = {_obj}.build({json.dumps(DATA)}); app.project.save(); return r;", timeout=1800, includes=())
    print(r.splitlines()[0])
    SON = ESTILO.get("sonidos", {})
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
    sys.exit()
base = (HERE.parent / "ae" / "collage.jsx").read_text(encoding="utf-8")
r = M.run_jsx(base + f"\nvar r = COLLAGE.build({json.dumps(DATA)}); app.project.save(); return r;", timeout=1800, includes=())
print(r.splitlines()[0])
# comprobacion con las medidas reales de After
malos = []
for ln in r.splitlines()[1:]:
    p = ln.split("|")
    if len(p) != 8:
        continue
    que, si, t, x, y, w, h = p[0], int(p[1]), float(p[2]), float(p[3]), float(p[4]), float(p[5]), float(p[6])
    sec = secciones[si]
    c = choca([x - w / 2, y - h / 2, x + w / 2, y + h / 2], sec, t, sec["fin"] + 0.3, [])
    if c:
        malos.append(f"{que} (seccion {si}): {c}")
print("chequeo con medidas reales:", malos or "sin choques ni textos fuera de la zona segura")
cues = []
habla = lambda x: x["tipo"] in ("cabeza", "gancho")
for i, sec in enumerate(secciones):
    if i:
        pv = secciones[i - 1]
        if (habla(pv) and not pv.get("corte")) != habla(sec):
            cues.append({"t": round(sec["ini"] - 0.32, 3), "sfx": "whoosh", "dur": 0.6, "gain": -4, "why": "franjas / salto a " + sec["tipo"]})
        else:   # v10c: deslizamiento de 1.2 s entre obras
            cues.append({"t": round(sec["ini"] - 0.85, 3), "sfx": "whoosh", "dur": 1.1, "gain": -7, "why": "deslizamiento a " + sec["tipo"]})
            cues.append({"t": round(sec["ini"] - 0.05, 3), "sfx": "tick", "gain": -12, "why": "llega"})
    if sec["tipo"] == "gancho" and sec.get("inserto"):
        cues.append({"t": round(sec["inserto"]["t0"] - 1.0, 3), "sfx": "riser", "dur": 1.0, "gain": -12, "why": "sube hacia la obra del gancho"})
    if sec.get("corte"):
        cues.append({"t": round(sec["corte"] + 0.05, 3), "sfx": "sub", "gain": -10, "why": "la obra llena el cuadro"})
    if habla(sec) and not sec.get("corte"):
        for o in sec.get("obras", []):
            cues.append({"t": round(max(min(o["t"], sec["fin"] - 1.5), sec["ini"] + 0.2) + 0.02, 3), "sfx": "click", "gain": -8, "why": "tarjeta de detalle"})
    if sec["tipo"] == "ficha":
        cues.append({"t": round(sec["ini"] + 0.5, 3), "sfx": "type", "gain": -11, "why": "fechas"})
    if sec["tipo"] == "cita":
        cues.append({"t": round(sec["ini"] + 0.1, 3), "sfx": "chime", "gain": -12, "why": "cita"})
    if sec.get("inserto"):
        cues.append({"t": round(sec["inserto"]["t0"] - 0.3, 3), "sfx": "whoosh", "dur": 0.6, "gain": -4, "why": "inserto entra"})
        cues.append({"t": round(sec["inserto"]["t1"] - 0.3, 3), "sfx": "whoosh", "dur": 0.6, "gain": -5, "why": "vuelve la cabeza"})
    if sec.get("corte"):
        cues.append({"t": round(sec["corte"] - 0.3, 3), "sfx": "whoosh", "dur": 0.6, "gain": -4, "why": "corte a la obra"})
    for e in sec.get("etqs", []):
        cues.append({"t": round(e["t"] + 0.03, 3), "sfx": "pop", "gain": -6, "why": "etiqueta " + e["txt"]})
    if sec["tipo"] == "obra":
        cues.append({"t": round(sec["ini"] + 0.33, 3), "sfx": "swish", "gain": -9, "why": "cartela"})
    for ca in sec.get("cartelas", []):
        cues.append({"t": round(ca["t"] + 0.03, 3), "sfx": "swish", "gain": -9, "why": "cartela"})
    if sec["tipo"] == "ficha":
        cues.append({"t": round(sec["ini"] + 0.65, 3), "sfx": "shimmer", "gain": -8, "why": "la silueta se llena"})
cues.append({"t": 0.38, "sfx": "hit", "gain": -5, "why": "gancho"})
if DATA.get("autodestruccion"):   # la firma del final
    cues.append({"t": round(total - 1.7, 3), "sfx": "glitch", "gain": -4, "why": "autodestruccion"})
    cues.append({"t": round(total - 1.2, 3), "sfx": "sub", "gain": -6, "why": "autodestruccion"})
SON = ESTILO.get("sonidos", {})   # el estilo puede cambiar cada sonido (p. ej. whoosh -> glitch en un canal de terror)
for c_ in cues:
    c_["sfx"] = SON.get(c_["sfx"], c_["sfx"])
cues.sort(key=lambda c: c["t"])
print(str(M.t_add_sound(cues=cues, comp=COMP, auto=False))[:160])
print(M.t_check_layout(comps=[COMP]))
print(M.run_jsx('app.project.save(); return "guardado";', includes=()))

if "--render" in sys.argv:
    subprocess.run([sys.executable, str(HERE / "render_ae.py"), str(carpeta)], check=True)
