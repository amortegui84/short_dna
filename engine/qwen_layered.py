#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""qwen_layered.py - imagenes con alfa real con Qwen-Image-Layered (VAE de 4 canales) en el ComfyUI local, puerto 8188.
Grafo copiado de la plantilla oficial image_qwen_image_layered.json. Sale una imagen RGBA por capa: <out>_0.png, <out>_1.png...
  python qwen_layered.py -p "texto" -o salida [--img entrada.png] [--layers 2] [--size 768] [--steps 20] [--cfg 2.5] [--seed 7]
Con --img descompone esa imagen; sin ella genera las capas desde el texto."""
import argparse, json, os, shutil, sys, time, urllib.request, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import CFG  # noqa: E402
SERVER = CFG["comfy_h3"]["url"]
COMFY = CFG["comfy_h3"]["comfy_dir"]


def post(path, payload):
    req = urllib.request.Request(SERVER + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode())


def grafo(a, prefijo):
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_layered_fp8mixed.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_layered_vae.safetensors"}},
        "4": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 1.0}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": a.prompt}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": ""}},
        "7": {"class_type": "EmptyQwenImageLayeredLatentImage", "inputs": {"width": a.size, "height": a.size, "layers": a.layers, "batch_size": 1}},
        "9": {"class_type": "LatentCut", "inputs": {"samples": ["8", 0], "dim": "t", "index": 1, "amount": 16384}},
        "10": {"class_type": "LatentCutToBatch", "inputs": {"samples": ["9", 0], "dim": "t", "slice_size": 1}},
        "11": {"class_type": "VAEDecode", "inputs": {"samples": ["10", 0], "vae": ["3", 0]}},
        "12": {"class_type": "SaveImage", "inputs": {"images": ["11", 0], "filename_prefix": prefijo}},
    }
    pos, neg, ancho = ["5", 0], ["6", 0], ["7", 0]
    if a.img:
        nombre = "qwl_" + os.path.basename(a.img)
        shutil.copy(a.img, os.path.join(COMFY, "input", nombre))
        g["20"] = {"class_type": "LoadImage", "inputs": {"image": nombre}}
        g["21"] = {"class_type": "ImageScaleToMaxDimension", "inputs": {"image": ["20", 0], "upscale_method": "lanczos", "largest_size": a.size}}
        g["22"] = {"class_type": "VAEEncode", "inputs": {"pixels": ["21", 0], "vae": ["3", 0]}}
        g["23"] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": pos, "latent": ["22", 0]}}
        g["24"] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": neg, "latent": ["22", 0]}}
        g["25"] = {"class_type": "GetImageSize", "inputs": {"image": ["21", 0]}}
        g["7"]["inputs"].update(width=["25", 0], height=["25", 1])
        pos, neg = ["23", 0], ["24", 0]
    g["8"] = {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": pos, "negative": neg, "latent_image": ancho, "seed": a.seed, "steps": a.steps,
                                                   "cfg": a.cfg, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}}
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--prompt", default=""); ap.add_argument("-o", "--out", required=True); ap.add_argument("--img")
    ap.add_argument("--layers", type=int, default=2); ap.add_argument("--size", type=int, default=768); ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--cfg", type=float, default=2.5); ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    t0, pref = time.time(), "qwl/" + os.path.basename(a.out)
    pid = post("/prompt", {"prompt": grafo(a, pref), "client_id": str(uuid.uuid4())})["prompt_id"]
    while True:
        time.sleep(3)
        h = json.loads(urllib.request.urlopen(SERVER + "/history/" + pid, timeout=60).read().decode())
        if h:
            break
    v = list(h.values())[0]
    if v["status"]["status_str"] != "success":
        sys.exit("ERROR: " + str([m[1].get("exception_message", "") for m in v["status"]["messages"] if "error" in str(m[0])])[:600])
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    for i, im in enumerate(v["outputs"]["12"]["images"]):
        shutil.copy(os.path.join(COMFY, "output", im.get("subfolder", ""), im["filename"]), f"{a.out}_{i}.png")
    print(f"listo {len(v['outputs']['12']['images'])} capas en {time.time() - t0:.0f} s -> {a.out}_*.png", flush=True)


if __name__ == "__main__":
    main()
