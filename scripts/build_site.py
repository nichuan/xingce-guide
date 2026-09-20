#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown 长文 → 单文件静态学习网站。

用法：
  python3 build_site.py --input final_draft.md --output ./site \
      --title "行测六大模块" --subtitle "考点 / 技巧 / 例题" --logo "行测"

产物：<output>/index.html（HTML + CSS + JS + 内容全部内联，零外部依赖）
"""
from __future__ import annotations

import argparse
import html
import os
import re
import sys

# --------------------------------------------------------------- 参数
ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True, help="源 Markdown 路径")
ap.add_argument("--output", required=True, help="输出目录")
ap.add_argument("--title", default="学习手册", help="站点标题")
ap.add_argument("--subtitle", default="考点 / 技巧 / 例题", help="顶栏副标题")
ap.add_argument("--logo", default="学", help="logo 方块文字（1-2 字）")
ap.add_argument("--quiz-re", default=r"^\*\*(?:示例|例题)\s*(\d+)\*\*(.*)$",
                help="例题标题正则（默认匹配 **示例 1** / **例题 1**）")
ap.add_argument("--quiz-label", default="例题", help="例题卡片前缀文案")
ap.add_argument("--download", default="", help="可选：顶栏下载链接的文件路径（相对站点根）")
ap.add_argument("--download-label", default="下载 Word 版", help="下载链接文案")
args = ap.parse_args()

SRC = os.path.abspath(args.input)
OUT = os.path.join(os.path.abspath(args.output), "index.html")
EX_Q = re.compile(args.quiz_re)
EX_A = re.compile(r"^\*\*解析\*\*")

md = open(SRC, encoding="utf-8").read()
lines = md.split("\n")


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(t: str) -> str:
    t = t.replace("\\|", "|")
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+?)`", r"<code>\1</code>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", t)
    return t


def plain(t: str) -> str:
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"`([^`]+?)`", r"\1", t)
    return t


def split_row(row: str):
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    row = row.replace("\\|", "\x00")
    return [c.strip().replace("\x00", "|") for c in row.split("|")]


IS_SEP = re.compile(r"^\|[\s:\-|]+\|$")

# --------------------------------------------------------------- 解析为块
blocks = []
i, n = 0, len(lines)
while i < n:
    ln = lines[i]
    s = ln.strip()
    if s == "" or s in ("---", "***", "___"):
        i += 1
        continue
    if s.startswith("```"):
        i += 1
        buf = []
        while i < n and not lines[i].strip().startswith("```"):
            buf.append(lines[i])
            i += 1
        i += 1
        blocks.append(("code", buf))
        continue
    if s.startswith("#"):
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        blocks.append(("h", len(m.group(1)), m.group(2).strip()))
        i += 1
        continue
    if s.startswith("|"):
        rows = []
        while i < n and lines[i].strip().startswith("|"):
            if not IS_SEP.match(lines[i].strip()):
                rows.append(split_row(lines[i]))
            i += 1
        blocks.append(("table", rows))
        continue
    if s.startswith(">"):
        paras, cur = [], []
        while i < n and lines[i].strip().startswith(">"):
            t = lines[i].strip()[1:].strip()
            if t:
                cur.append(t)
            elif cur:
                paras.append(" ".join(cur))
                cur = []
            i += 1
        if cur:
            paras.append(" ".join(cur))
        blocks.append(("quote", paras))
        continue
    m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", ln)
    if m:
        items = []
        while i < n:
            m2 = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
            if not m2:
                break
            items.append((len(m2.group(1)), m2.group(2) not in ("-", "*"), m2.group(3).strip()))
            i += 1
        blocks.append(("list", items))
        continue
    buf = [s]
    i += 1
    while i < n:
        ns = lines[i].strip()
        if ns == "" or ns.startswith(("#", "|", ">", "```")) or ns in ("---", "***", "___") \
                or re.match(r"^(\s*)([-*]|\d+\.)\s+", lines[i]):
            break
        buf.append(ns)
        i += 1
    blocks.append(("p", " ".join(buf)))


# --------------------------------------------------------------- 渲染器
def render_list(items):
    parts, stack = [], []  # 每层 [indent, tag, li_open]
    for indent, ordered, text in items:
        tag = "ol" if ordered else "ul"
        while stack and indent < stack[-1][0]:
            lvl = stack.pop()
            if lvl[2]:
                parts.append("</li>")
            parts.append("</%s>" % lvl[1])
        if not stack or indent > stack[-1][0]:
            parts.append("<%s>" % tag)
            stack.append([indent, tag, False])
        else:
            if stack[-1][2]:
                parts.append("</li>")
            if stack[-1][1] != tag:
                parts.append("</%s>" % stack.pop()[1])
                parts.append("<%s>" % tag)
                stack.append([indent, tag, False])
        parts.append("<li>%s" % inline(text))
        stack[-1][2] = True
    while stack:
        lvl = stack.pop()
        if lvl[2]:
            parts.append("</li>")
        parts.append("</%s>" % lvl[1])
    return "".join(parts)


def render_table(rows):
    if not rows:
        return ""
    cols = max(len(r) for r in rows)
    head = "".join("<th>%s</th>" % inline(c) for c in rows[0]) + "<th></th>" * (cols - len(rows[0]))
    body = []
    for r in rows[1:]:
        body.append("<tr>%s</tr>" % ("".join("<td>%s</td>" % inline(c) for c in r)
                                     + "<td></td>" * (cols - len(r))))
    return ('<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            % (head, "".join(body)))


def render_block(b):
    k = b[0]
    if k == "p":
        return "<p>%s</p>" % inline(b[1])
    if k == "quote":
        return '<div class="note">%s</div>' % "".join("<p>%s</p>" % inline(x) for x in b[1])
    if k == "table":
        return render_table(b[1])
    if k == "list":
        return render_list(b[1])
    if k == "code":
        return '<pre class="mono">%s</pre>' % esc("\n".join(b[1]))
    return ""


# --------------------------------------------------------------- 组装内容
chapters, content = [], []
unit_seq = chapter_seq = lesson_seq = 0
cur_ch = cur_unit = None
idx, N = 0, len(blocks)

while idx < N:
    b = blocks[idx]
    if b[0] == "h":
        lvl, text = b[1], b[2]
        if lvl == 1:
            idx += 1
            continue
        if lvl == 2:
            if cur_unit is not None:
                content.append("</section>")
                cur_unit = None
            if cur_ch is not None:
                content.append("</section>")
            chapter_seq += 1
            cur_ch = {"id": "c%d" % chapter_seq, "title": text, "units": [], "has_unit": False}
            chapters.append(cur_ch)
            content.append('<section class="chapter" id="c%d" data-anchor="c%d">' % (chapter_seq, chapter_seq))
            content.append('<h2 id="h%d">%s<a class="anchor" href="#h%d" aria-label="复制链接">#</a></h2>'
                           % (chapter_seq, inline(text), chapter_seq))
            idx += 1
            continue
        if lvl == 3:
            if cur_unit is not None:
                content.append("</section>")
            unit_seq += 1
            if cur_ch is not None:
                cur_ch["has_unit"] = True
            uid = "u%d" % unit_seq
            cur_unit = {"id": uid, "title": text, "lessons": []}
            if cur_ch is not None:
                cur_ch["units"].append(cur_unit)
            content.append('<section class="unit" id="%s" data-unit="%s" data-title="%s">'
                           % (uid, uid, esc(plain(text))))
            content.append(
                '<div class="unit-head"><h3 id="h-%s">%s<a class="anchor" href="#h-%s" aria-label="复制链接">#</a></h3>'
                '<label class="done"><input type="checkbox" data-done="%s"><span>已掌握</span></label></div>'
                % (uid, inline(text), uid, uid))
            idx += 1
            continue
        lesson_seq += 1
        m = re.match(r"^(\d+(?:\.\d+)*)", text)
        lid = "l%s" % (m.group(1).replace(".", "-") if m else lesson_seq)
        if cur_unit is not None:
            cur_unit["lessons"].append({"id": lid, "title": text})
        content.append('<h4 id="%s">%s<a class="anchor" href="#%s" aria-label="复制链接">#</a></h4>'
                       % (lid, inline(text), lid))
        idx += 1
        continue

    if b[0] == "p":
        m = EX_Q.match(b[1])
        if m:
            j, stem, ans, found = idx + 1, [], [], False
            while j < N:
                nb = blocks[j]
                if nb[0] == "h" or (nb[0] == "p" and EX_Q.match(nb[1])):
                    break
                if nb[0] == "p" and EX_A.match(nb[1]):
                    found = True
                    ans.append(render_block(("p", re.sub(r"^\*\*解析\*\*[：:]?\s*", "", nb[1]))))
                    j += 1
                    if j < N and blocks[j][0] == "quote":
                        ans.append(render_block(blocks[j]))
                        j += 1
                    continue
                (ans if found else stem).append(render_block(nb))
                j += 1
            if found:
                tag = plain(m.group(2)).strip(" （）")
                content.append(
                    '<div class="quiz">'
                    '<div class="quiz-label">%s %s%s</div>'
                    '<div class="quiz-stem">%s</div>'
                    '<details class="quiz-details"><summary><span class="sum-open">显示解析与答案</span>'
                    '<span class="sum-close">收起解析</span></summary>'
                    '<div class="quiz-answer">%s</div></details></div>'
                    % (args.quiz_label, m.group(1),
                       (' <span class="quiz-tag">%s</span>' % esc(tag)) if tag else "",
                       "".join(stem), "".join(ans)))
                idx = j
                continue

    content.append(render_block(b))
    idx += 1

if cur_unit is not None:
    content.append("</section>")
if cur_ch is not None:
    content.append("</section>")

body_html = "\n".join(content)


def build_toc():
    out = ['<ol class="toc-l1">']
    for ch in chapters:
        out.append('<li class="toc-ch" data-target="%s">' % ch["id"])
        out.append('<a class="toc-a toc-h2" href="#%s">%s</a>' % (ch["id"], inline(ch["title"])))
        if ch["units"]:
            out.append('<ol class="toc-l2">')
            for u in ch["units"]:
                has_kids = bool(u["lessons"])
                caret = ('<button class="caret" type="button" aria-label="展开"></button>' if has_kids
                         else '<span class="caret-spacer"></span>')
                out.append('<li class="toc-u" data-target="%s">' % u["id"])
                out.append('<div class="toc-row">%s<a class="toc-a toc-h3" href="#%s">%s</a>'
                           '<span class="toc-check"></span></div>'
                           % (caret, u["id"], inline(u["title"])))
                if has_kids:
                    out.append('<ol class="toc-l3">')
                    for ls in u["lessons"]:
                        out.append('<li><a class="toc-a toc-h4" href="#%s">%s</a></li>'
                                   % (ls["id"], inline(ls["title"])))
                    out.append("</ol>")
                out.append("</li>")
            out.append("</ol>")
        out.append("</li>")
    out.append("</ol>")
    return "".join(out)


toc_html = build_toc()
n_units = unit_seq

STYLE = r"""
:root{
  --bg:#eef2f7; --panel:#ffffff; --panel2:#f7f9fc; --text:#1f2937; --muted:#66748a;
  --primary:#1565c0; --primary-soft:#e8f1fb; --accent:#00897b; --warn:#e65100;
  --border:#e2e8f0; --border-strong:#cbd5e1; --shadow:0 1px 2px rgba(16,32,64,.06),0 8px 24px rgba(16,32,64,.06);
  --code-bg:#f4f6fa; --mark:#fff3a3; --radius:12px;
  --fs-base:16px; --lh:1.85; --content-max:900px;
  --ff:"PingFang SC","Microsoft YaHei","Hiragino Sans GB","Source Han Sans SC",system-ui,-apple-system,"Segoe UI",sans-serif;
  --ff-mono:"SF Mono",Consolas,"Liberation Mono",Menlo,monospace;
}
html[data-theme="dark"]{
  --bg:#0d1420; --panel:#151f2c; --panel2:#1a2534; --text:#dde7f2; --muted:#8fa3ba;
  --primary:#6db0f2; --primary-soft:#17293c; --accent:#4fd1b5; --warn:#ffab70;
  --border:#243142; --border-strong:#33445a; --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px rgba(0,0,0,.35);
  --code-bg:#111a26; --mark:#5c4d00;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:76px}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--ff);
  font-size:var(--fs-base);line-height:var(--lh);-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}

