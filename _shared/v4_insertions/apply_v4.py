#!/usr/bin/env python3
"""
v4 嫁接装配脚本
- 读取各章节 INSERTIONS 数据
- 用 ANCHOR 精确字符串匹配,在 ANCHOR 行后追加 INSERT 内容
- 输出装配报告
"""

import os
import sys
from pathlib import Path

# 项目根目录
ROOT = Path("/Users/baixiao/白笑/claude/运动健康/reports/2026-05-running-science")

# 导入数据 - 动态导入,容错
sys.path.insert(0, str(Path(__file__).parent))


def collect_insertions():
    """从各 chXX_data.py 文件收集 INSERTIONS"""
    all_insertions = []
    data_files = sorted(Path(__file__).parent.glob("data_ch*.py"))
    print(f"[v4] 找到 {len(data_files)} 个数据文件: {[f.name for f in data_files]}")

    for data_file in data_files:
        mod_name = data_file.stem
        try:
            mod = __import__(mod_name)
            if hasattr(mod, "INSERTIONS"):
                count = len(mod.INSERTIONS)
                all_insertions.extend(mod.INSERTIONS)
                print(f"  [{mod_name}] 加载 {count} 个 INSERTION")
        except Exception as e:
            print(f"  [{mod_name}] 加载失败: {e}")

    return all_insertions


def apply_one(file_path: Path, anchor: str, insert: str, dry_run: bool = False) -> tuple[bool, str]:
    """对单个文件应用一个 INSERTION

    检测 insert 是否以 anchor 开头:
    - 是 → replace 模式(用 insert 替换 anchor)
    - 否 → append 模式(在 anchor 后追加 insert)
    """
    if not file_path.exists():
        return False, f"文件不存在: {file_path}"

    content = file_path.read_text(encoding="utf-8")

    # 精确匹配
    if anchor not in content:
        # 容错:尝试去掉前后空白后匹配
        anchor_stripped = anchor.strip()
        if anchor_stripped in content:
            anchor = anchor_stripped
        else:
            return False, f"ANCHOR 未找到: {anchor[:60]!r}..."

    # 检测出现次数,>1 时拒绝(避免错装)
    occurrences = content.count(anchor)
    if occurrences > 1:
        return False, f"ANCHOR 出现 {occurrences} 次,模糊不可装: {anchor[:60]!r}..."

    # 检测 insert 是否以 anchor 开头(replace 模式)
    insert_lstripped = insert.lstrip()
    anchor_lstripped = anchor.lstrip()

    if insert_lstripped.startswith(anchor_lstripped[:80]):
        # replace 模式: insert 已包含 anchor,用整段 insert 替换 anchor
        new_content = content.replace(anchor, insert.rstrip(), 1)
        mode = "replace"
    else:
        # append 模式: 在 anchor 后追加 insert(空一行间隔)
        new_content = content.replace(anchor, anchor + "\n" + insert.rstrip(), 1)
        mode = "append"

    if not dry_run:
        file_path.write_text(new_content, encoding="utf-8")
    return True, f"OK [{mode}]"


def main():
    dry_run = "--apply" not in sys.argv
    if dry_run:
        print("[v4] DRY RUN 模式 (加 --apply 才实际写入)\n")
    else:
        print("[v4] APPLY 模式 (将实际修改文件)\n")

    insertions = collect_insertions()
    print(f"\n[v4] 总计 {len(insertions)} 个 INSERTION 待装配\n")

    stats = {"success": 0, "failed": 0, "failures": []}
    by_file = {}

    for i, ins in enumerate(insertions, 1):
        file_rel = ins["file"]
        anchor = ins["anchor"]
        insert = ins["insert"]

        file_path = ROOT / file_rel
        ok, msg = apply_one(file_path, anchor, insert)

        by_file.setdefault(file_rel, {"ok": 0, "fail": 0})
        if ok:
            stats["success"] += 1
            by_file[file_rel]["ok"] += 1
        else:
            stats["failed"] += 1
            by_file[file_rel]["fail"] += 1
            stats["failures"].append((i, file_rel, msg, anchor[:80]))

    # 报告
    print("=" * 70)
    print(f"[v4] 装配完成")
    print(f"  成功: {stats['success']}")
    print(f"  失败: {stats['failed']}")
    print()
    print("按文件:")
    for f, s in sorted(by_file.items()):
        flag = "✓" if s["fail"] == 0 else "✗"
        print(f"  {flag} {f}: {s['ok']} ok, {s['fail']} fail")

    if stats["failures"]:
        print("\n失败明细:")
        for i, f, msg, anchor in stats["failures"]:
            print(f"  #{i} {f}: {msg}")
            print(f"      anchor 预览: {anchor!r}")

    return 0 if stats["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
