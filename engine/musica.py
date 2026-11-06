"""Music for one video, made locally with ACE-Step 1.5 in ComfyUI (config comfy_h3; any "comfy_ace" ComfyUI with the ACE models).
The style comes from proyecto.json "musica" {"tags", "bpm", "key"} or, if missing, from the style file
(library/styles/<style>.json "musica"). Review rule: cinematic and restrained, never childish (no lute, recorder, celesta,
glockenspiel). Two takes -> <project>/musica/toma_N.mp3; the first is normalised to -27 LUFS as musica/elegida.wav (the
builder puts it under the voice at 0 dB and fades it out). Swap takes with: python musica.py <project> --elegir 2
Other providers (Suno and similar): factory/providers/music_*.py with the same output.
Usage: python musica.py <project> [--dur 80] [--elegir N]"""
import argparse, json, shutil, subprocess, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import CFG, LIB, buscar, proyecto  # noqa: E402

URL = CFG["comfy_h3"]["url"]
DUR = 80.0


def wf(tags, bpm, key, seed, pref):
    return {
        "1": {"class_type": "DualCLIPLoader", "inputs": {"clip_name1": "qwen_0.6b_ace15.safetensors", "clip_name2": "qwen_4b_ace15.safetensors", "type": "ace"}},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": "acestep_v1.5_xl_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ace_1.5_vae.safetensors"}},
        "4": {"class_type": "TextEncodeAceStepAudio1.5", "inputs": {"clip": ["1", 0], "tags": tags, "lyrics": "[Instrumental]", "seed": seed, "bpm": bpm,
              "duration": DUR, "timesignature": "4", "language": "unknown", "keyscale": key, "generate_audio_codes": True, "cfg_scale": 2.0,
              "temperature": 0.85, "top_p": 0.9, "top_k": 0, "min_p": 0.0}},
        "5": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
        "6": {"class_type": "EmptyAceStep1.5LatentAudio", "inputs": {"seconds": DUR, "batch_size": 1}},
        "7": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["2", 0], "shift": 3.0}},
        "8": {"class_type": "KSampler", "inputs": {"model": ["7", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0], "seed": seed,
              "steps": 8, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "9": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveAudioMP3", "inputs": {"audio": ["9", 0], "filename_prefix": pref, "quality": "V0"}},
    }


def pedir(w):
    r = urllib.request.urlopen(urllib.request.Request(URL + "/prompt", data=json.dumps({"prompt": w}).encode(), headers={"Content-Type": "application/json"}))
    pid = json.load(r)["prompt_id"]
    for _ in range(400):
        h = json.load(urllib.request.urlopen(URL + "/history/" + pid))
        if pid in h:
            return h[pid]
        time.sleep(3)
    raise RuntimeError("ACE-Step no termino")


ap = argparse.ArgumentParser(); ap.add_argument("carpeta"); ap.add_argument("--dur", type=float, default=80.0); ap.add_argument("--elegir", type=int)
a = ap.parse_args(); DUR = a.dur
carpeta = Path(a.carpeta).resolve(); pj = proyecto(carpeta)
dest = carpeta / "musica"; dest.mkdir(exist_ok=True)
if not a.elegir:
    m = pj.get("musica") or json.loads(buscar("styles", pj.get("estilo", "collage_v10c"), pj.get("marca")).read_text(encoding="utf-8"))["musica"]   # estilo de la marca primero
    root = Path(CFG["comfy_h3"]["comfy_dir"])
    for k, seed in enumerate((101, 202)):
        h = pedir(wf(m["tags"], m.get("bpm", 88), m.get("key", "D minor"), seed, f"audio/{pj['slug']}_musica_{k + 1}"))
        au = h["outputs"]["10"]["audio"][0]
        shutil.copy2(root / "output" / au.get("subfolder", "") / au["filename"], dest / f"toma_{k + 1}.mp3")
        print("toma", k + 1, h["status"]["status_str"], flush=True)
n = a.elegir or 1
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(dest / f"toma_{n}.mp3"), "-af", "loudnorm=I=-27:TP=-3:LRA=9", "-ar", "48000", "-ac", "2",
                str(dest / "elegida.wav")], check=True)
print("elegida: toma", n)
