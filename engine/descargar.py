"""Shared downloader for real media, with fallbacks for pages that block scripts (review 2026-11-15: "more effective scraping").
Order, cheapest first, each tried only when the previous one is blocked (403/406/451/503, a Cloudflare challenge, or an HTML
page where a file was expected):
  1. plain HTTP with a descriptive User-Agent (what Wikimedia and the US archives ask bots to send); 429 -> respects Retry-After
  2. curl_cffi with a real Chrome TLS/HTTP2 fingerprint (most 403s are fingerprint blocks)
  3. the Wayback Machine copy of the same URL (id_ = the raw archived file)
Pages that build their gallery with JavaScript: medios_de_pagina(url) opens them in Playwright (Chromium, headless) and lists
the image/video URLs; social media (X, Instagram, Reddit, Flickr, Tumblr...) goes through gallery-dl, video through yt-dlp
with --impersonate. Cookies: only from the user's own browser and accounts, opt-in with SHORTS_COOKIES_BROWSER=firefox|chrome|edge.
Never: CAPTCHA solvers, other people's accounts, proxy pools. A CAPTCHA page is reported as blocked, for a manual download.
Usage: python descargar.py <url> <out file>          download one file with the fallbacks
       python descargar.py --pagina <url>             list the media URLs a JS page loads
       python descargar.py --galeria <url> <folder>   gallery-dl into a folder"""
import json, os, re, shutil, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

UA = "shorts-factory/1.1 (documentary research; real archival media)"
COOKIES = os.environ.get("SHORTS_COOKIES_BROWSER", "").strip()   # opt-in, the user's own browser only
BLOQUEO = (401, 403, 406, 409, 451, 503)
# a challenge wall, not a page that merely has a reCAPTCHA in its contact form (PhilSA, 2026-11-15)
CAPTCHA = re.compile(rb"<title>[^<]*(just a moment|attention required|access denied|are you a robot|verify you are human|captcha)[^<]*</title>|cf-chl-|/cdn-cgi/challenge-platform", re.I)


class ErrorHTTP(Exception):
    def __init__(self, code, url, via=""):
        super().__init__(f"HTTP {code} for {url}" + (f" ({via})" if via else "")); self.code = code; self.url = url


def _espera(retry_after, intento):
    try:
        return min(300, int(retry_after))
    except (TypeError, ValueError):
        return min(300, 20 * (intento + 1))


def _bloqueado(code, data, esperaba_archivo):
    if code in BLOQUEO:
        return True
    head = (data or b"")[:4000]
    return esperaba_archivo and (CAPTCHA.search(head) is not None or head.lstrip()[:15].lower().startswith((b"<!doctype html", b"<html")))


def _urllib(url, timeout):
    r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout)
    return r.status, r.read(), r.headers


def _curl(url, timeout):
    from curl_cffi import requests as cr   # pip curl_cffi (MIT)
    r = cr.get(url, impersonate="chrome", timeout=timeout, allow_redirects=True)
    return r.status_code, r.content, r.headers


