"""One hand-directed Kling 4.0 reference-to-video take (same head element, references and costs log as kling.py), for a
retake of a few lines with a prompt written by hand (e.g. a closing that must be one continuous shot).
Dry by default: prints the prompt and the price; --pagar sends it.
Usage: python kling_toma.py <project> <prompt.txt> <clip name> --dur 8 [--pagar]"""
import json, subprocess, sys, time
from datetime import datetime
from pathlib import Path

carpeta_arg, prompt_p, nombre = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
DUR = int(sys.argv[sys.argv.index("--dur") + 1]) if "--dur" in sys.argv else 8
PAGAR_TOMA = "--pagar" in sys.argv
# kling.py's setup (head element, references, fal helpers) without its generation loop
src = (Path(__file__).parent / "kling.py").read_text(encoding="utf-8")
setup = src[:src.index("total = 0.0")]
sys.argv = [str(Path(__file__).parent / "kling.py"), carpeta_arg] + (["--pagar"] if PAGAR_TOMA else [])
g = {"__file__": str(Path(__file__).parent / "kling.py"), "__name__": "kling_setup"}
exec(compile(setup, "kling.py", "exec"), g)
carpeta, RES = g["carpeta"], g["RES"]
texto = prompt_p.read_text(encoding="utf-8").strip()
usd = DUR * g["USD_S"][RES]
elem = {"frontal_image_url": f"<{g['MAESTRO_P'].name}>", "reference_image_urls": [f"<{r}>" for r in g["refs"]]}
cuerpo = {"prompt": texto, "duration": DUR, "elements": [elem], "resolution": RES, "aspect_ratio": "9:16"}
(carpeta / "prompts" / f"{nombre}.json").write_text(json.dumps(cuerpo, indent=1, ensure_ascii=False), encoding="utf-8")
print(texto); print(f"\n[{nombre}] {DUR} s at {RES}: USD {usd:.2f}")
out = carpeta / "clips" / f"{nombre}.mp4"
if not PAGAR_TOMA:
    sys.exit("dry run: nothing sent (add --pagar after the OK)")
if out.exists():
    sys.exit(f"{out.name} already exists")
key = g["clave_fal"]()
elem["frontal_image_url"] = g["uri_imagen"](g["MAESTRO_P"])
elem["reference_image_urls"] = [g["uri_imagen"](g["REF_DIR"] / r) for r in g["refs"]]
t0 = time.time()
res = g["esperar"](g["fal"]("POST", f"https://queue.fal.run/{g['MODEL']}", cuerpo, key), key, nombre)
out.write_bytes(__import__("urllib.request").request.urlopen(res["video"]["url"], timeout=300).read())
vd = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)], capture_output=True, text=True).stdout)
log_p = carpeta / "costos.json"; log = json.loads(log_p.read_text(encoding="utf-8")) if log_p.exists() else {"clips": []}
log["clips"].append({"clip": nombre, "pedido_s": DUR, "resolucion": RES, "duracion_s": round(vd, 2), "usd": round(usd, 3),
                     "generacion_s": round(time.time() - t0, 1), "hora": datetime.now().isoformat(timespec="seconds"), "nota": "hand-directed retake"})
log["total_usd"] = round(sum(c["usd"] for c in log["clips"]), 3)
log_p.write_text(json.dumps(log, indent=1), encoding="utf-8")
print(f"[{nombre}] done: {vd:.1f} s, USD {usd:.2f}")
