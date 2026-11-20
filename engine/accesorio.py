"""Thematic accessory on a host's approved still (CCC: "the accessory is added to the head in its start frame, a local edit
of the approved still, USD 0"). Qwen-Image-Edit-2509 (Apache 2.0) + Lightning 4-step LoRA on the central ComfyUI (port 8188).
The result is the head reference (@Element1) for kling.py: save it in the project and point proyecto.json "maestro_episodio" at it.
Usage: python accesorio.py <still.png> "<edit prompt>" <out.png> [--seeds 1,2,3]"""
import json, sys, time, uuid, urllib.request, urllib.error
from pathlib import Path

URL = "http://127.0.0.1:8188"
src, prompt, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
seeds = [int(s) for s in sys.argv[sys.argv.index("--seeds") + 1].split(",")] if "--seeds" in sys.argv else [1]


def post(path, data, ctype="application/json"):
    try:
        return json.load(urllib.request.urlopen(urllib.request.Request(URL + path, data=data, headers={"Content-Type": ctype}), timeout=60))
    except urllib.error.HTTPError as e:
        sys.exit(f"ComfyUI {e.code} on {path}: {e.read().decode(errors='replace')[:800]}")


def upload(p):
    b = uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{p.name}\"\r\nContent-Type: image/png\r\n\r\n").encode() \
        + p.read_bytes() + f"\r\n--{b}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{b}--\r\n".encode()
    return post("/upload/image", body, f"multipart/form-data; boundary={b}")["name"]


name = upload(src)
for seed in seeds:
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_edit_2509_fp8_e4m3fn.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors", "strength_model": 1.0}},
        "3": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["2", 0], "shift": 3.0}},
        "4": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image"}},
        "5": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "6": {"class_type": "LoadImage", "inputs": {"image": name}},
        "7": {"class_type": "ImageScaleToTotalPixels", "inputs": {"image": ["6", 0], "upscale_method": "lanczos", "megapixels": 1.5, "resolution_steps": 8}},
        "8": {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {"clip": ["4", 0], "prompt": prompt, "vae": ["5", 0], "image1": ["7", 0]}},
        "9": {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {"clip": ["4", 0], "prompt": "", "vae": ["5", 0], "image1": ["7", 0]}},
        "10": {"class_type": "VAEEncode", "inputs": {"pixels": ["7", 0], "vae": ["5", 0]}},
        "11": {"class_type": "KSampler", "inputs": {"model": ["3", 0], "positive": ["8", 0], "negative": ["9", 0], "latent_image": ["10", 0],
                                                    "seed": seed, "steps": 4, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["5", 0]}},
        "13": {"class_type": "SaveImage", "inputs": {"images": ["12", 0], "filename_prefix": "ccc_accesorio"}},
    }
    pid = post("/prompt", json.dumps({"prompt": g}).encode())["prompt_id"]
    while True:
        time.sleep(3)
        h = json.load(urllib.request.urlopen(f"{URL}/history/{pid}", timeout=60))
        if pid in h:
            break
    st = h[pid].get("status", {})
    if st.get("status_str") == "error":
        sys.exit(f"ComfyUI error: {json.dumps(st)[:600]}")
    img = h[pid]["outputs"]["13"]["images"][0]
    data = urllib.request.urlopen(f"{URL}/view?filename={img['filename']}&subfolder={img['subfolder']}&type=output", timeout=60).read()
    dst = out if len(seeds) == 1 else out.with_name(f"{out.stem}_s{seed}{out.suffix}")
    dst.write_bytes(data)
    print(dst, flush=True)
