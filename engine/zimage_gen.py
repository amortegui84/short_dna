#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
zimage_gen.py - imagenes con Z-Image Turbo en el ComfyUI local (API HTTP), con LoRA opcionales.

Sirve para fabricar fotogramas clave de una serie (misma ropa, misma luz, mismo estilo) que luego se animan con H3.
Los LoRA de personajes se pasan con --lora ARCHIVO:fuerza (la etiqueta del LoRA va al principio del prompt).

  python zimage_gen.py -p "..." -o salida.png [--size 1344x768] [--seed 7] [--lora ARCHIVO:fuerza ...]
  python zimage_gen.py --spec items.json          # lote: {"items":[{"name","prompt","size","seed","lora"}], "out_dir": "..."}

Ajustes (los del ejemplo de la plantilla de Z-Image Turbo): 9 pasos, cfg 1, euler / ddim_uniform, ModelSamplingAuraFlow shift 3,
codificador qwen_3_4b (tipo lumina2), VAE ae. El negativo es ConditioningZeroOut. No hay que correr QwenStudio a la vez.
"""
import argparse, json, os, shutil, sys, time, urllib.request, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import CFG  # noqa: E402
SERVER = CFG["comfy_h3"]["url"]
COMFY_OUT = CFG["comfy_h3"]["comfy_dir"] + "/output"
COUPLE_LORA = None


def post(path, payload):
    req = urllib.request.Request(SERVER + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=60).read().decode()


def get(path):
    return json.loads(urllib.request.urlopen(SERVER + path, timeout=60).read().decode())


def graph(prompt, w, h, seed, loras, steps=9, prefix="zimg/z"):
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "lumina2", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
    }
    model = ["1", 0]
    for i, (name, strength) in enumerate(loras):
        g["2%d" % i if False else "1%d" % i] = {"class_type": "LoraLoaderModelOnly",
                                                 "inputs": {"model": model, "lora_name": name, "strength_model": strength}}
        model = ["1%d" % i, 0]
    g["4"] = {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": model, "shift": 3.0}}
    g["5"] = {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}}
    g["6"] = {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["5", 0]}}
    g["7"] = {"class_type": "EmptySD3LatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}}
    g["8"] = {"class_type": "KSampler", "inputs": {"model": ["4", 0], "seed": seed, "steps": steps, "cfg": 1.0,
                                                     "sampler_name": "euler", "scheduler": "ddim_uniform",
                                                     "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["7", 0], "denoise": 1.0}}
    g["9"] = {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}}
    g["90"] = {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": prefix}}
    return g


def run(prompt, size, seed, loras, out, steps=9):
    w, h = (int(x) for x in size.lower().split("x"))
    g = graph(prompt, w, h, seed, loras, steps, prefix="zimg/" + os.path.splitext(os.path.basename(out))[0])
    r = json.loads(post("/prompt", {"prompt": g, "client_id": str(uuid.uuid4())}))
    pid = r["prompt_id"]
    t0 = time.time()
    while True:
        time.sleep(4)
        try:
            hist = get("/history/" + pid)
        except Exception:
            continue
        if hist:
            v = list(hist.values())[0]
            st = v.get("status", {})
            if st.get("status_str") != "success":
                for m in st.get("messages", []):
                    if "error" in str(m[0]):
                        print("  ERROR:", str(m[1].get("exception_message", ""))[:400])
                return False
            im = v["outputs"]["90"]["images"][0]
            src = os.path.join(COMFY_OUT, im.get("subfolder", ""), im["filename"])
            os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
            shutil.copy(src, out)
            print("  listo en %.1f min -> %s" % ((time.time() - t0) / 60.0, out), flush=True)
            return True


def parse_lora(x):
    n, _, s = x.rpartition(":")
    try:
        return (n, float(s)) if n else (x, 1.0)
    except ValueError:
        return (x, 1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--prompt"); ap.add_argument("-o", "--out")
    ap.add_argument("--size", default="1344x768"); ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--steps", type=int, default=9)
    ap.add_argument("--lora", nargs="*", default=[], help="ARCHIVO:fuerza (ruta relativa a models/loras)")
    ap.add_argument("--spec")
    a = ap.parse_args()
    try:
        get("/system_stats")
    except Exception:
        sys.exit("ComfyUI no responde en %s" % SERVER)
    if a.spec:
        spec = json.load(open(a.spec, encoding="utf-8-sig"))
        out_dir = spec.get("out_dir", ".")
        base = [parse_lora(x) for x in spec.get("lora", [])]
        for it in spec["items"]:
            out = os.path.join(out_dir, it["name"] + ".png")
            if os.path.exists(out) and not spec.get("overwrite"):
                print("[%s] ya existe" % it["name"]); continue
            print("[%s] generando" % it["name"], flush=True)
            loras = [parse_lora(x) for x in it["lora"]] if "lora" in it else base
            run(it["prompt"], it.get("size", a.size), int(it.get("seed", a.seed)), loras, out, a.steps)
    else:
        run(a.prompt, a.size, a.seed, [parse_lora(x) for x in a.lora], a.out, a.steps)


if __name__ == "__main__":
    main()
