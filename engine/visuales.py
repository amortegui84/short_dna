"""The visuals of a story that are not downloadable artworks (stage "visuales", after "obras"):
- "documentos": public-domain PDFs (e.g. a declassified report) -> chosen pages rendered to obras/<stem>.jpg (PyMuPDF, 2x);
- "visuales": generated reconstructions {stem: prompt} -> obras/<stem>.jpg with Z-Image at 1088x1920 (local, free), in the
  brand's style line (brand.json "estetica"); they are labelled "reconstruction" in titulos by the script stage.
Writes obras/CREDITOS.json entries for each. Skips files that exist. Usage: python visuales.py <project>"""
import json, subprocess, sys, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import marca_dir, proyecto  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta)
O = carpeta / "obras"; O.mkdir(exist_ok=True)
cred = json.loads((O / "CREDITOS.json").read_text(encoding="utf-8")) if (O / "CREDITOS.json").exists() else {}
brand = json.loads((marca_dir(pj.get("marca")) / "brand.json").read_text(encoding="utf-8")) if pj.get("marca") else {}
for doc in pj.get("documentos", []):
    pdf = O / ("_" + Path(doc["url"]).name)
    if not pdf.exists():
        pdf.write_bytes(urllib.request.urlopen(urllib.request.Request(doc["url"], headers={"User-Agent": "shorts-factory research"}), timeout=120).read())
    import fitz
    d = fitz.open(pdf)
    for stem, n in doc["paginas"].items():
        out = O / f"{stem}.jpg"
        if not out.exists():
            d[n - 1].get_pixmap(matrix=fitz.Matrix(2.2, 2.2)).save(str(out))
        cred[stem] = {"fuente": doc["url"], "pagina": n, "licencia": doc.get("licencia", "")}
        print("documento", out.name, flush=True)
for stem, prompt in pj.get("visuales", {}).items():
    out = O / f"{stem}.jpg"
    if out.exists():
        continue
    png = O / f"_{stem}.png"
    full = f"{prompt}. {brand.get('estetica', '')} Cinematic, grainy, no text, no logos, vertical."
    subprocess.run([sys.executable, str(Path(__file__).parent / "zimage_gen.py"), "-p", full, "-o", str(png), "--size", "1088x1920", "--seed", "7"], check=True)
    from PIL import Image
    Image.open(png).convert("RGB").save(out, quality=92); png.unlink()
    cred[stem] = {"fuente": "generated reconstruction (Z-Image, local)", "prompt": prompt, "licencia": "own work; label as AI reconstruction"}
    print("visual", out.name, flush=True)
(O / "CREDITOS.json").write_text(json.dumps(cred, indent=1, ensure_ascii=False), encoding="utf-8")
