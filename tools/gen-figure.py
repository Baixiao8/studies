#!/usr/bin/env python3
"""
gen-figure.py · 调 OpenAI 图像生成 (gpt-image-1) 生成图,存为 PNG。

用法:
  tools/.venv/bin/python3 tools/gen-figure.py "你的 prompt" -o assets/xxx.png
  可选:
    --size 1024x1024 | 1536x1024 | 1024x1536 | auto   (gpt-image-1)
    --model gpt-image-1 (默认) | dall-e-3
    --quality high | medium | low                      (仅 gpt-image-1)

key 来源(按优先级):
  1. 环境变量 OPENAI_API_KEY
  2. 项目根 .env 里的 OPENAI_API_KEY=...

安全约定:
  · key 永远不会被打印到终端或日志
  · .env 已在 .gitignore,不会提交、不会外泄
"""
import os
import sys
import argparse
import base64
from pathlib import Path


def load_key() -> str | None:
    """优先环境变量,其次项目根 .env。返回 key 或 None。"""
    k = os.environ.get("OPENAI_API_KEY")
    if k:
        return k.strip()
    root = Path(__file__).resolve().parent.parent
    env = root / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENAI_API_KEY") and "=" in line:
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def mask(key: str) -> str:
    """只回显前 7 位,用于确认而不泄露。"""
    return (key[:7] + "…") if len(key) > 8 else "set"


def main():
    ap = argparse.ArgumentParser(description="OpenAI 图像生成 → PNG")
    ap.add_argument("prompt", help="生图描述词")
    ap.add_argument("-o", "--output", required=True, help="输出 PNG 路径")
    ap.add_argument("--size", default="1024x1024",
                    help="1024x1024 | 1536x1024 | 1024x1536 | auto")
    ap.add_argument("--model", default="gpt-image-1",
                    help="gpt-image-1 (默认) | dall-e-3")
    ap.add_argument("--quality", default="high", help="high|medium|low (仅 gpt-image-1)")
    args = ap.parse_args()

    key = load_key()
    if not key:
        print("✗ 没找到 OPENAI_API_KEY(环境变量和 .env 都没有)。", file=sys.stderr)
        print("  在项目根 .env 写一行: OPENAI_API_KEY=sk-...", file=sys.stderr)
        sys.exit(1)
    print(f"[gen-figure] key={mask(key)} model={args.model} size={args.size} → {args.output}")

    try:
        from openai import OpenAI
    except ImportError:
        print("✗ 没装 openai 库。跑: tools/.venv/bin/pip install openai", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=key)
    kwargs = dict(model=args.model, prompt=args.prompt, size=args.size, n=1)
    if args.model == "gpt-image-1":
        kwargs["quality"] = args.quality
    try:
        resp = client.images.generate(**kwargs)
    except Exception as e:
        print(f"✗ 生成失败: {e}", file=sys.stderr)
        sys.exit(2)

    data = resp.data[0]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if getattr(data, "b64_json", None):
        out.write_bytes(base64.b64decode(data.b64_json))
    elif getattr(data, "url", None):
        import urllib.request
        urllib.request.urlretrieve(data.url, out)
    else:
        print("✗ 返回里既无 b64_json 也无 url", file=sys.stderr)
        sys.exit(3)
    print(f"✓ 已存 {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
