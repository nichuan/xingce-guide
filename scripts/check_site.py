#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""站点构建产物自检：标签闭合、残留 Markdown、内联 JS 语法、关键结构统计。

用法：
    python3 scripts/check_site.py dist/index.html

任何一项不通过即以非 0 退出码结束（CI 会因此失败，避免把坏页面发到 Pages）。
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

VOID = {"br", "img", "meta", "link", "hr", "input", "source", "area", "base",
        "col", "embed", "param", "track", "wbr"}

MIN_UNITS = 20          # 至少多少个学习单元
MIN_QUIZ = 10           # 至少多少道例题
MIN_TABLES = 10         # 至少多少张表格


class Balance(HTMLParser):
    """校验标签闭合：任何未闭合/多余闭合都记为错误。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, tuple[int, int]]] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        if tag not in VOID:
            self.errors.append(f"<{tag}/> 自闭合标签不在白名单内 {self.getpos()}")

    def handle_endtag(self, tag):
        if not self.stack:
            self.errors.append(f"多余的闭合标签 </{tag}> {self.getpos()}")
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for _, pos in self.stack[i + 1:]:
                    self.errors.append(f"未闭合标签 <{self.stack[i + 1][0]}> 起始于 {pos}")
                del self.stack[i:]
                return
        self.errors.append(f"无法匹配的闭合标签 </{tag}> {self.getpos()}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("用法: python3 scripts/check_site.py <html 路径>", file=sys.stderr)
        return 2

    path = argv[1]
    if not os.path.isfile(path):
        print(f"找不到文件: {path}", file=sys.stderr)
        return 2

    html = open(path, encoding="utf-8").read()
    problems: list[str] = []

    # 1) 标签闭合
    parser = Balance()
    parser.feed(html)
    for tag, pos in parser.stack:
        parser.errors.append(f"未闭合标签 <{tag}> 起始于 {pos}")
    problems += parser.errors[:20]

    # 2) 残留 Markdown 标记
    for pat, name in ((r"\*\*", "粗体标记 **"), (r"\\\|", "转义竖线 \\|")):
        hits = len(re.findall(pat, html))
        if hits:
            problems.append(f"残留 {name} × {hits}")

    # 3) 关键结构统计
    stats = {
        "chapters": len(re.findall(r'<section class="chapter', html)),
        "units": len(re.findall(r"data-unit=\"", html)),
        "checkboxes": html.count('data-done="'),
        "quiz": html.count('<details class="quiz-details">'),
        "tables": html.count("<table>"),
        "toc_links": html.count('class="toc-a'),
    }
    if stats["units"] < MIN_UNITS:
        problems.append(f"学习单元过少: {stats['units']} < {MIN_UNITS}")
    if stats["quiz"] < MIN_QUIZ:
        problems.append(f"例题过少: {stats['quiz']} < {MIN_QUIZ}")
    if stats["tables"] < MIN_TABLES:
        problems.append(f"表格过少: {stats['tables']} < {MIN_TABLES}")
    if stats["units"] != stats["checkboxes"]:
        problems.append(f"单元数与勾选框数不一致: {stats['units']} vs {stats['checkboxes']}")
    if stats["toc_links"] < stats["units"]:
        problems.append(f"目录条目少于学习单元: {stats['toc_links']} < {stats['units']}")

    # 4) 内联 JS 语法（有 node 才检查）
    m = re.search(r"<script>(.*?)</script>", html, re.S)
    if not m:
        problems.append("未找到内联 <script>")
    elif shutil.which("node"):
        with tempfile.TemporaryDirectory() as tmp:
            js = os.path.join(tmp, "inline.js")
            with open(js, "w", encoding="utf-8") as f:
                f.write(m.group(1))
            proc = subprocess.run(["node", "--check", js], capture_output=True, text=True)
            if proc.returncode != 0:
                problems.append("内联 JS 语法错误: " + (proc.stderr.strip().splitlines() or [""])[-1])
    else:
        print("提示: 未检测到 node，跳过内联 JS 语法检查")

    size_kb = os.path.getsize(path) / 1024
    print(f"站点文件: {path} ({size_kb:.1f} KB)")
    print("结构统计: " + ", ".join(f"{k}={v}" for k, v in stats.items()))

    if problems:
        print("\n❌ 自检失败：", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        return 1

    print("✅ 自检通过")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
