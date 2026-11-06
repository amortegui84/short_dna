"""Path "brand": the brand's website -> a brand kit Claude turns into components. Reads only the public page the user gives:
logo candidates (inline/linked SVG in the header, apple-touch-icon, og:image, favicons), colours (CSS custom properties and the
most used hex values), fonts (font-family, Google Fonts links), name, tagline. Writes <work_dir>/marcas/<slug>/:
marca.json, logo_* files, and a Motion DNA brand profile draft (brand_motion_dna.json, schema in Motion DNA
library/brands/_schema.md) to import with `python tools/brand.py new/import` in Motion DNA.
Next (Claude, with the skill): check the logo and colours with the user, then build components (lower thirds, title cards,
end card, transitions) with Motion DNA (apply_brand, kit pieces) and, if wanted, Figma frames with the brand tokens.
Never type anything into the site; never use brand logos in library examples (house rule).
Usage: python marca.py <url> <slug>"""
import collections, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import CFG  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (shorts-factory brand reader)"}
url, slug = sys.argv[1], sys.argv[2]
d = Path(CFG["work_dir"]) / "marcas" / slug; d.mkdir(parents=True, exist_ok=True)


def get(u, binary=False):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()
    return r if binary else r.decode("utf-8", "replace")


html = get(url)
abs_ = lambda u: urllib.parse.urljoin(url, u)
css = "".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
for href in re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)', html)[:6]:
    try:
        css += get(abs_(href))
    except Exception:
        pass
meta = lambda p: (re.search(rf'<meta[^>]+(?:property|name)=["\']{p}["\'][^>]+content=["\']([^"\']+)', html) or [None, None])[1]
nombre = meta("og:site_name") or (re.search(r"<title>(.*?)</title>", html, re.S) or [None, slug])[1].strip()
# colores: variables CSS con nombre de marca primero, luego los hex mas usados (sin blancos ni negros puros)
vars_ = dict(re.findall(r"--([\w-]*(?:brand|primary|accent|secondary|color)[\w-]*)\s*:\s*(#[0-9a-fA-F]{3,8})", css))
hexes = [h.upper() for h in re.findall(r"#[0-9a-fA-F]{6}\b", css + html)]
comunes = [h for h, _ in collections.Counter(hexes).most_common(20) if h not in ("#FFFFFF", "#000000")][:8]
fuentes = [f.strip(" '\"") for f in re.findall(r"font-family\s*:\s*([^;}{]+)", css)]
fuentes = [f.split(",")[0].strip(" '\"") for f in fuentes]
fuentes = [f for f, _ in collections.Counter(fuentes).most_common(6) if f and not f.startswith("var(")]
google = re.findall(r"fonts\.googleapis\.com/css2?\?family=([^\"'&]+)", html)
# logos
cands = []
for m in re.finditer(r'<(?:img|link)[^>]+(?:src|href)=["\']([^"\']+)["\'][^>]*>', html):
    tag, u = m.group(0).lower(), m.group(1)
    if "logo" in tag or "apple-touch-icon" in tag or ('rel="icon"' in tag and u.endswith(".svg")):
        cands.append(abs_(u))
if meta("og:image"):
    cands.append(abs_(meta("og:image")))
svg_inline = re.search(r"<header.*?(<svg.*?</svg>)", html, re.S)
logos = []
if svg_inline:
    (d / "logo_inline.svg").write_text(svg_inline.group(1), encoding="utf-8"); logos.append("logo_inline.svg")
for i, u in enumerate(dict.fromkeys(cands)):
    ext = Path(urllib.parse.urlparse(u).path).suffix.lower() or ".png"
    if ext not in (".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico"):
        continue
    try:
        (d / f"logo_{i}{ext}").write_bytes(get(u, True)); logos.append(f"logo_{i}{ext}")
    except Exception:
        pass
    if len(logos) >= 6:
        break
kit = {"nombre": nombre, "url": url, "lema": meta("og:description") or meta("description"), "colores_var": vars_, "colores": comunes,
       "fuentes": fuentes, "google_fonts": [urllib.parse.unquote(g).replace("+", " ") for g in google], "logos": logos}
(d / "marca.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")
cols = list(vars_.values())[:3] or comunes[:3]
draft = {"name": nombre, "slug": slug, "identity": {"colors": {f"c{i + 1}": c for i, c in enumerate(cols)},
         "fonts": {"title": (fuentes or ["Inter"])[0], "text": (fuentes[1:] or fuentes or ["Inter"])[0]}, "logo": logos[0] if logos else ""},
         "feel": {"energy": [2, 3], "tones": ["modern"], "style": "Modern"}, "rules": [], "notes": "draft from " + url + "; confirm colours, fonts and logo with the user"}
(d / "brand_motion_dna.json").write_text(json.dumps(draft, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(kit, ensure_ascii=False))
