"""GIF-like animated elements for a brand's kit (stickers that move in the video): MiniMax H3 text-to-video of one object on black,
cut to a seamless loop (the last 0.6 s cross-faded into the start) and matted to real alpha (Motion DNA video_matte.py, InSPyReNet):
brands/<brand>/kit/loops/<name>.mov (ProRes 4444 with alpha, 24 fps) + <name>.webp (animated preview) + <name>_src.mp4.
Specs: kit_spec.json "loops": [{"name", "prompt", "seconds"}]. Local and free; one GPU job at a time. Skips existing files.
Usage: python loops.py <brand> [name ...]"""
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import H3, MOTION_DNA, PY_PORTABLE, duracion, marca_dir  # noqa: E402

marca = sys.argv[1]; solo = set(sys.argv[2:])
K = marca_dir(marca, True) / "kit"; L = K / "loops"; L.mkdir(exist_ok=True)
spec = json.loads((K / "kit_spec.json").read_text(encoding="utf-8"))
P = ("summary:\n[text-to-video generation]\nA looping animated sticker element for compositing.\n\ndetailed_description:\n"
     "{p} One single object, centered, filling about half of the frame, on a pure solid black background, completely empty around it, "
     "static locked-off camera, the motion is small and repetitive so it can loop, realistic, dramatic low-key light, 9:16.\n\n"
     "overall_soundscape:\nSilence.\n\nnon_diegetic_music:\nN/A\n")
for it in spec.get("loops", []):
    n = it["name"]; mov = L / f"{n}.mov"
    if mov.exists() or (solo and n not in solo):
        continue
    src = L / f"{n}_src.mp4"
    if not src.exists():
        pf = L / f"_{n}.txt"; pf.write_text(P.format(p=it["prompt"]), encoding="utf-8")
        subprocess.run([PY_PORTABLE, H3, "-p", str(pf), "--seconds", str(it.get("seconds", 4.46)), "--size", "768x1344", "--seeds", "5", "-o", str(src)], check=True)
    # loop sin costura: el final se funde con el principio (xfade de 0.6 s) y se recorta a la duracion - 0.6
    d = duracion(src); x = 0.6; lp = L / f"_{n}_loop.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex",
                    f"[0:v]split[a][b];[a]trim=0:{d - x:.3f},setpts=PTS-STARTPTS[main];[b]trim={d - x:.3f}:{d:.3f},setpts=PTS-STARTPTS[tail];"
                    f"[main]split[m1][m2];[m2]trim=0:{x},setpts=PTS-STARTPTS[head];[tail][head]xfade=transition=fade:duration={x}:offset=0[blend];"
                    f"[m1]trim={x}:{d - x:.3f},setpts=PTS-STARTPTS[mid];[blend][mid]concat=n=2:v=1:a=0,fps=24[out]", "-map", "[out]", "-an", str(lp)], check=True)
    subprocess.run([PY_PORTABLE, str(MOTION_DNA / "tools" / "video_matte.py"), str(lp), str(mov), "--size", "768x1344", "--fps", "24"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mov), "-vf", "fps=12,scale=256:-2", "-loop", "0", "-c:v", "libwebp_anim", "-lossless", "0", "-q:v", "70", str(L / f"{n}.webp")])
    lp.unlink(missing_ok=True); print("loop", n, flush=True)
print("loops:", len(list(L.glob("*.mov"))), "in", L)
