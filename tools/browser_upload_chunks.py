"""Split a video into <=9 MB parts so Claude in Chrome can hand it to a site's upload field, and print the page scripts.

Why: Claude in Chrome's file_upload takes at most ~10 MB per call, and a site's own "Select video" button opens a native
file picker that never appears while Chrome is driven remotely. So the file goes in as parts through a hidden input,
is joined back into one File inside the page, and is given to the site's real <input type=file>.
Proven on TikTok Studio (tiktok.com/tiktokstudio/upload), 2026-11-18, 20 scheduled posts.

Usage: python tools/browser_upload_chunks.py <video.mp4> [--out <folder>]
Prints: the part paths (upload each one with its own file_upload call) and the three page scripts to run in order.
"""
import argparse, pathlib, sys

PART = 9_000_000

INJECT = """// 1) add a hidden input that collects the parts
(() => { let i = document.getElementById('kitin');
  if (!i) { i = document.createElement('input'); i.type = 'file'; i.multiple = true; i.id = 'kitin';
    i.setAttribute('aria-label', 'kitin chunk input'); i.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;opacity:0';
    document.body.appendChild(i); }
  window.__parts = window.__parts || {};
  i.onchange = () => { for (const f of i.files) window.__parts[f.name] = f; };
  return 'ready'; })()"""

ASSEMBLE = """// 3) join the parts in name order and give the file to the site's own input
(() => { const names = Object.keys(window.__parts).sort();
  const file = new File(names.map(n => window.__parts[n]), '{name}', {type: 'video/mp4'});
  const target = [...document.querySelectorAll('input[type=file]')].find(x => x.id !== 'kitin' && (x.accept || '').includes('video'));
  if (!target) return 'no video input on this page';
  const dt = new DataTransfer(); dt.items.add(file); target.files = dt.files;
  target.dispatchEvent(new Event('change', {bubbles: true}));
  window.__parts = {}; return names.length + ' parts, ' + file.size + ' bytes'; })()"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", help="folder for the parts (default: <video folder>/_chunks)")
    a = ap.parse_args()
    src = pathlib.Path(a.video).resolve()
    if not src.exists():
        sys.exit(f"missing: {src}")
    out = pathlib.Path(a.out) if a.out else src.parent / "_chunks"
    out.mkdir(parents=True, exist_ok=True)
    data = src.read_bytes()
    parts = []
    for k in range(0, len(data), PART):
        p = out / f"{src.stem}_part{k // PART:02d}"
        p.write_bytes(data[k:k + PART])
        parts.append(p)
    print(f"{src.name}: {len(data)} bytes in {len(parts)} parts")
    print("\n" + INJECT)
    print("\n// 2) file_upload each part into the input labelled 'kitin chunk input', one part per call:")
    for p in parts:
        print("//   " + str(p))
    print("\n" + ASSEMBLE.replace("{name}", src.name))


if __name__ == "__main__":
    main()
