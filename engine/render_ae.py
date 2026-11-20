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
# versions (user 2026-11-17: "de aqui en adelante pon v1, v2"): <slug>_vN.mp4, the previous version moves to old/
import re as _re
viejo = carpeta / "old"; viejo.mkdir(exist_ok=True)
nums = [int(m.group(1)) for f in list(carpeta.glob(f"{pj['slug']}_v*.mp4")) + list(viejo.glob(f"{pj['slug']}_v*.mp4"))
        if (m := _re.match(rf"{_re.escape(pj['slug'])}_v(\d+)\.mp4$", f.name))]
if (carpeta / f"{pj['slug']}.mp4").exists():   # the unnumbered render from before the rule is v1
    (carpeta / f"{pj['slug']}.mp4").replace(viejo / f"{pj['slug']}_v1.mp4"); nums.append(1)
for f in carpeta.glob(f"{pj['slug']}_v*.mp4"):
    f.replace(viejo / f.name)
VERSION = max(nums, default=0) + 1
crudo, envio = carpeta / f"{pj['slug']}_AE.mp4", carpeta / f"{pj['slug']}_v{VERSION}.mp4"
crudo.unlink(missing_ok=True)


def gpu_libre(max_min=5):
    """Before aerender, give ComfyUI a few minutes to finish and ask it to free memory. The 2026-11-14 ep23 hangs were not
    the VRAM (ep21 rendered fine with ComfyUI busy) but an apostrophe in the -comp name (see build_collage.py), so the wait
    is short: renders no longer queue behind hours of clip generation."""
    import urllib.request
    base = CFG.get("comfy_url", "http://127.0.0.1:8188")
    for _ in range(max_min * 2):
        try:
            q = json.loads(urllib.request.urlopen(base + "/queue", timeout=5).read())
        except Exception:
            return   # ComfyUI not running: nothing holds the GPU
        if not q.get("queue_running") and not q.get("queue_pending"):
            break
        print("waiting for ComfyUI to finish before aerender...", flush=True); time.sleep(30)
    try:
        urllib.request.urlopen(urllib.request.Request(base + "/free", data=b'{"unload_models": true, "free_memory": true}',
                                                      headers={"Content-Type": "application/json"}), timeout=10)
        time.sleep(15)
    except Exception:
        pass


def purgar_cache(limite_gb=30):
    """User 2026-11-17: "vaciar el cache de vez en cuando". Before every render: AE purges its memory caches (app.purge);
    the disk cache folder is measured and, when over `limite_gb`, emptied only if After Effects is closed (else a warning:
    close AE and run this again). The 2026-11-17 hang came with a 100 GB disk cache."""
    try:
        sys.path.insert(0, str(MOTION_DNA / "tools" / "mcp")); import ss_motion_mcp as _M
        _M.run_jsx("app.purge(PurgeTarget.ALL_CACHES); return 'purged';", includes=(), timeout=60)
    except Exception as e:
        print("purge skipped:", str(e)[:80])
    import os, shutil
    base = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "Adobe" / "After Effects"
    for dc in base.glob("*/Disk Cache*"):
        gb = sum(f.stat().st_size for f in dc.rglob("*") if f.is_file()) / 1e9
        if gb < limite_gb:
            continue
        abierto = subprocess.run(["tasklist", "/FI", "IMAGENAME eq AfterFX.exe"], capture_output=True, text=True).stdout.count("AfterFX.exe")
        if abierto:
            print(f"WARNING: AE disk cache {gb:.0f} GB at {dc}: close After Effects and empty it (or run render_ae.py with AE closed)")
        else:
            for f in dc.iterdir():
                shutil.rmtree(f, ignore_errors=True) if f.is_dir() else f.unlink(missing_ok=True)
            print(f"AE disk cache emptied ({gb:.0f} GB)")


purgar_cache(); gpu_libre(); t0 = time.time()
with open(carpeta / "_aerender.log", "w", encoding="utf-8") as log:
    subprocess.run([CFG["aerender"], "-project", str(copia), "-comp", datos["comp"], "-OMtemplate", CFG.get("ae_render_template", "H.264 - Match Render Settings - 15 Mbps"),
                    "-output", str(crudo), "-sound", "ON"], stdout=log, stderr=subprocess.STDOUT)
if not crudo.exists():
    sys.exit(f"aerender did not write {crudo} (see _aerender.log)")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(crudo), "-c:v", "libx264", "-crf", "19", "-preset", "medium",
                "-af", "loudnorm=I=-20:TP=-1.5:LRA=7", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(envio)], check=True)
err = subprocess.run(["ffmpeg", "-i", str(envio), "-vf", "blackdetect=d=0.04", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
qa = {"version": VERSION, "video": envio.name, "min": round((time.time() - t0) / 60, 1), "negros": err.count("black_start"),
      "lufs": float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])}
mq = subprocess.run([PY_TOOLS, str(MOTION_DNA / "tools" / "motion_qa.py"), str(envio)], capture_output=True, text=True).stdout
qa["saltos"] = [l.strip() for l in mq.splitlines() if "JUMP" in l and "y 0.7" not in l]
# audio QA is mandatory (2026-11-17: cut words at 12 s and 47 s went out unnoticed): cut line ends and hard drops
aq = subprocess.run([sys.executable, str(Path(__file__).parent / "qa_audio.py"), str(carpeta), str(envio)], capture_output=True, text=True)
qa["audio"] = [l.strip(" -") for l in aq.stdout.splitlines()[1:] if "FAIL" in l]
qa["ok"] = qa["negros"] == 0 and -21.5 <= qa["lufs"] <= -18.5 and aq.returncode == 0
(carpeta / "qa_render.json").write_text(json.dumps(qa, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(qa, ensure_ascii=False, indent=1))
crudo.replace(viejo / crudo.name)   # the main folder keeps only the latest delivered version
print("version:", envio.name)
