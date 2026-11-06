"""Upload publish copies of episodes to a GitHub release so posting services (Zapier) can fetch them by a direct URL.
Creates the public repo <your GitHub user>/<repo> and the release 'tapes' if missing; re-uploading a file replaces it.
Uses the GitHub login git already has (git credential fill); the token is never printed. See docs/PUBLISHING.md (A4).
Usage: python tools/publish_release.py [--repo cult_pixel_media] <file.mp4> [<file.mp4> ...]"""
import json, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

args = sys.argv[1:]
REPO, TAG = "cult_pixel_media", "tapes"
if "--repo" in args:
    i = args.index("--repo"); REPO = args[i + 1]; del args[i:i + 2]
if not args:
    sys.exit(__doc__)
out = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n",
                     capture_output=True, text=True).stdout
tok = dict(l.split("=", 1) for l in out.splitlines() if "=" in l).get("password")
if not tok:
    sys.exit("git has no GitHub login on this machine: push once to any GitHub repo (or install Git Credential Manager) and retry")
H = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", "User-Agent": "shorts-factory-publisher"}


def api(method, url, body=None, data=None, ctype="application/json"):
    payload = data if data is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(url, method=method, data=payload, headers=dict(H, **{"Content-Type": ctype}))
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


owner = api("GET", "https://api.github.com/user")[1].get("login")
R = f"{owner}/{REPO}"
if api("GET", f"https://api.github.com/repos/{R}")[0] == 404:
    s, j = api("POST", "https://api.github.com/user/repos", {"name": REPO, "private": False, "auto_init": True,
               "description": "Publish copies of short videos (direct links for scheduled posting)."})
    print(f"repo {R} created" if s == 201 else f"repo error {s}: {j.get('message')}")
s, rel = api("GET", f"https://api.github.com/repos/{R}/releases/tags/{TAG}")
if s == 404:
    s, rel = api("POST", f"https://api.github.com/repos/{R}/releases", {"tag_name": TAG, "name": "Episodes"})
have = {a["name"]: a for a in rel.get("assets", [])}
upload = rel["upload_url"].split("{")[0]
for f in args:
    p = Path(f)
    if p.name in have:
        api("DELETE", have[p.name]["url"])
    s, a = api("POST", f"{upload}?name={p.name}", data=p.read_bytes(), ctype="video/mp4")
    print(p.name, "->", a.get("browser_download_url") or f"error {s}: {a.get('message')}")
