#!/usr/bin/env python3
"""V3: Eliminate 'book / magazine / editorial illustration' which trigger
printed-page renderings with fake text. Pure isolated cinematic frame."""
import json, subprocess, sys, time, urllib.request
from pathlib import Path

IMG_DIR = Path("/Users/baixiao/白笑/claude/运动健康/images")

STYLE = (
    "A single cinematic frame. The entire canvas is one continuous visual image, "
    "not a printed page, not a book spread, not a magazine layout, not framed art. "
    "Dark almost-black background fills the frame. The subject is rendered with thin precise gold line work, "
    "with subtle warm crimson accents only where useful for emphasis. "
    "Minimal and restrained composition, abundant negative space, art-house cinematic atmosphere, "
    "purely visual imagery without written characters anywhere in the scene. "
)

WORK = [
    ("s9_hero",
     "A solo runner crossing a finish tape, arms raised in triumph, body in dynamic forward motion. "
     "The finish tape stretches gracefully across the frame in golden light. "
     "A faint stadium grandstand silhouette in the deep background. Cinematic triumphant atmosphere."),
    ("s10_hero",
     "A solo runner viewed from behind, walking slowly into a vast horizon at dawn. "
     "A long shadow stretches behind the figure on a flat empty ground. "
     "A thin warm horizon line glows softly where the sky meets the ground. "
     "Empty contemplative dawn sky, quiet aftermath atmosphere."),
]


def submit(name, content):
    body = {"model_id": 4714, "prompt": STYLE + content, "nums": 1, "Aspect": 2}
    body_file = Path(f"/tmp/manual_imgs/body3_{name}.json")
    body_file.write_text(json.dumps(body, ensure_ascii=False))
    r = subprocess.run(["58pic", "same-style", "-m", "4714", "--body-file", str(body_file), "--format", "json"],
                       capture_output=True, text=True)
    out = r.stdout or r.stderr
    resp = json.loads(out)
    if resp["body"].get("code") != 1:
        raise RuntimeError(out[:300])
    return resp["body"]["data"][0]["ai_id"]


def poll(ai_id, max_wait=180):
    start = time.time()
    while time.time() - start < max_wait:
        r = subprocess.run(["58pic", "same-style-status", str(ai_id), "--format", "json"],
                           capture_output=True, text=True)
        try:
            data = json.loads(r.stdout or r.stderr)["body"]["data"]
        except Exception:
            time.sleep(3); continue
        if data.get("status") == 3 and data.get("details"):
            return data["details"][0].get("download_url") or data["details"][0].get("image_url")
        time.sleep(4)
    raise TimeoutError(ai_id)


def dl(url, name):
    out = IMG_DIR / f"{name}.jpg"
    tmp = out.with_suffix(".raw")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(tmp, "wb") as f:
        f.write(r.read())
    subprocess.run(["sips", "-Z", "1280", "-s", "format", "jpeg", "-s", "formatOptions", "normal",
                    str(tmp), "--out", str(out)], capture_output=True, check=True)
    tmp.unlink()
    return out


for name, content in WORK:
    for attempt in range(3):
        try:
            ai_id = submit(name, content)
            print(f"  [submit] {name} → {ai_id}", flush=True)
            break
        except Exception as e:
            if "请稍等" in str(e) and attempt < 2:
                time.sleep(8); continue
            print(f"  ✗ {name}: {e}"); ai_id = None; break
    if not ai_id: continue
    try:
        url = poll(ai_id)
        out = dl(url, name)
        print(f"  ✓ {name}.jpg ({out.stat().st_size//1024}KB)", flush=True)
    except Exception as e:
        print(f"  ✗ {name} dl: {e}")
