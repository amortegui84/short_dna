"""A light collect of one video, so someone else (or Claude) can open, edit and render it anywhere:
- its After Effects project reduced to its comp (reduceProject) and every footage file copied inside the folder under
  media/<original path without the drive>, never flattened (there are many L03.mov), relinked (ae/collect.jsx);
- the presenter mattes re-encoded as ProRes 4444 qscale 11 (~6x lighter, alpha SSIM 0.99997); the originals stay;
- the render, the video's data, a HANDOFF.md and a CLAUDE.md; plus a stored (uncompressed) zip.
Usage: python collect.py <project>   -> <work_dir>/collects/<slug>/ and <slug>.zip"""
import json, shutil, subprocess, sys, zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import CFG, MOTION_DNA, REPO, proyecto  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta)
datos = json.loads((carpeta / "datos_ae.json").read_text(encoding="utf-8"))
aep = (carpeta / "ae" / f"{pj['slug']}.aep").as_posix()
dest = Path(CFG["work_dir"]) / "collects" / pj["slug"]
if dest.exists():
    shutil.rmtree(dest)
# light mattes at the path the collect expects: collect.jsx does not copy what already exists and relinks to it
md = dest / "media" / carpeta.relative_to(carpeta.anchor) / "mates"; md.mkdir(parents=True)
for m in sorted((carpeta / "mates").glob("L*.mov")):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(m), "-c:v", "prores_ks", "-profile:v", "4", "-qscale:v", "11",
                    "-pix_fmt", "yuva444p10le", "-alpha_bits", "8", "-vendor", "apl0", "-an", str(md / m.name)], check=True)
sys.path.insert(0, str(MOTION_DNA / "tools" / "mcp"))
import ss_motion_mcp as M  # noqa: E402
r = M.run_jsx(f"""app.beginSuppressDialogs();
try {{
  if (app.project) app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
  app.open(new File("{aep}"));
  var c = null; for (var i = 1; i <= app.project.numItems; i++) {{ var it = app.project.item(i); if (it instanceof CompItem && it.name === {json.dumps(datos["comp"])}) c = it; }}
  if (!c) throw new Error("comp not found");
  app.project.reduceProject([c]);
  $.evalFile(new File("{(REPO / 'ae' / 'collect.jsx').as_posix()}"));
  var r = COLLECT_FILES("{dest.as_posix()}", "{pj['slug']}");
  app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES); app.open(new File("{aep}"));
  return r;
}} finally {{ app.endSuppressDialogs(false); }}""", timeout=1800, includes=())
print(r)
shutil.copy2(carpeta / f"{pj['slug']}.mp4", dest / f"{pj['slug']}.mp4")
(dest / "datos").mkdir()
for f in ("proyecto.json", "timeline.json", "datos_ae.json", "cajas_cabeza.json"):
    if (carpeta / f).exists():
        shutil.copy2(carpeta / f, dest / "datos" / f)
(dest / "HANDOFF.md").write_text(f"""# Handoff: {pj.get('artista', pj['slug'])} ({pj['slug']})

- `ae/{pj['slug']}.aep`: only the comp `{datos['comp']}` and what it uses; every footage file is inside this folder (`media/...`,
  same path as on the machine that made it, without the drive letter). The presenter mattes are light ProRes 4444 copies.
- `{pj['slug']}.mp4`: the delivered render. `datos/`: the project, timeline and build data.
- Rebuilding needs the shorts-factory repo (engine/build_collage.py + ae/collage.jsx); editing or rendering needs only the aep.
- Style and rules: docs/STYLE_COLLAGE.md in the repo.
""", encoding="utf-8")
(dest / "CLAUDE.md").write_text(f"# CLAUDE.md\nRead HANDOFF.md. One comp, `{datos['comp']}`; all footage under media/. Never alter the artworks.\n", encoding="utf-8")
z = dest.with_suffix(".zip"); z.unlink(missing_ok=True)
with zipfile.ZipFile(z, "w", zipfile.ZIP_STORED) as zf:
    for f in sorted(dest.rglob("*")):
        if f.is_file():
            zf.write(f, f"{pj['slug']}/" + f.relative_to(dest).as_posix())
print("collect:", dest, round(sum(f.stat().st_size for f in dest.rglob('*') if f.is_file()) / 1e6), "MB |", z)
