"""Screenshots of Google Maps for the map zoom of a place (haunted-places format, 2026-11-15; the user asked for plain 2D
screenshots: "puede ser 2d lo de google maps, ¿no puedes solo entrar y tomar screenshots?").
Opens Google Maps in headless Chromium (Playwright) with no account, answers the cookie wall with the most private option
("Reject all"), hides the search box and controls, and saves one vertical 1080x1920 screenshot per zoom level, centred on
the place, in the map and/or satellite view. The video must show "© Google" while these play (reaccion.py does it from the
plan's credit). No personal data is typed anywhere; nothing is logged in.
Usage: python mapa_capturas.py <out folder> <lat> <lng> [--z 3 6 9 12 15 17] [--vista mapa|satelite|ambas]
Writes <out>/mapa_<vista>_z<z>.png and <out>/mapa.json (centre and zoom list) for the "mapa" plan in reaccion.json."""
import argparse, json, time
from pathlib import Path

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("lat", type=float); ap.add_argument("lng", type=float)
ap.add_argument("--z", type=int, nargs="+", default=[3, 6, 9, 12, 15, 17])
ap.add_argument("--vista", default="ambas", choices=["mapa", "satelite", "ambas"])
ap.add_argument("--idioma", default="en")
a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
vistas = ["mapa", "satelite"] if a.vista == "ambas" else [a.vista]
OCULTAR = """#omnibox-container, #omnibox, .app-viewcard-strip, #minimap, .scene-footer-container, #runway-expand-button,
  .widget-scene-imagery-render, [role="navigation"], .gb_Ad, #gb, .searchbox, .app-horizontal-widget-holder,
  .widget-zoom, #assistive-chips, .JdG3E, .widget-consent-button, .scene-footer, [aria-label="Show Your Location"],
  .app-bottom-content-anchor, .yHc72, .MlqQ3d, .Hk4XGb, .gb_va, button[aria-label*="Layers"], .TUqRYe, .ZHkpSb
  { display: none !important; visibility: hidden !important; }"""


def rechazar_cookies(pg):
    for txt in ("Reject all", "Rechazar todo", "Alle ablehnen", "Tout refuser"):
        b = pg.get_by_role("button", name=txt)
        if b.count():
            b.first.click(); pg.wait_for_timeout(1500); return True
    return False


with sync_playwright() as p:
    br = p.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1080, "height": 1920}, locale=a.idioma)
    pg = ctx.new_page()
    for v in vistas:
        for z in a.z:
            capa = "/data=!3m1!1e3" if v == "satelite" else ""
            pg.goto(f"https://www.google.com/maps/@{a.lat},{a.lng},{z}z{capa}?hl={a.idioma}", wait_until="domcontentloaded", timeout=90000)
            if "consent." in pg.url:
                rechazar_cookies(pg)
                pg.goto(f"https://www.google.com/maps/@{a.lat},{a.lng},{z}z{capa}?hl={a.idioma}", wait_until="domcontentloaded", timeout=90000)
            pg.wait_for_timeout(2500)
            pg.add_style_tag(content=OCULTAR)
            pg.wait_for_timeout(5000 if v == "satelite" else 3500)   # tiles finish loading
            f = out / f"mapa_{v}_z{z}.png"
            pg.screenshot(path=str(f))
            print(f.name, flush=True)
    br.close()
(out / "mapa.json").write_text(json.dumps({"lat": a.lat, "lng": a.lng, "z": a.z, "vistas": vistas}, indent=1), encoding="utf-8")