.topbar{position:sticky;top:0;z-index:60;display:flex;align-items:center;gap:10px;
  padding:10px 16px;background:var(--panel);
  backdrop-filter:saturate(180%) blur(12px);border-bottom:1px solid var(--border)}
@supports (background:color-mix(in srgb,red 50%,transparent)){
  .topbar{background:color-mix(in srgb,var(--panel) 88%,transparent)}
}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;white-space:nowrap}
.brand .logo{width:26px;height:26px;border-radius:8px;background:linear-gradient(135deg,var(--primary),var(--accent));
  display:grid;place-items:center;color:#fff;font-size:12px;font-weight:800}
.brand small{display:block;font-weight:400;color:var(--muted);font-size:11px;line-height:1.1}
.searchbox{position:relative;flex:1 1 200px;min-width:0;max-width:520px;margin-left:auto}
.searchbox input{width:100%;padding:8px 34px 8px 34px;border:1px solid var(--border);border-radius:999px;
  background:var(--panel2);color:var(--text);font-size:14px;font-family:var(--ff);outline:none}
.searchbox input:focus{border-color:var(--primary);box-shadow:0 0 0 3px var(--primary-soft)}
.searchbox .ico{position:absolute;left:11px;top:50%;transform:translateY(-50%);color:var(--muted);font-size:13px}
.searchbox kbd{position:absolute;right:10px;top:50%;transform:translateY(-50%);font-family:var(--ff-mono);
  font-size:11px;color:var(--muted);border:1px solid var(--border);border-radius:5px;padding:1px 5px;background:var(--panel)}
.snav{display:none;align-items:center;gap:2px;font-size:12px;color:var(--muted);white-space:nowrap}
.snav.on{display:flex}
.snav button{background:var(--panel2);border:1px solid var(--border);color:var(--text);
  border-radius:6px;padding:3px 7px;cursor:pointer;font-size:12px}
.tools{display:flex;align-items:center;gap:6px}
.tbtn{background:var(--panel2);border:1px solid var(--border);color:var(--text);border-radius:9px;
  padding:6px 10px;font-size:13px;cursor:pointer;font-family:var(--ff);white-space:nowrap;transition:.15s}
.tbtn:hover{border-color:var(--primary);color:var(--primary)}
.tbtn.pri{background:var(--primary);border-color:var(--primary);color:#fff}
.tbtn.pri:hover{opacity:.9;color:#fff}
.tbtn.icon{padding:6px 9px}
#menuBtn{display:none}
.progress-track{height:3px;background:transparent}
#studyBar{height:3px;width:0;background:linear-gradient(90deg,var(--primary),var(--accent));transition:width .25s}

.layout{display:grid;grid-template-columns:300px minmax(0,1fr);gap:26px;
  max-width:1440px;margin:0 auto;padding:22px 24px 60px}
.sidebar{position:sticky;top:74px;align-self:start;max-height:calc(100vh - 96px);overflow-y:auto;
  padding-right:4px;scrollbar-width:thin}
.sidebar::-webkit-scrollbar{width:8px}
.sidebar::-webkit-scrollbar-thumb{background:var(--border-strong);border-radius:8px}
.side-card{background:var(--panel);border:1px solid var(--border);border-radius:var(--radius);
  padding:12px 14px;margin-bottom:14px;box-shadow:var(--shadow)}
.side-card h4{margin:0 0 8px;font-size:13px;color:var(--muted);font-weight:600;letter-spacing:.04em}
.pbar{height:8px;border-radius:99px;background:var(--panel2);border:1px solid var(--border);overflow:hidden}
.pbar>i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--primary),var(--accent));transition:width .25s}
.pmeta{display:flex;justify-content:space-between;align-items:center;margin-top:8px;font-size:12px;color:var(--muted)}
.pmeta button{background:none;border:none;color:var(--muted);font-size:12px;cursor:pointer;text-decoration:underline;padding:0}
.pmeta button:hover{color:var(--primary)}