def _wayback(url, timeout):
    api = "https://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe="")
    snap = json.loads(urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": UA}), timeout=60).read())
    near = (snap.get("archived_snapshots") or {}).get("closest") or {}
    if not near.get("available"):
        raise ErrorHTTP(404, url, "no Wayback copy")
    raw = re.sub(r"/web/(\d+)/", r"/web/\1id_/", near["url"])
    return _urllib(raw, timeout)


def traer(url, timeout=120, esperaba_archivo=True, reintentos_429=4, quiet=False):
    """Bytes of url, trying plain HTTP, then a Chrome fingerprint, then the Wayback copy. Raises ErrorHTTP (with .code) when
    every route fails; a 429 that outlasts the retries is raised as 429 so callers can switch to a smaller file."""
    ultimo = None
    for via, f in (("http", _urllib), ("chrome", _curl), ("wayback", _wayback)):
        for intento in range(reintentos_429 + 1):
            try:
                code, data, hdr = f(url, timeout)
            except urllib.error.HTTPError as e:
                code, data, hdr = e.code, b"", e.headers
            except ErrorHTTP as e:
                code, data, hdr = e.code, b"", {}
            except ImportError:
                code, data, hdr = -1, b"", {}
            except Exception as e:   # network errors: let the next route try
                code, data, hdr = -2, str(e).encode(), {}
            if code == 429 and via != "wayback":
                if intento == reintentos_429:
                    raise ErrorHTTP(429, url, via)
                time.sleep(_espera((hdr or {}).get("Retry-After"), intento)); continue
            break
        if 200 <= code < 300 and not _bloqueado(code, data, esperaba_archivo):
            if via != "http" and not quiet:
                print(f"  downloaded via {via}: {url[:90]}", flush=True)
            return data
        ultimo = code
        if code in (400, 404, 410) and via == "http":
            break   # the file is not there: a fingerprint will not change that (Wikimedia thumbnail sizes rely on this)
    if ultimo in (400, 404, 410):
        raise ErrorHTTP(ultimo, url, "not found")
    raise ErrorHTTP(ultimo, url, "blocked on every route" + (" (looks like a CAPTCHA page: download it by hand)" if ultimo == 200 else ""))


def ytdlp_args():
    """Flags that make yt-dlp look like Chrome, wait between requests and (opt-in) use the user's own cookies."""
    a = ["--impersonate", "chrome", "--sleep-requests", "1", "--retries", "5", "--fragment-retries", "5"]
    return a + (["--cookies-from-browser", COOKIES] if COOKIES else [])


def ytdlp():
    exe = next(iter(Path.home().glob("AppData/Local/Microsoft/WinGet/Packages/yt-dlp*/yt-dlp.exe")), None) or shutil.which("yt-dlp")
    return [str(exe)] if exe else [sys.executable, "-m", "yt_dlp"]


def galeria(url, carpeta):
    """gallery-dl (GPL-2.0, run as a separate program) for X, Instagram, Reddit, Flickr, Tumblr, DeviantArt... -> files in carpeta."""
    carpeta = Path(carpeta); carpeta.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "gallery_dl", "--sleep-request", "1", "-D", str(carpeta), url]
    if COOKIES:
        cmd[3:3] = ["--cookies-from-browser", COOKIES]
    subprocess.run(cmd, check=True)
    return sorted(p for p in carpeta.iterdir() if p.is_file())


def medios_de_pagina(url, espera_ms=4000):
    """Open a page in headless Chromium (Playwright) and list the image and video URLs it shows or loads over the network,
    biggest images first. For galleries built with JavaScript; the files are then fetched with traer()."""
    from playwright.sync_api import sync_playwright
    vistos = {}
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(user_agent=None, viewport={"width": 1440, "height": 1000})
        pg.on("response", lambda r: vistos.setdefault(r.url, r.headers.get("content-type", "")))
        pg.goto(url, wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_timeout(espera_ms)
        for _ in range(4):   # lazy galleries load on scroll
            pg.mouse.wheel(0, 2500); pg.wait_for_timeout(800)
        html = pg.content()
        if CAPTCHA.search(html[:20000].encode("utf-8", "ignore")):
            b.close(); raise ErrorHTTP(200, url, "CAPTCHA page: open it by hand")
        tam = pg.eval_on_selector_all("img", "els => els.map(e => [e.currentSrc || e.src, e.naturalWidth * e.naturalHeight])")
        vids = pg.eval_on_selector_all("video, video source", "els => els.map(e => e.currentSrc || e.src)")
        b.close()
    imgs = {u: a for u, a in tam if u and u.startswith("http")}
    for u, ct in vistos.items():
        if ct.startswith("image/") and u not in imgs:
            imgs[u] = 0
    videos = [u for u in vids if u and u.startswith("http")] + [u for u, ct in vistos.items() if ct.startswith("video/")]
    return {"imagenes": [u for u, _ in sorted(imgs.items(), key=lambda kv: -kv[1])], "videos": list(dict.fromkeys(videos))}


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "--pagina":
        print(json.dumps(medios_de_pagina(a[1]), indent=1))
    elif a[0] == "--galeria":
        for f in galeria(a[1], a[2]):
            print(f)
    else:
        Path(a[1]).write_bytes(traer(a[0])); print(a[1], Path(a[1]).stat().st_size // 1024, "KB")
