#!/usr/bin/env python3
"""Regenerate hero images with text-safe prompts (no hex codes, no ALL CAPS,
no negative commands like 'NO TEXT' — those leak into generated images)."""
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

IMG_DIR = Path("/Users/baixiao/白笑/claude/运动健康/images")

# Reformulated style — no hex, no ALL CAPS, no negative instructions
STYLE = (
    "A refined editorial illustration for a high-end sports science book. "
    "The image fills the entire canvas from edge to edge in a wide cinematic composition. "
    "Dark almost-black background dominates the frame. "
    "The subject is rendered with thin precise gold line work, with subtle warm crimson accents only where useful for emphasis. "
    "Magazine-quality technical illustration, minimal and restrained, abundant negative space, art-house aesthetic, purely visual imagery without any written characters. "
)

REDO = [
    ("s4_hero",
     "A side-profile silhouette of a male runner mid-stride captured with anatomical precision. "
     "Thin gold lines emphasize the spine curve, hip drive, leg muscles, and foot landing. "
     "The figure is in dynamic forward motion. Subtle bone and muscle structure visible through the silhouette."),

    ("s5_hero",
     "Floating hexagonal molecular structures suggesting carbohydrates, scattered tiny glowing energy dots, "
     "and a single stylized translucent water droplet at the center of the composition. "
     "Pure abstract chemistry visualization, no human figure, no environment."),

    ("s6_hero",
     "A serene crescent moon high in a vast dark sky, a faint warm glow at the horizon line, "
     "and a gentle slow undulating sine wave pattern across the lower portion of the frame suggesting heart rate variability during deep sleep. "
     "Tranquil minimalism, no figures, no buildings."),

    ("s8_hero",
     "An abstract side view of a runner's knee and lower leg joint, rendered with anatomical precision in thin gold lines. "
     "A single soft warm crimson glow at the joint center indicates a stress point. "
     "Tendons, ligaments and muscle contours visible. No other body parts beyond the leg."),

    ("s9_hero",
     "A solo runner crossing a finish tape, arms raised in triumph, body in dynamic forward motion. "
     "The finish tape stretches gracefully across the frame in golden light. "
     "A stadium grandstand suggestion in the deep background as faint silhouette. Cinematic triumphant energy."),

    ("s10_hero",
     "A solo runner walking slowly away from the viewer into a vast horizon at dawn. "
     "A long shadow stretches behind the figure. A thin warm horizon line glows softly where the sky meets the ground. "
     "Quiet reflective aftermath, abundant sky, contemplative atmosphere."),
]


def submit(name, content):
    body = {"model_id": 4714, "prompt": STYLE + content, "nums": 1, "Aspect": 2}
    body_file = Path(f"/tmp/manual_imgs/body2_{name}.json")
    body_file.write_text(json.dumps(body, ensure_ascii=False))
    result = subprocess.run(
        ["58pic", "same-style", "-m", "4714", "--body-file", str(body_file), "--format", "json"],
        capture_output=True, text=True,
    )
    output = result.stdout or result.stderr
    resp = json.loads(output)
    if resp["body"].get("code") != 1:
        raise RuntimeError(output[:300])
    return resp["body"]["data"][0]["ai_id"]


def poll(ai_id, max_wait=180):
    start = time.time()
    while time.time() - start < max_wait:
        result = subprocess.run(
            ["58pic", "same-style-status", str(ai_id), "--format", "json"],
            capture_output=True, text=True,
        )
        try:
            data = json.loads(result.stdout or result.stderr)["body"]["data"]
        except Exception:
            time.sleep(3); continue
        if data.get("status") == 3 and data.get("details"):
            return data["details"][0].get("download_url") or data["details"][0].get("image_url")
        time.sleep(4)
    raise TimeoutError(ai_id)


def download_compress(url, name):
    out_path = IMG_DIR / f"{name}.jpg"
    tmp = out_path.with_suffix(".raw")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(tmp, "wb") as f:
        f.write(r.read())
    subprocess.run(
        ["sips", "-Z", "1280", "-s", "format", "jpeg", "-s", "formatOptions", "normal",
         str(tmp), "--out", str(out_path)],
        capture_output=True, check=True,
    )
    tmp.unlink()
    return out_path


def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else [n for n, _ in REDO]
    work = [(n, p) for n, p in REDO if n in targets]
    print(f"Regenerating {len(work)} images with text-safe prompts...", flush=True)

    for name, content in work:
        for attempt in range(3):
            try:
                ai_id = submit(name, content)
                print(f"  [submit] {name} → ai_id={ai_id}", flush=True)
                break
            except Exception as e:
                if "请稍等" in str(e) and attempt < 2:
                    print(f"  [submit] {name} rate-limited, wait 8s", flush=True)
                    time.sleep(8)
                else:
                    print(f"  ✗ submit {name}: {e}", flush=True)
                    ai_id = None
                    break
        if not ai_id:
            continue
        try:
            url = poll(ai_id)
            out = download_compress(url, name)
            print(f"  ✓ {name}.jpg ({out.stat().st_size//1024}KB)", flush=True)
        except Exception as e:
            print(f"  ✗ {name} download: {e}", flush=True)


if __name__ == "__main__":
    main()