.toc-l1,.toc-l2,.toc-l3{list-style:none;margin:0;padding:0}
.toc-l1{border-left:2px solid var(--border);margin-left:2px}
.toc-a{display:block;padding:5px 10px;border-radius:8px;color:var(--muted);font-size:13.5px;
  border-left:2px solid transparent;margin-left:-2px;cursor:pointer}
.toc-a:hover{color:var(--primary);background:var(--panel2)}
.toc-h2{color:var(--text);font-weight:700;font-size:14px;margin-top:6px}
.toc-row{display:flex;align-items:center;gap:2px;margin-left:-2px;border-left:2px solid transparent}
.toc-row:hover{background:var(--panel2);border-radius:8px}
.caret,.caret-spacer{flex:0 0 18px;width:18px;height:18px;border:none;background:none;color:var(--muted);
  cursor:pointer;font-size:10px;display:grid;place-items:center;transition:transform .18s}
.caret-spacer{cursor:default}
.toc-u.open>.toc-row .caret{transform:rotate(90deg)}
.toc-l3{display:none;margin-left:16px}
.toc-u.open>.toc-l3{display:block}
.toc-h4{font-size:12.5px;padding:3px 8px;color:var(--muted)}
.toc-a.active{color:var(--primary);background:var(--primary-soft);border-left-color:var(--primary);font-weight:600}
.toc-check{flex:0 0 auto;font-size:11px;color:var(--accent);opacity:0}
.toc-u.done .toc-check{opacity:1}
.toc-u.done .toc-check::after{content:"✓"}
.toc-u.done>.toc-row .toc-h3{color:var(--accent)}

