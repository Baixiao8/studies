#!/usr/bin/env python3
"""Batch generate 10 chapter hero images for the sports science manual.

Style fixed: dark background, gold + minor accent line art, editorial,
edge-to-edge full-bleed, 16:9 cinematic, no frame.
"""
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

IMG_DIR = Path("/Users/baixiao/白笑/claude/运动健康/images")
IMG_DIR.mkdir(parents=True, exist_ok=True)

STYLE = (
    "Editorial illustration for a high-end sports science manual. "
    "EDGE-TO-EDGE FULL-BLEED COMPOSITION, no frame, no matte, no border, no margin, no white space around image, fills entire canvas. "
    "Dark near-black background (#0e0e0c). Minimal thin precise gold line art (#d4a548) as primary color, occasional warm crimson accent for emphasis. "
    "Magazine-quality technical illustration aesthetic, refined and restrained. "
    "Wide cinematic 16:9 composition with abundant negative space. "
    "NO TEXT, NO LABELS, NO NUMBERS, NO WORDS anywhere in the image. "
)

CHAPTERS = [
    ("s1_hero",
     "A lone male runner silhouette in profile, mid-stride. Faint anatomical hint of internal circulatory system glowing as gold lines through the body, small mitochondria ellipses scattered, abstract energy waves flowing horizontally behind. Subject: HUMAN PHYSIOLOGY and ENERGY SYSTEMS."),
    ("s2_hero",
     "Abstract architectural diagram of training periodization: concentric arcs and radial lines forming a layered structure, like a strategic blueprint. Suggests CYCLES, PHASES, and SYSTEMATIC PLANNING. No human figure."),
    ("s3_hero",
     "An empty oval running track viewed from a low dramatic perspective, gold lane lines converging to vanishing point. A faint heartbeat / interval rhythm waveform crosses the sky. Subject: WORKOUTS and INTERVAL TRAINING."),
    ("s4_hero",
     "A runner mid-form silhouette captured from the side, gold lines emphasizing posture vectors — spine, hip drive, foot landing. Faint outline of leg muscles as gold contours. Subject: STRENGTH and RUNNING FORM."),
    ("s5_hero",
     "Abstract molecular structure suggesting carbohydrates and electrolytes — hexagonal gold molecules, dotted energy particles, a stylized droplet shape. Subject: NUTRITION and HYDRATION. No human figure."),
    ("s6_hero",
     "A crescent moon high in the sky, gold horizon line below, faint slow gold wave pattern suggesting sleep cycles or HRV oscillation across the lower frame. Subject: SLEEP and RECOVERY. Tranquil minimalism."),
    ("s7_hero",
     "Side profile silhouette of a runner's head, gold contour. Inside the head, abstract gold geometric patterns suggesting focused thought and inner monologue, with a single bright dot at the temple. Subject: SPORTS PSYCHOLOGY."),
    ("s8_hero",
     "An abstract anatomical knee joint or runner's leg seen in side profile, gold lines highlighting key tendons and joints, with subtle crimson glow at one stress point. Subject: INJURY and REHABILITATION."),
    ("s9_hero",
     "A solo runner crossing a finish line, finish tape glowing gold, arms raised in triumph, body in motion-blur gold lines. Faint stadium suggestion in distant negative space. Subject: RACE DAY and TAPER. Cinematic energy."),
    ("s10_hero",
     "A runner walking away from camera into a vast horizon at dawn, long shadow, a thin gold line of sunrise across the horizon. Subject: POST-RACE RECOVERY and reflection. Quiet aftermath."),
]


def submit(out_name: str, content: str) -> str:
    """Submit and return ai_id."""
    body = {
        "model_id": 4714,
        "prompt": STYLE + content,
        "nums": 1,
        "Aspect": 2,  # 16:9
    }
    body_file = Path(f"/tmp/manual_imgs/body_{out_name}.json")
    body_file.parent.mkdir(parents=True, exist_ok=True)
    body_file.write_text(json.dumps(body, ensure_ascii=False))

    result = subprocess.run(
        ["58pic", "same-style", "-m", "4714", "--body-file", str(body_file), "--format", "json"],
        capture_output=True, text=True,
    )
    # CLI exit code may be nonzero even on success; parse stdout/stderr
    output = result.stdout or result.stderr
    try:
        resp = json.loads(output)
    except json.JSONDecodeError:
        raise RuntimeError(f"non-JSON response: {output[:500]}")

    body_resp = resp.get("body", {})
    if body_resp.get("code") != 1:
        raise RuntimeError(f"submit failed: {output[:500]}")

    data = body_resp["data"][0]
    return data["ai_id"]


def poll(ai_id: str, max_wait: int = 180):
    start = time.time()
    while time.time() - start < max_wait:
        result = subprocess.run(
            ["58pic", "same-style-status", str(ai_id), "--format", "json"],
            capture_output=True, text=True,
        )
        output = result.stdout or result.stderr
        try:
            resp = json.loads(output)
        except json.JSONDecodeError:
            time.sleep(3)
            continue
        data = resp["body"]["data"]
        st = data.get("status")
        if st == 3:
            details = data.get("details") or []
            if details:
                return details[0].get("download_url") or details[0].get("image_url")
        time.sleep(4)
    raise TimeoutError(f"task {ai_id} timeout")


def download_compress(url: str, out_name: str):
    out_path = IMG_DIR / (out_name + ".jpg")
    tmp = out_path.with_suffix(".raw")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as f:
        f.write(resp.read())
    subprocess.run(
        ["sips", "-Z", "1280", "-s", "format", "jpeg",
         "-s", "formatOptions", "normal", str(tmp), "--out", str(out_path)],
        capture_output=True, check=True,
    )
    tmp.unlink()
    return out_path


def main():
    # allow filtering: pass chapter names as args
    targets = sys.argv[1:] if len(sys.argv) > 1 else [name for name, _ in CHAPTERS]
    targets_set = set(targets)
    work = [(n, p) for n, p in CHAPTERS if n in targets_set]
    print(f"Generating {len(work)} images...", flush=True)

    # SEQUENTIAL: submit → poll → download → next. Avoids rate limit.
    for name, content in work:
        # Retry submit up to 3 times if rate-limited
        for attempt in range(3):
            try:
                ai_id = submit(name, content)
                print(f"  [submit] {name} → ai_id={ai_id}", flush=True)
                break
            except Exception as e:
                if "请稍等" in str(e) and attempt < 2:
                    print(f"  [submit] {name} rate-limited, wait 8s...", flush=True)
                    time.sleep(8)
                    continue
                print(f"  ✗ {name} submit FAILED: {e}", flush=True)
                ai_id = None
                break
        if not ai_id:
            continue
        try:
            print(f"  [poll] {name} (ai_id={ai_id})...", flush=True)
            url = poll(ai_id)
            out = download_compress(url, name)
            print(f"  ✓ {name}.jpg ({out.stat().st_size//1024}KB)", flush=True)
        except Exception as e:
            print(f"  ✗ {name} download FAILED: {e}", flush=True)


if __name__ == "__main__":
    main()
