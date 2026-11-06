"""Descarga las obras de dominio publico listadas en proyecto.json ("obras_descarga": {nombre: url de Wikimedia}).
Guarda obras/<nombre>.jpg (1920 px) y obras/CREDITOS.json. Uso: python obras.py <carpeta>"""
import json, sys, time, urllib.request
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from comun import proyecto  # noqa: E402

UA = {"User-Agent": "avatares-arte-pilot/1.0 (local research)"}
carpeta = Path(sys.argv[1])
pj = proyecto(carpeta)
dest = carpeta / "obras"
dest.mkdir(exist_ok=True)
for n, url in pj["obras_descarga"].items():
    f = dest / f"{n}.jpg"
    if not f.exists():
        for intento in range(6):   # Wikimedia devuelve 429 si se piden muchas seguidas: esperar y reintentar
            try:
                data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or intento == 5:
                    raise
                time.sleep(15 * (intento + 1))
        tmp = dest / f"{n}.descarga"
        tmp.write_bytes(data)
        Image.open(tmp).convert("RGB").save(f, quality=92)   # verifica que es una imagen real
        tmp.unlink()
        time.sleep(1)
    print(f.name, f.stat().st_size // 1024, "KB", flush=True)
(dest / "CREDITOS.json").write_text(json.dumps({"autor": pj["artista"], "fuente": "Wikimedia Commons",
                                                "licencia": "dominio publico segun la ficha de cada archivo",
                                                "urls": pj["obras_descarga"]}, indent=2, ensure_ascii=False), encoding="utf-8")