.content{background:var(--panel);border:1px solid var(--border);border-radius:16px;
  padding:34px 44px 56px;box-shadow:var(--shadow);max-width:var(--content-max);min-width:0}
.content>*:first-child{margin-top:0}
h1,h2,h3,h4{line-height:1.35;scroll-margin-top:78px}
h2{font-size:calc(var(--fs-base) * 1.55);margin:0 0 18px;padding:0 0 12px;color:var(--text);
  border-bottom:2px solid var(--border);position:relative}
h3{font-size:calc(var(--fs-base) * 1.2);margin:34px 0 14px;color:var(--primary)}
h4{font-size:calc(var(--fs-base) * 1.02);margin:22px 0 10px;color:var(--text)}
.chapter{padding-top:34px;margin-top:30px;border-top:1px dashed var(--border)}
.chapter:first-child{padding-top:0;margin-top:0;border-top:none}
.unit{scroll-margin-top:78px}
.unit-head{display:flex;align-items:center;gap:12px;margin:34px 0 14px;flex-wrap:wrap}
.unit-head h3{margin:0;flex:1}
.done{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;color:var(--muted);
  border:1px solid var(--border);border-radius:999px;padding:3px 10px;cursor:pointer;user-select:none;
  background:var(--panel2);white-space:nowrap;transition:.15s}
.done:hover{border-color:var(--primary);color:var(--primary)}
.done input{accent-color:var(--accent);cursor:pointer;margin:0}
.unit.is-done .unit-head h3{color:var(--accent)}
.unit.is-done .done{background:color-mix(in srgb,var(--accent) 12%,transparent);border-color:var(--accent);color:var(--accent)}
p{margin:0 0 14px}
strong{font-weight:700}
code{font-family:var(--ff-mono);font-size:.9em;background:var(--code-bg);padding:1px 5px;border-radius:5px}
a.anchor{opacity:0;margin-left:8px;font-weight:400;color:var(--muted);font-size:.8em;transition:.15s}
h2:hover a.anchor,h3:hover a.anchor,h4:hover a.anchor{opacity:.7}
ul,ol{margin:0 0 14px;padding-left:24px}
li{margin:4px 0}
li::marker{color:var(--primary)}
.note{background:var(--primary-soft);border-left:3px solid var(--primary);border-radius:0 10px 10px 0;
  padding:12px 16px;margin:0 0 16px;color:var(--text)}
.note p{margin:0 0 8px;font-size:calc(var(--fs-base) * .95)}
.note p:last-child{margin-bottom:0}
pre.mono{background:var(--code-bg);border:1px solid var(--border);border-radius:10px;padding:12px 14px;
  overflow-x:auto;font-family:var(--ff-mono);font-size:13px;line-height:1.6;margin:0 0 16px;white-space:pre}
.tw{overflow-x:auto;margin:0 0 18px;border:1px solid var(--border);border-radius:10px}
table{width:100%;border-collapse:collapse;font-size:calc(var(--fs-base) * .9)}
th{background:var(--panel2);text-align:left;font-weight:700;color:var(--text);white-space:nowrap}
th,td{border-bottom:1px solid var(--border);border-right:1px solid var(--border);padding:9px 12px;vertical-align:top}
th:last-child,td:last-child{border-right:none}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:var(--panel2)}

