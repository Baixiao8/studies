#!/usr/bin/env python3
"""58pic 图片下载 + 压缩 pipeline.

Usage:
  # Submit + poll + download + compress
  ./img_pipeline.py gen --model 4714 --prompt "..." --out section_01.jpg --aspect "--ar 16:9"

  # Just download + compress an existing oss URL
  ./img_pipeline.py download <url> --out section_01.jpg
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

IMG_DIR = Path("/Users/baixiao/白笑/claude/运动健康/images")
IMG_DIR.mkdir(parents=True, exist_ok=True)


def run58pic(*args):
    """Run 58pic CLI and parse JSON response."""
    result = subprocess.run(
        ["58pic", *args, "--format", "json"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def submit(model_id: int, prompt: str, nums: int = 1, aspect: str = ""):
    """Submit generation task. Returns ai_id."""
    args = ["same-style", "-m", str(model_id), "--prompt", prompt, "--nums", str(nums)]
    resp = run58pic(*args)
    body = resp.get("body", {})
    if body.get("code") != 1:
        raise RuntimeError(f"submit failed: {json.dumps(body, ensure_ascii=False)}")
    data = body["data"][0]
    print(f"  → submitted ai_id={data['ai_id']} (credits used: {data['credits_used']})", file=sys.stderr)
    return data["ai_id"]


def poll(ai_id: str, max_wait: int = 180):
    """Poll task status until done. Returns list of image details."""
    start = time.time()
    while time.time() - start < max_wait:
        resp = run58pic("same-style-status", str(ai_id))
        data = resp["body"]["data"]
        st = data.get("status")
        if st == 3:   # completed with details
            details = data.get("details") or []
            if details:
                return details
        if st in (4, 5):   # failed states (educated guess)
            raise RuntimeError(f"task failed: {json.dumps(data, ensure_ascii=False)}")
        time.sleep(4)
    raise TimeoutError(f"task {ai_id} did not complete in {max_wait}s")


def download(url: str, out_path: Path):
    """Download URL to raw temp file."""
    tmp = out_path.with_suffix(out_path.suffix + ".raw")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as f:
        f.write(resp.read())
    return tmp


def compress(raw_path: Path, out_path: Path, max_dim: int = 1280, quality: str = "normal"):
    """Compress with sips: resize to max_dim, JPEG quality."""
    subprocess.run(
        ["sips", "-Z", str(max_dim),
         "-s", "format", "jpeg",
         "-s", "formatOptions", quality,
         str(raw_path),
         "--out", str(out_path)],
        check=True, capture_output=True,
    )
    raw_path.unlink()
    return out_path


def gen(model_id: int, prompt: str, out_name: str,
        nums: int = 1, max_dim: int = 1280, quality: str = "normal"):
    """End-to-end: submit, poll, download, compress."""
    out_path = IMG_DIR / out_name
    if not out_path.suffix:
        out_path = out_path.with_suffix(".jpg")

    print(f"[gen] {out_name}  prompt: {prompt[:60]}...", file=sys.stderr)
    ai_id = submit(model_id, prompt, nums)
    details = poll(ai_id)
    primary = details[0]
    url = primary.get("download_url") or primary.get("image_url") or primary.get("preview_url")
    if not url:
        raise RuntimeError("no download URL in result")
    raw = download(url, out_path)
    raw_size = raw.stat().st_size
    compress(raw, out_path, max_dim=max_dim, quality=quality)
    final_size = out_path.stat().st_size
    print(f"  ✓ {out_path.name}  {raw_size//1024}KB → {final_size//1024}KB", file=sys.stderr)
    return out_path


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gen", help="generate + download + compress")
    g.add_argument("--model", type=int, default=4714, help="model id (default 即梦4.5)")
    g.add_argument("--prompt", required=True)
    g.add_argument("--out", required=True, help="output filename, saved in images/")
    g.add_argument("--nums", type=int, default=1)
    g.add_argument("--max-dim", type=int, default=1280)
    g.add_argument("--quality", default="normal", choices=["low", "normal", "high", "best"])

    d = sub.add_parser("download", help="download + compress an existing URL")
    d.add_argument("url")
    d.add_argument("--out", required=True)
    d.add_argument("--max-dim", type=int, default=1280)
    d.add_argument("--quality", default="normal")

    c = sub.add_parser("compress", help="compress local images in-place")
    c.add_argument("paths", nargs="+")
    c.add_argument("--max-dim", type=int, default=1280)
    c.add_argument("--quality", default="normal")

    args = p.parse_args()

    if args.cmd == "gen":
        gen(args.model, args.prompt, args.out, args.nums, args.max_dim, args.quality)
    elif args.cmd == "download":
        out = IMG_DIR / args.out
        raw = download(args.url, out)
        compress(raw, out, max_dim=args.max_dim, quality=args.quality)
        print(f"  ✓ {out.name} ({out.stat().st_size//1024}KB)")
    elif args.cmd == "compress":
        for path in args.paths:
            src = Path(path)
            if not src.is_absolute():
                src = IMG_DIR / src
            before = src.stat().st_size
            tmp = src.with_suffix(src.suffix + ".tmp.jpg")
            compress(src, tmp, max_dim=args.max_dim, quality=args.quality)
            tmp.replace(src)
            after = src.stat().st_size
            print(f"  ✓ {src.name}  {before//1024}KB → {after//1024}KB")


if __name__ == "__main__":
    main()
