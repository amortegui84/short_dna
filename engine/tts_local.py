"""Local voice clone (no ElevenLabs credit): Qwen3-TTS 12Hz Base clones a voice from a short reference clip and its words.
Runs on the central ComfyUI Python, which has torch; the Qwen3-TTS package lives in the Haru folder (installed there
2026-11-19, model in ComfyUI\\models\\qwen3_tts). tts.py calls it when proyecto.json has "motor_voz": "qwen3".
The reference of a voice is brands/<brand>/voces/<elevenlabs voice id>.wav + .txt (the exact words said in the wav), cut
from lines that ElevenLabs made for that voice, so the local clone stands in for it.
Test 2026-11-19: speaker similarity to the ElevenLabs narrator 0.987-0.990 (two real ElevenLabs lines: 0.987-0.993; other
people 0.92-0.95), Whisper match 0.86-1.00, ~2x real time on the RTX 5090 laptop.
Tags like [whispers] or [pause] are ElevenLabs v3 only: they are removed here (the Base model would read them aloud).
Waits while ComfyUI is generating (one GPU job at a time).
Usage (embedded python): python -I tts_local.py <ref.wav> <ref.txt> <out.mp3|wav> <text>"""
import json, re, subprocess, sys, time, urllib.request

PKGS = r"D:\ComfyUI_windows_portable_nvidia\haru\pkgs_tts"
MODELO = r"D:\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\ComfyUI\models\qwen3_tts\Qwen3-TTS-12Hz-0.6B-Base"


def comfy_ocupado():
    try:
        q = json.load(urllib.request.urlopen("http://127.0.0.1:8188/queue", timeout=5))
        return bool(q.get("queue_running"))
    except Exception:
        return False


def main():
    ref, ref_txt, salida, texto = sys.argv[1:5]
    texto = re.sub(r"\s*\[[^\]]+\]\s*", " ", texto).strip()
    # ALL-CAPS words are v3 emphasis ("in EGYPT"); Qwen3 spells them out ("Ichi Buiti", R22 2026-11-19): lower case them,
    # keeping short acronyms (FBI, UFO, CERN) as they are
    siglas = {"CERN", "AARO", "NASA", "UFOS", "UAPS", "NATO", "UNESCO", "DARPA", "NORAD", "USSR", "KGB", "LIDAR"}
    texto = re.sub(r"\b[A-Z]{4,}\b", lambda w: w.group(0) if w.group(0) in siglas else w.group(0).capitalize(), texto)
    while comfy_ocupado():
        print("ComfyUI is generating: waiting for the GPU", flush=True)
        time.sleep(30)
    sys.path.insert(0, PKGS)
    import numpy as np, soundfile as sf, torch
    from qwen_tts import Qwen3TTSModel
    m = Qwen3TTSModel.from_pretrained(MODELO, device_map="cuda:0", dtype=torch.bfloat16)
    prompt = m.create_voice_clone_prompt(ref_audio=ref, ref_text=open(ref_txt, encoding="utf-8").read().strip(),
                                         x_vector_only_mode=False)
    wavs, sr = m.generate_voice_clone(text=texto, language="English", voice_clone_prompt=prompt)
    wav = np.concatenate([np.asarray(wavs[0], np.float32), np.zeros(int(0.25 * sr), np.float32)])   # room for the end fade
    tmp = salida + ".wav"
    sf.write(tmp, wav, sr)
    if salida.endswith(".wav"):
        import os; os.replace(tmp, salida)
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "192k", salida], check=True)
        import os; os.remove(tmp)


if __name__ == "__main__":
    main()
