"""Descarga las obras de dominio publico listadas en proyecto.json ("obras_descarga": {nombre: url de Wikimedia} o
{nombre: {"url", "licencia", "credito", "pagina"}} para guardar la licencia de cada archivo: CC BY / BY-SA piden credito).
Guarda obras/<nombre>.jpg (1920 px) y obras/CREDITOS.json. Uso: python obras.py <carpeta>"""
import json, re, subprocess, sys, time
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from comun import proyecto  # noqa: E402
import descargar  # noqa: E402  plain HTTP -> Chrome fingerprint -> Wayback; yt-dlp/gallery-dl flags (2026-11-15)

UA = {"User-Agent": descargar.UA}
carpeta = Path(sys.argv[1])
pj = proyecto(carpeta)
dest = carpeta / "obras"
dest.mkdir(exist_ok=True)
YTDLP = descargar.ytdlp()


def video(n, u):
    """Archival footage: {"video": true, "url": <direct file or a page yt-dlp understands>, "desde": s, "hasta": s} ->
    obras/<n>.mp4, silent, 1080 px wide at most, only the chosen stretch (the edit loops it if short)."""
    f = dest / f"{n}.mp4"
    if f.exists():
        return f
    crudo = dest / f"_{n}_crudo.mp4"
    corte = (["-ss", str(u["desde"])] if u.get("desde") is not None else []) + (["-to", str(u["hasta"])] if u.get("hasta") is not None else [])
    vf = ((u["recorte"] + ",") if u.get("recorte") else "") + "scale='min(1080,iw)':-2"   # "recorte": an ffmpeg crop, e.g. to drop a burned-in timestamp
    if "upload.wikimedia.org" in u["url"]:
        # Commons files are small; Wikimedia answers 429 to streamed reads when busy (2026-11-13, ep18): download the whole
        # file with backoff, then cut it locally
        for intento in range(8):
            try:
                crudo.write_bytes(descargar.traer(u["url"], timeout=180)); break
            except descargar.ErrorHTTP as e:
                if e.code != 429 or intento == 7:
                    raise
                time.sleep(60 * (intento + 1))
    elif u["url"].lower().split("?")[0].endswith((".mp4", ".webm", ".mov", ".ogv", ".m4v")):
        # direct file: ffmpeg reads only the stretch over HTTP (an archive reel can be gigabytes); a server that blocks
        # ffmpeg (403) gets the whole file through the fallbacks instead, cut locally below
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-user_agent", UA["User-Agent"], *corte, "-i", u["url"], "-an",
                            "-vf", vf, "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(f)])
        if r.returncode == 0:
            return f
        crudo.write_bytes(descargar.traer(u["url"], timeout=600))
    else:
        # yt-dlp looking like Chrome, with pauses and (opt-in) the user's own browser cookies; X/TikTok/news pages too
        subprocess.run([*YTDLP, *descargar.ytdlp_args(), "-f", "best[height<=1080][ext=mp4]/best[height<=1080]/best",
                        "--merge-output-format", "mp4", "-o", str(crudo), "--no-playlist", u["url"]], check=True)
    corte = (["-ss", str(u["desde"])] if u.get("desde") is not None else []) + (["-to", str(u["hasta"])] if u.get("hasta") is not None else [])
    subprocess.run(["ffmpeg", "-v", "error", "-y", *corte, "-i", str(crudo), "-an", "-vf", vf,
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(f)], check=True)
    crudo.unlink()
    return f


