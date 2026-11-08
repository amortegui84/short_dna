"""Make the voice-over lines sound like the host's lines (one voice, not two).

The host lines come out of speech-to-speech (the H3 clip's own voice converted to the series voice); the B lines come straight
from text-to-speech. Both are the same ElevenLabs voice, but STS carries more top end and a different "mic", so the cut jumps
between two timbres (CCC Dürer: STS lines ~4 dB brighter above 3 kHz, speaker similarity 0.89 between the groups vs 0.95+
inside each). This step, run after montaje.py, measures the long-term average spectrum of both groups in 1/3-octave bands,
EQs every voice-over line toward the host's spectrum (smoothed, clamped to +-8 dB), and levels every line to the same
loudness. The originals are kept as audio/<id>_sinigualar.wav. Local, no cost.
Usage: python igualar_voz.py <project> [--lufs -20] [--solo-medir]"""
import json, shutil, subprocess, sys
from pathlib import Path

import numpy as np
import soundfile as sf

carpeta = Path(sys.argv[1]).resolve()
LUFS = float(sys.argv[sys.argv.index("--lufs") + 1]) if "--lufs" in sys.argv else -20.0
SOLO = "--solo-medir" in sys.argv
pj = json.loads((carpeta / "proyecto.json").read_text(encoding="utf-8"))
AUD = carpeta / "audio"
host = [l["id"] for l in pj["lineas"] if l["tipo"] == "A"]
vo = [l["id"] for l in pj["lineas"] if l["tipo"] != "A"]


def leer(lid):
    orig = AUD / f"{lid}_sinigualar.wav"
    y, sr = sf.read(str(orig if orig.exists() else AUD / f"{lid}.wav"), always_2d=True)
    return y.mean(1), sr


def ltas(y, sr):
    """Long-term average spectrum of the voiced part (frames above -45 dBFS), in dB per 1/3-octave band."""
    n = 2048
    fr = np.fft.rfftfreq(n, 1 / sr)
    win = np.hanning(n)
    P = []
    for i in range(0, len(y) - n, n // 2):
        seg = y[i:i + n]
        if 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9) < -45:
            continue
        P.append(np.abs(np.fft.rfft(seg * win)) ** 2)
    P = np.mean(P, 0)
    cent = 100 * 2 ** (np.arange(0, 24) / 3)          # 100 Hz .. ~16 kHz
    out = []
    for c in cent:
        m = (fr >= c / 2 ** (1 / 6)) & (fr < c * 2 ** (1 / 6))
        out.append(10 * np.log10(P[m].mean() + 1e-12) if m.any() else np.nan)
    return cent, np.array(out)


def lufs(path):
    e = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float([l for l in e.splitlines() if l.strip().startswith("I:")][-1].split()[1])


def media(ids):
    curvas = []
    for lid in ids:
        y, sr = leer(lid)
        cent, d = ltas(y, sr)
        curvas.append(d - np.nanmean(d))               # shape only, not level
    return cent, np.nanmean(curvas, 0)


cent, H = media(host)
_, V = media(vo)
g = H - V
g = np.convolve(np.nan_to_num(g), [0.25, 0.5, 0.25], mode="same")   # smooth across neighbouring bands
g = np.clip(g, -8, 8)
g[cent < 120] = 0                                    # leave rumble alone
print("EQ for the voice-over lines (dB):", " ".join(f"{int(c)}:{x:+.1f}" for c, x in zip(cent, g) if c < 12000))
if SOLO:
    sys.exit(0)
# firequalizer takes a gain_entry list: entry(freq, gain)
entries = ";".join(f"entry({c:.0f},{x:.2f})" for c, x in zip(cent, g))
for lid in host + vo:
    dst = AUD / f"{lid}.wav"
    keep = AUD / f"{lid}_sinigualar.wav"
    if not keep.exists():
        shutil.copy2(dst, keep)
    tmp = AUD / f"_{lid}_eq.wav"
    af = (f"firequalizer=gain_entry='{entries}':gain='cubic_interpolate(f)'," if lid in vo else "")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(keep), "-af", af + "anull", "-ar", "48000", str(tmp)], check=True)
    gain = LUFS - lufs(tmp)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af", f"volume={gain:.2f}dB,alimiter=limit=0.95:level=disabled", "-ar", "48000", str(dst)], check=True)
    tmp.unlink()
    print(f"{lid} {'VO  ' if lid in vo else 'HOST'} -> {lufs(dst):.1f} LUFS")
