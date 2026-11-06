"""Publish copy of a finished episode: <slug>_pub.mp4 next to the final cut (<slug>_AE.mp4, else <slug>.mp4).
H.264 high, CRF 21, at most 6 Mbps, AAC 160k 48 kHz, faststart: ~50 MB for 80 s, small enough for the platforms' URL
fetchers (the 150 MB master is not). Skips when the copy is newer than the cut. See docs/PUBLISHING.md.
Usage: python engine/publicar.py <project folder> [--force]"""
import subprocess, sys
from pathlib import Path

carpeta = Path(sys.argv[1]).resolve()
slug = carpeta.name
cut = next((carpeta / f for f in (f"{slug}_AE.mp4", f"{slug}.mp4") if (carpeta / f).exists()), None)
if not cut:
    sys.exit(f"no finished cut in {carpeta}")
out = carpeta / f"{slug}_pub.mp4"
if out.exists() and out.stat().st_mtime > cut.stat().st_mtime and "--force" not in sys.argv:
    print(f"up to date: {out} ({out.stat().st_size / 1048576:.1f} MB)")
    sys.exit(0)
print(f"encoding {cut.name} -> {out.name}", flush=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(cut), "-c:v", "libx264", "-preset", "slow", "-crf", "21",
                "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p", "-profile:v", "high",
                "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", str(out)], check=True)
print(f"ok: {out} ({out.stat().st_size / 1048576:.1f} MB)")
