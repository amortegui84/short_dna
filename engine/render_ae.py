"""Renders one video with aerender from a copy of its After Effects project (the original stays editable) and encodes the
delivery: H.264 CRF 19 + AAC 192k, loudnorm -20 LUFS / -1.5 dBTP. Then QA: black frames (blackdetect d=0.04), loudness, and
Motion DNA tools/motion_qa.py (one-frame pops, frozen holds; subtitle changes at y~0.73 are expected).
Usage: python render_ae.py <project>"""
import json, re, shutil, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import CFG, MOTION_DNA, PY_TOOLS, proyecto  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta)
datos = json.loads((carpeta / "datos_ae.json").read_text(encoding="utf-8"))
aep = carpeta / "ae" / f"{pj['slug']}.aep"; copia = carpeta / "ae" / "_render.aep"
shutil.copy2(aep, copia)
crudo, envio = carpeta / f"{pj['slug']}_AE.mp4", carpeta / f"{pj['slug']}.mp4"
crudo.unlink(missing_ok=True); t0 = time.time()
with open(carpeta / "_aerender.log", "w", encoding="utf-8") as log:
    subprocess.run([CFG["aerender"], "-project", str(copia), "-comp", datos["comp"], "-OMtemplate", CFG.get("ae_render_template", "H.264 - Match Render Settings - 15 Mbps"),
                    "-output", str(crudo), "-sound", "ON"], stdout=log, stderr=subprocess.STDOUT)
if not crudo.exists():
    sys.exit(f"aerender did not write {crudo} (see _aerender.log)")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(crudo), "-c:v", "libx264", "-crf", "19", "-preset", "medium",
                "-af", "loudnorm=I=-20:TP=-1.5:LRA=7", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(envio)], check=True)
err = subprocess.run(["ffmpeg", "-i", str(envio), "-vf", "blackdetect=d=0.04", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
qa = {"video": envio.name, "min": round((time.time() - t0) / 60, 1), "negros": err.count("black_start"),
      "lufs": float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])}
mq = subprocess.run([PY_TOOLS, str(MOTION_DNA / "tools" / "motion_qa.py"), str(envio)], capture_output=True, text=True).stdout
qa["saltos"] = [l.strip() for l in mq.splitlines() if "JUMP" in l and "y 0.7" not in l]
qa["ok"] = qa["negros"] == 0 and -21.5 <= qa["lufs"] <= -18.5
(carpeta / "qa_render.json").write_text(json.dumps(qa, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(qa, ensure_ascii=False, indent=1))
