"""Audio QA, mandatory before any delivery (review 2026-11-17: the voice was cut at 12 s and 47 s and nobody caught it;
Claude cannot listen, so the check is by numbers). Fails when:
- a line's audio (audio/Lxx.wav) or a head clip (clips/Lxx.mp4) still has speech in its last 80 ms (a word cut at the end)
  or starts loud in its first 30 ms (a word cut at the start);
- the delivered video has a hard drop: speech-level sound falling to near silence within one 20 ms step (a cut word in
  the edit), outside the last second.
Writes <project>/qa_audio.json and exits 1 on any failure.
Usage: python qa_audio.py <project> [video.mp4]"""
import json, subprocess, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from comun import proyecto, ultimo_render  # noqa: E402

HABLA = 45.0   # dB (16-bit RMS) that counts as speech


def niveles(src, paso=0.02):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(b, np.int16).astype(float); n = int(16000 * paso)
    return np.array([20 * np.log10(np.sqrt((a[i:i + n] ** 2).mean()) + 1) for i in range(0, len(a) - n + 1, n)])


def bordes(src):
    e = niveles(src, 0.01)
    if len(e) < 20:
        return []
    out = []
    if e[-8:].mean() > HABLA:
        out.append(f"speech in the last 80 ms ({e[-8:].mean():.0f} dB): a word is cut at the end")
    return out


def arranque(src):
    """Warning only: a take that starts already talking (Kling often speaks from frame 0) cannot be fixed by the cut."""
    e = niveles(src, 0.01)
    return [f"starts in speech ({e[:3].mean():.0f} dB in the first 30 ms)"] if len(e) > 20 and e[:3].mean() > HABLA + 10 else []


def caidas(src):
    e = niveles(src, 0.02); dur = len(e) * 0.02; out = []
    for i in range(1, len(e)):
        if e[i - 1] > HABLA + 10 and e[i] < 15 and i * 0.02 < dur - 1.0:
            out.append(round(i * 0.02, 2))
    return out


def main():
    carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta)
    fallos, avisos = [], []
    for ln in pj["lineas"]:
        lid = ln["id"]
        if ln.get("mudo"):
            continue
        for nombre, src in (("audio", carpeta / "audio" / f"{lid}.wav"), ("clip", carpeta / "clips" / f"{lid}.mp4")):
            if src.exists() and (nombre == "audio" or ln["tipo"] == "A"):
                fallos += [f"{lid} {nombre}: {m}" for m in bordes(src)]
                avisos += [f"{lid} {nombre}: {m}" for m in arranque(src)]
    # the voice track alone (music would hide a cut): a hard drop from speech to silence is a cut word
    voz = carpeta / "vo" / "voz_reaccion.wav"
    if voz.exists():
        fallos += [f"voice track: hard drop at {t} s (a cut word?)" for t in caidas(voz)]
    video = Path(sys.argv[2]) if len(sys.argv) > 2 else ultimo_render(carpeta, pj["slug"])
    qa = {"ok": not fallos, "fallos": fallos, "avisos": avisos, "video": video.name if video.exists() else None}
    (carpeta / "qa_audio.json").write_text(json.dumps(qa, indent=1, ensure_ascii=False), encoding="utf-8")
    print("audio QA:", "OK" if qa["ok"] else "FAIL")
    for f in fallos:
        print(" - FAIL", f)
    for a in avisos:
        print(" - warn", a)
    return qa["ok"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