for n, url in pj["obras_descarga"].items():
    if isinstance(url, dict) and url.get("video"):
        f = video(n, url); print(f.name, f.stat().st_size // 1024, "KB", flush=True); continue
    spec = url if isinstance(url, dict) else {}
    url = url["url"] if isinstance(url, dict) else url
    if spec.get("de_pagina") is not None:
        # a gallery built with JavaScript: open the page in Playwright and take its N-th biggest image (0 = biggest)
        url = descargar.medios_de_pagina(url)["imagenes"][int(spec["de_pagina"])]
    elif spec.get("galeria") is not None and not (dest / f"{n}.jpg").exists():
        # social posts (X, Instagram, Reddit, Flickr...): gallery-dl, N-th file of the post
        url = None
        archivos = descargar.galeria(spec["url"], dest / f"_{n}_galeria")
        tmp_g = archivos[int(spec["galeria"])]
    # Wikimedia answers 400 to thumbnail widths outside its fixed list (2026-11-13, ep16 "1600px"): use 1280 or 1920
    url = re.sub(r"(/thumb/.+/)(\d+)px-", lambda m: m.group(1) + ("1280" if int(m.group(2)) <= 1280 else "1920") + "px-", url) \
        if url and "upload.wikimedia.org" in url else url
    f = dest / f"{n}.jpg"
    if not f.exists():
        # Wikimedia answers 429 to many original-file downloads and asks for thumbnails in its fixed sizes (2026-11-13, ep17):
        # on a 429 the same file is asked as a 1920 px, then 1280 px thumbnail (a thumbnail wider than the original gives 4xx)
        m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons/)([0-9a-f]/[0-9a-f]{2}/)([^/]+)$", url or "")
        alternativas = ([url] if url else []) + ([f"{m.group(1)}thumb/{m.group(2)}{m.group(3)}/{w}px-{m.group(3)}" + (".png" if m.group(3).lower().endswith((".svg", ".tif", ".tiff")) else "")
                                 for w in (1920, 1280)] if m and not url.lower().endswith((".webm", ".ogv", ".pdf")) else [])
        data = tmp_g.read_bytes() if url is None else None
        for intento in range(0 if data else 6):
            for u_alt in alternativas:
                try:
                    data = descargar.traer(u_alt, timeout=90, reintentos_429=0, quiet=False)
                    break
                except descargar.ErrorHTTP as e:
                    if e.code not in (429, 400, 404) or (e.code != 429 and u_alt == url):
                        raise
            if data:
                break
            if intento == 5:
                raise SystemExit(f"{n}: Wikimedia keeps answering 429")
            time.sleep(20 * (intento + 1))
        tmp = dest / f"{n}.descarga"
        tmp.write_bytes(data)
        if data[:5] == b"%PDF-":
            # a page of a public-domain PDF (declassified records, ep18): "pdf_pagina" (1-based) rendered at ~2x
            import fitz
            u = pj["obras_descarga"][n]
            doc = fitz.open(str(tmp))
            doc[int(u.get("pdf_pagina", 1)) - 1].get_pixmap(matrix=fitz.Matrix(2.5, 2.5)).save(str(dest / f"{n}.png"))
            doc.close()
            Image.open(dest / f"{n}.png").convert("RGB").save(f, quality=92); (dest / f"{n}.png").unlink()
        elif b"<svg" in data[:2000]:
            # Wikimedia diagrams are often SVG (ep21): rasterize with fitz on a white ground
            import fitz
            doc = fitz.open(str(tmp), filetype="svg")
            pg = doc[0]; z = max(1.0, 2400 / max(pg.rect.width, pg.rect.height))
            pg.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False).save(str(dest / f"{n}.png"))
            doc.close()
            Image.open(dest / f"{n}.png").convert("RGB").save(f, quality=92); (dest / f"{n}.png").unlink()
        else:
            Image.open(tmp).convert("RGB").save(f, quality=92)   # verifica que es una imagen real
        tmp.unlink()
        if url is None:
            import shutil; shutil.rmtree(dest / f"_{n}_galeria", ignore_errors=True)
        time.sleep(1)
    print(f.name, f.stat().st_size // 1024, "KB", flush=True)
cred_p = dest / "CREDITOS.json"
cred = json.loads(cred_p.read_text(encoding="utf-8")) if cred_p.exists() else {}
cred.update({"autor": pj["artista"], "fuente": "Wikimedia Commons / US government archives",
             "licencia": "per file below (real media keeps its own license and credit)",
             "urls": {n: (u["url"] if isinstance(u, dict) else u) for n, u in pj["obras_descarga"].items()}})
for n, u in pj["obras_descarga"].items():
    if isinstance(u, dict):
        cred[n] = {"fuente": u.get("pagina", u["url"]), "licencia": u.get("licencia", "check"), "credito": u.get("credito", ""), "real": True}
cred_p.write_text(json.dumps(cred, indent=2, ensure_ascii=False), encoding="utf-8")
