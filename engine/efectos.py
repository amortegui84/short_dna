"""Effect clips for a brand's kit with MiniMax H3 text-to-video (local): smoke, sparks, flames, ash, dripping wax, static bursts...
on pure black, so After Effects lays them over anything with Screen/Add. H3 also generates the matching sound (crackle, hiss,
sizzle), kept in the clip as the effect's own sound. Writes brands/<brand>/kit/fx/<name>.mp4. Skips existing files.
Specs live in brands/<brand>/kit/kit_spec.json "fx": [{"name", "prompt", "seconds"}].
Usage: python efectos.py <brand> [name ...]"""
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import H3, PY_PORTABLE, marca_dir  # noqa: E402

marca = sys.argv[1]; solo = set(sys.argv[2:])
K = marca_dir(marca, True) / "kit"; F = K / "fx"; F.mkdir(exist_ok=True)
spec = json.loads((K / "kit_spec.json").read_text(encoding="utf-8"))
BASE = ("summary:\n[text-to-video generation + audio generation]\nA vertical visual-effect plate for compositing.\n\ndetailed_description:\n"
        "{p} The background is pure solid black, completely empty, no people, no objects, no text, static camera, centered, high contrast, "
        "realistic, 9:16.\n\noverall_soundscape:\n{s}\n\nnon_diegetic_music:\nN/A\n")
for it in spec.get("fx", []):
    out = F / f"{it['name']}.mp4"
    if out.exists() or (solo and it["name"] not in solo):
        continue
    pf = F / f"_{it['name']}.txt"
    pf.write_text(BASE.format(p=it["prompt"], s=it.get("sonido", "Only the natural sound of the effect, close and detailed.")), encoding="utf-8")
    subprocess.run([PY_PORTABLE, H3, "-p", str(pf), "--seconds", str(it.get("seconds", 5.17)), "--size", "768x1344", "--gen-audio",
                    "--seeds", "11", "-o", str(out)], check=True)
    print("fx", out.name, flush=True)
print("fx:", len(list(F.glob("*.mp4"))), "clips in", F)