.quiz{border:1px solid var(--border);border-radius:14px;margin:0 0 22px;overflow:hidden;background:var(--panel2)}
.quiz-label{display:flex;align-items:center;gap:8px;padding:9px 16px;font-weight:700;font-size:13px;
  color:#fff;background:linear-gradient(90deg,var(--primary),var(--accent))}
.quiz-tag{font-weight:500;font-size:11.5px;background:rgba(255,255,255,.22);padding:1px 8px;border-radius:99px}
.quiz-stem{padding:16px 18px 4px}
.quiz-stem p{margin:0 0 10px}
.quiz-stem blockquote{margin:0}
.quiz-stem .note{background:transparent;border-left:3px solid var(--border-strong);border-radius:0;
  padding:0 0 0 13px}
.quiz-stem .note p:last-child{margin-bottom:0}
.quiz-details{border-top:1px dashed var(--border-strong)}
.quiz-details>summary{cursor:pointer;padding:11px 18px;font-size:13.5px;color:var(--primary);
  font-weight:600;list-style:none;user-select:none}
.quiz-details>summary::-webkit-details-marker{display:none}
.quiz-details>summary::before{content:"▸ ";display:inline-block;transition:transform .18s}
.quiz-details[open]>summary::before{transform:rotate(90deg)}
.sum-close{display:none}
.quiz-details[open] .sum-open{display:none}
.quiz-details[open] .sum-close{display:inline}
.quiz-answer{padding:4px 18px 16px;border-top:1px dashed var(--border)}
.quiz-answer p{font-size:calc(var(--fs-base) * .96)}

mark.hl{background:var(--mark);color:inherit;border-radius:3px;padding:0 1px}
mark.hl.active{outline:2px solid var(--primary);background:var(--mark)}

#toTop{position:fixed;right:22px;bottom:24px;z-index:50;width:42px;height:42px;border-radius:50%;
  border:1px solid var(--border);background:var(--panel);color:var(--primary);font-size:17px;cursor:pointer;
  box-shadow:var(--shadow);opacity:0;pointer-events:none;transition:.2s}
#toTop.on{opacity:1;pointer-events:auto}
.pagefoot{max-width:var(--content-max);margin:0 auto;padding:0 24px 50px;color:var(--muted);font-size:12.5px}
.help{position:fixed;inset:0;z-index:90;background:rgba(10,18,30,.5);display:none;place-items:center;padding:20px}
.help.on{display:grid}
.help-card{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:22px 26px;
  max-width:440px;width:100%;box-shadow:var(--shadow)}
.help-card h3{margin:0 0 12px;color:var(--text)}
.help-card table{font-size:13px}
.help-card kbd{font-family:var(--ff-mono);border:1px solid var(--border);border-radius:5px;
  padding:1px 6px;background:var(--panel2);font-size:12px}

body.teaching .sidebar{display:none}
body.teaching .layout{grid-template-columns:minmax(0,1fr);max-width:1180px}
body.teaching .content{max-width:100%;padding:40px 56px 64px;font-size:calc(var(--fs-base) * 1.12)}
body.teaching h2{font-size:calc(var(--fs-base) * 1.75)}
body.teaching h3{font-size:calc(var(--fs-base) * 1.32)}
body.teaching .done{display:none}
.overlay{position:fixed;inset:0;background:rgba(10,18,30,.45);z-index:55;display:none}
.overlay.on{display:block}

@media (max-width:1080px){
  .layout{grid-template-columns:1fr;padding:16px}
  .sidebar{position:fixed;top:0;left:0;bottom:0;width:296px;max-height:none;z-index:58;
    background:var(--panel);border-right:1px solid var(--border);padding:14px;overflow-y:auto;
    transform:translateX(-102%);transition:transform .22s;border-radius:0}
  .sidebar.on{transform:none}
  #menuBtn{display:inline-flex}
  .content{padding:24px 20px 44px;border-radius:12px}
  .brand small{display:none}
  .searchbox{max-width:none}
}
@media (max-width:760px){
  .topbar{flex-wrap:wrap;gap:8px}
  .searchbox{order:3;flex-basis:100%;max-width:none;margin-left:0}
  .tools{margin-left:auto}
}
@media (max-width:640px){
  .searchbox kbd{display:none}
  .tools .label{display:none}
  h2{font-size:calc(var(--fs-base) * 1.34)}
  .content{padding:20px 15px 40px}
}

