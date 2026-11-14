"""Descarga las obras de dominio publico listadas en proyecto.json ("obras_descarga": {nombre: url de Wikimedia} o
{nombre: {"url", "licencia", "credito", "pagina"}} para guardar la licencia de cada archivo: CC BY / BY-SA piden credito).
Guarda obras/<nombre>.jpg (1920 px) y obras/CREDITOS.json. Uso: python obras.py <carpeta>"""
import json, re, subprocess, sys, time, urllib.request
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from comun import proyecto  # noqa: E402

UA = {"User-Agent": "avatares-arte-pilot/1.0 (local research)"}
carpeta = Path(sys.argv[1])
pj = proyecto(carpeta)
dest = carpeta / "obras"
dest.mkdir(exist_ok=True)
YTDLP = next(iter(Path.home().glob("AppData/Local/Microsoft/WinGet/Packages/yt-dlp*/yt-dlp.exe")), None)


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
                crudo.write_bytes(urllib.request.urlopen(urllib.request.Request(u["url"], headers=UA), timeout=180).read())
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or intento == 7:
                    raise
                time.sleep(60 * (intento + 1))
    elif u["url"].lower().split("?")[0].endswith((".mp4", ".webm", ".mov", ".ogv", ".m4v")):
        # direct file: ffmpeg reads only the stretch over HTTP (an archive reel can be gigabytes)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-user_agent", UA["User-Agent"], *corte, "-i", u["url"], "-an",
                        "-vf", vf, "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(f)], check=True)
        return f
    else:
        subprocess.run([str(YTDLP), "-f", "best[height<=1080][ext=mp4]/best[height<=1080]", "-o", str(crudo), "--no-playlist", u["url"]], check=True)
    corte = (["-ss", str(u["desde"])] if u.get("desde") is not None else []) + (["-to", str(u["hasta"])] if u.get("hasta") is not None else [])
    subprocess.run(["ffmpeg", "-v", "error", "-y", *corte, "-i", str(crudo), "-an", "-vf", vf,
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(f)], check=True)
    crudo.unlink()
    return f


for n, url in pj["obras_descarga"].items():
    if isinstance(url, dict) and url.get("video"):
        f = video(n, url); print(f.name, f.stat().st_size // 1024, "KB", flush=True); continue
    url = url["url"] if isinstance(url, dict) else url
    # Wikimedia answers 400 to thumbnail widths outside its fixed list (2026-11-13, ep16 "1600px"): use 1280 or 1920
    url = re.sub(r"(/thumb/.+/)(\d+)px-", lambda m: m.group(1) + ("1280" if int(m.group(2)) <= 1280 else "1920") + "px-", url) \
        if "upload.wikimedia.org" in url else url
    f = dest / f"{n}.jpg"
    if not f.exists():
        # Wikimedia answers 429 to many original-file downloads and asks for thumbnails in its fixed sizes (2026-11-13, ep17):
        # on a 429 the same file is asked as a 1920 px, then 1280 px thumbnail (a thumbnail wider than the original gives 4xx)
        m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons/)([0-9a-f]/[0-9a-f]{2}/)([^/]+)$", url)
        alternativas = [url] + ([f"{m.group(1)}thumb/{m.group(2)}{m.group(3)}/{w}px-{m.group(3)}" + (".png" if m.group(3).lower().endswith((".svg", ".tif", ".tiff")) else "")
                                 for w in (1920, 1280)] if m and not url.lower().endswith((".webm", ".ogv", ".pdf")) else [])
        data = None
        for intento in range(6):
            for u_alt in alternativas:
                try:
                    data = urllib.request.urlopen(urllib.request.Request(u_alt, headers=UA), timeout=90).read()
                    break
                except urllib.error.HTTPError as e:
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
        else:
            Image.open(tmp).convert("RGB").save(f, quality=92)   # verifica que es una imagen real
        tmp.unlink()
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