@media print{
  html,html[data-theme="dark"]{
    --bg:#fff;--panel:#fff;--panel2:#fafafa;--text:#000;--muted:#3a3a3a;
    --primary:#0b4a8f;--primary-soft:#eef4fb;--accent:#0a6b5f;--warn:#a63a00;
    --border:#bbb;--border-strong:#999;--code-bg:#f5f5f5;--mark:#ffe9a3;--shadow:none;
  }
  .topbar,.sidebar,#toTop,.pagefoot,.overlay,.quiz-details>summary{display:none!important}
  body{background:#fff;color:#000;font-size:11.5pt}
  .layout{display:block;padding:0;max-width:none}
  .content{box-shadow:none;border:none;border-radius:0;padding:0;max-width:none}
  .quiz{border:1px solid #999;break-inside:avoid;background:#fff}
  .quiz-label{background:none;color:#000}
  .quiz-details>div{display:block!important}
  .quiz-stem,.quiz-answer{padding:10px}
  .quiz-answer{border-top:1px dashed #999}
  .quiz-stem .note{border-left-color:#999}
  table{font-size:10pt}
  .tw{overflow:visible;border-color:#999}
  th,td{border-color:#999}
  h2,h3,h4{break-after:avoid}
  tr,li,.note,.quiz,.unit{break-inside:avoid}
  .unit-head .done{display:none}
  a.anchor{display:none}
}
"""

SCRIPT = r"""
(function(){
  var LS_P = 'study.progress.v1', LS_S = 'study.settings.v1';
  var $ = function(s,r){return (r||document).querySelector(s)};
  var $$ = function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};

  var settings = {theme:'light', fs:16, teaching:false};
  try{ Object.assign(settings, JSON.parse(localStorage.getItem(LS_S)||'{}')); }catch(e){}
  function applySettings(){
    document.documentElement.setAttribute('data-theme', settings.theme);
    document.documentElement.style.setProperty('--fs-base', settings.fs+'px');
    document.body.classList.toggle('teaching', !!settings.teaching);
    $('#themeBtn').textContent = settings.theme==='dark' ? '☀' : '☾';
    $('#teachBtn').classList.toggle('pri', !!settings.teaching);
  }
  function saveSettings(){ try{localStorage.setItem(LS_S, JSON.stringify(settings));}catch(e){} applySettings(); }
  $('#themeBtn').addEventListener('click', function(){ settings.theme = settings.theme==='dark'?'light':'dark'; saveSettings(); });
  $('#fontUp').addEventListener('click', function(){ settings.fs = Math.min(22, settings.fs+1); saveSettings(); });
  $('#fontDown').addEventListener('click', function(){ settings.fs = Math.max(13, settings.fs-1); saveSettings(); });
  $('#teachBtn').addEventListener('click', function(){ settings.teaching = !settings.teaching; saveSettings(); });

  var sidebar = $('#sidebar'), overlay = $('#overlay');
  function closeDrawer(){ sidebar.classList.remove('on'); overlay.classList.remove('on'); }
  $('#menuBtn').addEventListener('click', function(){
    if(window.innerWidth>1080){ settings.teaching=!settings.teaching; saveSettings(); return; }
    sidebar.classList.toggle('on'); overlay.classList.toggle('on', sidebar.classList.contains('on'));
  });
  overlay.addEventListener('click', closeDrawer);

  $$('.caret', sidebar).forEach(function(btn){
    btn.addEventListener('click', function(e){ e.preventDefault(); e.stopPropagation();
      btn.closest('.toc-u').classList.toggle('open'); });
  });
  $$('.toc-a', sidebar).forEach(function(a){
    a.addEventListener('click', function(e){
      e.preventDefault();
      var id = a.getAttribute('href').slice(1), el = document.getElementById(id);
      if(!el) return;
      if(el.classList.contains('unit')) el = el.querySelector('h3') || el;
      el.scrollIntoView({behavior:'smooth', block:'start'});
      try{ history.replaceState(null,'','#'+id); }catch(err){}
      if(window.innerWidth<=1080) closeDrawer();
    });
  });

  var units = $$('[data-unit]'), done = {};
  try{ done = JSON.parse(localStorage.getItem(LS_P)||'{}'); }catch(e){}
  function refreshProgress(){
    var n = units.length, d = 0;
    units.forEach(function(u){
      var k = u.getAttribute('data-unit'), isDone = !!done[k];
      var cb = u.querySelector('input[data-done]');
      if(cb) cb.checked = isDone;
      if(u.classList.contains('unit')) u.classList.toggle('is-done', isDone);
      var li = sidebar.querySelector('.toc-u[data-target="'+k+'"]');
      if(li) li.classList.toggle('done', isDone);
      if(isDone) d++;
    });
    var pct = n ? Math.round(d/n*100) : 0;
    $('#studyFill').style.width = pct+'%';
    $('#studyBar').style.width = pct+'%';
    $('#ptext').textContent = d+' / '+n+' 节（'+pct+'%）';
  }
  document.addEventListener('change', function(e){
    var cb = e.target.closest('input[data-done]');
    if(!cb) return;
    var sec = cb.closest('[data-unit]'), k = sec.getAttribute('data-unit');
    if(cb.checked) done[k]=1; else delete done[k];
    try{ localStorage.setItem(LS_P, JSON.stringify(done)); }catch(err){}
    refreshProgress();
  });
  $('#resetP').addEventListener('click', function(){
    if(!confirm('确定要清空全部学习进度吗？')) return;
    done = {}; try{ localStorage.setItem(LS_P, JSON.stringify(done)); }catch(e){} refreshProgress();
  });
  refreshProgress();

  var tocUnits = $$('.toc-u', sidebar), tocChs = $$('.toc-ch', sidebar);
  var spyTargets = units.map(function(u){ return {k:u.getAttribute('data-unit'), el:u}; });
  var ticking = false;
  function spy(){
    var y = window.scrollY + 110, best = null;
    for(var i=0;i<spyTargets.length;i++){
      var t = spyTargets[i];
      if(t.el.offsetTop <= y) best = t; else break;
    }
    tocUnits.forEach(function(li){ li.querySelector('.toc-a').classList.remove('active'); });
    tocChs.forEach(function(li){ li.querySelector('.toc-a').classList.remove('active'); });
    if(best){
      var li = sidebar.querySelector('.toc-u[data-target="'+best.k+'"]');
      if(li){
        li.querySelector('.toc-a').classList.add('active');
        li.classList.add('open');
        var ch = li.closest('.toc-ch');
        if(ch) ch.querySelector('.toc-a').classList.add('active');
        var box = sidebar.getBoundingClientRect(), r = li.getBoundingClientRect();
        if(r.top < box.top+40 || r.bottom > box.bottom-40) sidebar.scrollTop += r.top - box.top - box.height/2;
      }
    }
    $('#toTop').classList.toggle('on', window.scrollY > 500);
    ticking = false;
  }
  window.addEventListener('scroll', function(){
    if(!ticking){ ticking = true; requestAnimationFrame(spy); }
  }, {passive:true});
  spy();
  $('#toTop').addEventListener('click', function(){ window.scrollTo({top:0,behavior:'smooth'}); });

  document.addEventListener('click', function(e){
    var a = e.target.closest('a.anchor');
    if(!a) return;
    e.preventDefault();
    var url = location.origin + location.pathname + a.getAttribute('href');
    var ok = function(){ a.textContent='✓'; setTimeout(function(){a.textContent='#';},1200); };
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(url).then(ok, function(){ location.hash=a.getAttribute('href'); });
    } else { location.hash = a.getAttribute('href'); ok(); }
  });

  var input = $('#search'), snav = $('#snav'), sInfo = $('#sInfo'), marks = [], cur = -1;
  function clearMarks(){
    $$('mark.hl').forEach(function(m){
      var p = m.parentNode; p.replaceChild(document.createTextNode(m.textContent), m); p.normalize();
    });
    marks = []; cur = -1; snav.classList.remove('on');
  }
  function skipNode(node){
    var el = node.parentNode;
    while(el && el !== document.body){
      var tag = el.tagName;
      if(tag==='SCRIPT'||tag==='STYLE'||tag==='SUMMARY'||tag==='BUTTON'||tag==='MARK') return true;
      if(el.classList && (el.classList.contains('unit-head')||el.classList.contains('quiz-label')
        ||el.classList.contains('toc')||el.classList.contains('sidebar'))) return true;
      el = el.parentNode;
    }
    return false;
  }
  function runSearch(q){
    clearMarks();
    if(!q) return;
    var walker = document.createTreeWalker($('#content'), NodeFilter.SHOW_TEXT, null), nd, nodes = [];
    while((nd = walker.nextNode())){
      if(!nd.nodeValue || !nd.nodeValue.trim()) continue;
      if(nd.nodeValue.toLowerCase().indexOf(q.toLowerCase()) < 0) continue;
      if(skipNode(nd)) continue;
      nodes.push(nd);
    }
    nodes.forEach(function(node){
      var text = node.nodeValue, lower = text.toLowerCase(), ql = q.toLowerCase();
      var frag = document.createDocumentFragment(), pos = 0, idx;
      while((idx = lower.indexOf(ql, pos)) >= 0){
        if(idx > pos) frag.appendChild(document.createTextNode(text.slice(pos, idx)));
        var m = document.createElement('mark');
        m.className = 'hl'; m.textContent = text.slice(idx, idx+q.length);
        frag.appendChild(m); marks.push(m); pos = idx + q.length;
      }
      if(pos < text.length) frag.appendChild(document.createTextNode(text.slice(pos)));
      node.parentNode.replaceChild(frag, node);
    });
    cur = marks.length ? 0 : -1;
    if(cur >= 0){ marks[0].classList.add('active'); gotoMark(0, true); }
    sInfo.textContent = marks.length ? '1 / '+marks.length : '无匹配';
    snav.classList.add('on');
  }
  function gotoMark(i, smooth){
    if(!marks.length) return;
    if(marks[cur]) marks[cur].classList.remove('active');
    cur = (i + marks.length) % marks.length;
    marks[cur].classList.add('active');
    marks[cur].scrollIntoView({behavior: smooth?'smooth':'auto', block:'center'});
    sInfo.textContent = (cur+1)+' / '+marks.length;
  }
  var timer = null;
  input.addEventListener('input', function(){
    clearTimeout(timer);
    var q = input.value.trim();
    timer = setTimeout(function(){ runSearch(q); }, 180);
  });
  input.addEventListener('keydown', function(e){
    if(e.key==='Enter'){ e.preventDefault(); gotoMark(e.shiftKey ? cur-1 : cur+1); }
    if(e.key==='Escape'){ input.value=''; clearMarks(); input.blur(); }
  });
  $('#sPrev').addEventListener('click', function(){ gotoMark(cur-1); });
  $('#sNext').addEventListener('click', function(){ gotoMark(cur+1); });
  $('#sClear').addEventListener('click', function(){ input.value=''; clearMarks(); input.focus(); });

  var allOpen = false;
  $('#expandBtn').addEventListener('click', function(){
    allOpen = !allOpen;
    $$('details.quiz-details').forEach(function(d){ d.open = allOpen; });
    $('#expandBtn').textContent = allOpen ? '收起全部解析' : '展开全部解析';
  });
  window.addEventListener('beforeprint', function(){
    $$('details.quiz-details').forEach(function(d){ if(!d.dataset.was) d.dataset.was = d.open?'1':'0'; d.open = true; });
  });
  window.addEventListener('afterprint', function(){
    $$('details.quiz-details').forEach(function(d){ d.open = d.dataset.was === '1'; });
  });
  $('#printBtn').addEventListener('click', function(){
    $$('details.quiz-details').forEach(function(d){ d.open = true; });
    window.print();
  });

  var shorts = $('#shorts');
  function toggleHelp(on){ shorts.classList.toggle('on', on===undefined ? !shorts.classList.contains('on') : on); }
  $('#helpBtn').addEventListener('click', function(){ toggleHelp(); });
  shorts.addEventListener('click', function(e){ if(e.target===shorts) toggleHelp(false); });
  function stepUnit(dir){
    var y = window.scrollY + 130, c = 0;
    for(var i=0;i<units.length;i++){ if(units[i].offsetTop <= y) c = i; }
    var t = units[Math.max(0, Math.min(units.length-1, c + dir))];
    if(t) (t.querySelector('h3')||t).scrollIntoView({behavior:'smooth', block:'start'});
  }
  document.addEventListener('keydown', function(e){
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
    if(e.key === '/' && !typing){ e.preventDefault(); input.focus(); input.select(); return; }
    if(e.key === 'Escape'){ toggleHelp(false); closeDrawer(); return; }
    if(e.key === '?' && !typing){ e.preventDefault(); toggleHelp(); return; }
    if(typing) return;
    if(e.key === 'j' || e.key === 'J'){ e.preventDefault(); stepUnit(1); }
    if(e.key === 'k' || e.key === 'K'){ e.preventDefault(); stepUnit(-1); }
  });

  applySettings();
  if(location.hash && location.hash.length > 1){
    var target = document.getElementById(location.hash.slice(1));
    if(target) setTimeout(function(){
      (target.querySelector('h2,h3,h4') || target).scrollIntoView({behavior:'auto', block:'start'});
    }, 60);
  }
})();
"""

HTML_DOC = """<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s · 学习网站</title>
<meta name="description" content="%(title)s：%(subtitle)s">
<style>%(style)s</style>
</head>
<body>
<a class="sr" href="#content">跳到正文</a>

<header class="topbar">
  <button class="tbtn icon" id="menuBtn" title="目录 / 侧栏">☰</button>
  <div class="brand"><span class="logo">%(logo)s</span>
    <span>%(title)s<small>%(subtitle)s</small></span></div>

  <div class="searchbox">
    <span class="ico">🔍</span>
    <input id="search" type="search" placeholder="搜索考点、技巧、公式、关键词…" autocomplete="off">
    <kbd>/</kbd>
  </div>
  <div class="snav" id="snav">
    <span id="sInfo">0 / 0</span>
    <button id="sPrev" title="上一个（Shift+Enter）">↑</button>
    <button id="sNext" title="下一个（Enter）">↓</button>
    <button id="sClear">✕</button>
  </div>

  <div class="tools">
    %(download_link)s<button class="tbtn" id="expandBtn">展开全部解析</button>
    <button class="tbtn icon" id="printBtn" title="打印 / 导出 PDF">🖨</button>
    <button class="tbtn icon" id="fontDown" title="缩小字号">A-</button>
    <button class="tbtn icon" id="fontUp" title="放大字号">A+</button>
    <button class="tbtn icon" id="themeBtn" title="切换深色 / 浅色">☾</button>
    <button class="tbtn" id="teachBtn" title="隐藏侧栏、放大字号，适合投屏讲解"><span class="label">演示模式</span></button>
    <button class="tbtn icon" id="helpBtn" title="快捷键">?</button>
  </div>
</header>
<div class="progress-track"><div id="studyBar"></div></div>
<div class="overlay" id="overlay"></div>

<div class="layout">
  <aside class="sidebar" id="sidebar">
    <div class="side-card">
      <h4>学习进度</h4>
      <div class="pbar"><i id="studyFill"></i></div>
      <div class="pmeta"><span id="ptext">0 / 0 节</span><button id="resetP" type="button">重置</button></div>
    </div>
    <nav aria-label="章节目录">%(toc)s</nav>
  </aside>

  <main class="content" id="content">
%(body)s
  </main>
</div>

<div class="pagefoot">%(title)s · 共 %(units)d 个学习单元 · 快捷键 <kbd>?</kbd> 查看 · 进度自动保存在本机浏览器</div>
<button id="toTop" title="回到顶部">↑</button>

<div class="help" id="shorts">
  <div class="help-card">
    <h3>快捷键与使用说明</h3>
    <table>
      <tr><td><kbd>/</kbd></td><td>聚焦搜索框</td></tr>
      <tr><td><kbd>Enter</kbd> / <kbd>Shift+Enter</kbd></td><td>跳到下一个 / 上一个匹配</td></tr>
      <tr><td><kbd>Esc</kbd></td><td>清空搜索、关闭弹窗</td></tr>
      <tr><td><kbd>j</kbd> / <kbd>k</kbd></td><td>下一节 / 上一节</td></tr>
      <tr><td><kbd>?</kbd></td><td>打开本说明</td></tr>
    </table>
    <p style="font-size:13px;color:var(--muted);margin:14px 0 0">
      「已掌握」勾选与进度自动保存在浏览器本地。点击标题旁的 <b>#</b> 可复制该节链接。
    </p>
  </div>
</div>

<script>%(script)s</script>
</body>
</html>
"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
download_link = ""
if args.download:
    download_link = ('<a class="tbtn" href="%s" download>%s</a>'
                     % (html.escape(args.download, quote=True), esc(args.download_label)))
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML_DOC % {
        "title": esc(args.title), "subtitle": esc(args.subtitle), "logo": esc(args.logo),
        "style": STYLE, "toc": toc_html, "body": body_html, "units": n_units,
        "script": SCRIPT, "download_link": download_link,
    })

print("site written:", OUT)
print("bytes:", os.path.getsize(OUT), "| units:", n_units, "| chapters:", len(chapters),
      "| quiz:", body_html.count('<div class="quiz">'), "| tables:", body_html.count("<table>"))
