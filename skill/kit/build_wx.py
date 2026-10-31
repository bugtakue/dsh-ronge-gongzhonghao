#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown -> 微信公众号自包含 HTML（内联样式 + base64 图）。

用法:
  python build_wx.py --md article.md --out article.html
  python build_wx.py --md article.md --out article.html --preview preview.png

Markdown 约定:
  # 标题
  副标题（紧跟标题后的第一行非空、非 # 行）
  meta 行（再下一行，如 "数据截至 2026-10-30 · 约 2800 字"）
  ## 01｜小节标题
  ### 子标题
  - 列表 / 1. 列表
  > 引文
  ![图注](figs/a.png)
  :::lead   ... :::   结论卡
  :::note   ... :::   免责声明
  ==高亮==  **加粗**
"""
import argparse, base64, html, os, re, subprocess, sys

# ---------- 主题 ----------
INK = "#1F2723"; GREEN = "#23453A"; GOLD = "#B58B3E"; RED = "#A6472E"
GREY = "#6E6A61"; CREAM = "#FBF3DA"; SAND = "#E4D8BF"; HL = "#F5E4A8"
FONT = "font-family:'STFangsong','FangSong_GB2312','FangSong',serif;"
SERIF = "font-family:'Songti SC','STSong','Noto Serif CJK SC',serif;"
NUM = "font-family:Georgia,'Times New Roman',serif;font-variant-numeric:tabular-nums;"

def esc(t):
    return html.escape(t, quote=False)

def inline(t):
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r'<strong style="color:%s;font-weight:700;">\1</strong>' % GREEN, t)
    t = re.sub(r"`([^`]+)`", r'<code style="background:#F1EFE8;padding:1px 5px;font-size:14px;">\1</code>', t)
    t = re.sub(r"==(.+?)==", r'<span style="background-color:%s;color:%s;font-weight:700;padding:0 3px;">\1</span>' % (HL, INK), t)
    return t

def P(t):
    return f'<p style="{FONT}margin:0 0 22px;font-size:17px;line-height:1.95;color:#3A3A3A;letter-spacing:.3px;">{inline(t)}</p>'

def section(num, title):
    return f'''<section style="margin:52px 0 24px;">
<p style="margin:0 0 4px;font-family:Georgia,serif;font-size:15px;color:{GOLD};letter-spacing:3px;">— {num} —</p>
<p style="margin:0 0 9px;{SERIF}font-size:23px;font-weight:700;color:{INK};line-height:1.45;">{inline(title)}</p>
<p style="margin:0;height:1px;background:{SAND};"></p></section>'''

def leadcard(lines):
    ps = "".join(f'<p style="margin:0 0 10px;{FONT}font-size:16px;line-height:1.85;color:#2A2A2A;font-weight:600;">{inline(x)}</p>' for x in lines)
    return f'''<section style="margin:22px 0 30px;padding:18px 18px 8px;background:{CREAM};">
<p style="margin:0 0 12px;{FONT}font-size:11px;letter-spacing:4px;color:#8A6A22;">本 文 结 论</p>{ps}</section>'''

def notecard(lines):
    return f'''<section style="margin:26px 0;padding:14px 0 0;border-top:1px solid {SAND};">
<p style="margin:0;{FONT}font-size:13px;color:{GREY};line-height:1.85;">{inline(" ".join(lines))}</p></section>'''

def quote(t):
    return f'''<section style="margin:30px 0;padding:16px 18px;background:{CREAM};">
<p style="margin:0;{SERIF}font-size:19px;line-height:1.85;color:#2A2A2A;font-weight:600;">{inline(t)}</p></section>'''

def bullets(items, ordered=False):
    tag = "ol" if ordered else "ul"
    lis = "".join(f'<li style="margin:0 0 9px;">{inline(x)}</li>' for x in items)
    return f'<{tag} style="{FONT}margin:0 0 24px;padding-left:22px;color:#3A3A3A;font-size:17px;line-height:1.9;">{lis}</{tag}>'

def img_tag(path, caption, base_dir):
    full = path if os.path.isabs(path) else os.path.join(base_dir, path)
    if not os.path.exists(full):
        return f'<p style="color:#A6472E;">[缺图: {esc(path)}]</p>'
    with open(full, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = "png" if full.lower().endswith(".png") else ("jpeg" if full.lower().endswith((".jpg", ".jpeg")) else "png")
    cap = f'<p style="margin:9px 0 4px;{FONT}font-size:12px;color:{GREY};line-height:1.7;">{esc(caption)}</p>' if caption else ""
    return f'<section style="margin:30px 0;"><img src="data:image/{ext};base64,{b64}" style="width:100%;display:block;"/>{cap}</section>'

def parse(md, base_dir, brand="研 究 笔 记"):
    lines = md.split("\n"); out = []; i = 0; sec_count = 0
    title = subtitle = meta = None
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip(); i = 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and not lines[i].startswith("#"):
        subtitle = lines[i].strip(); i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and not lines[i].startswith("#"):
        meta = lines[i].strip(); i += 1
    if title:
        sub = f'<p style="margin:0;{FONT}font-size:13px;color:{GREY};line-height:1.8;">{inline(subtitle)}</p>' if subtitle else ""
        met = f'<p style="margin:14px 0 0;{FONT}font-size:12px;color:{GREY};">{inline(meta)}</p>' if meta else ""
        out.append(f'''<section style="margin:0 0 26px;padding:2px 0 0;">
<p style="margin:0 0 12px;{FONT}font-size:11px;letter-spacing:6px;color:{GOLD};">{brand}</p>
<p style="margin:0 0 12px;{SERIF}font-size:22px;font-weight:700;color:{INK};line-height:1.55;">{inline(title)}</p>
{sub}</section>{met}''')
    while i < len(lines):
        s = lines[i].rstrip()
        if not s:
            i += 1; continue
        m = re.match(r"^:::(lead|note)$", s)
        if m:
            kind = m.group(1); buf = []; i += 1
            while i < len(lines) and lines[i].strip() != ":::":
                if lines[i].strip(): buf.append(lines[i].strip())
                i += 1
            i += 1
            out.append((leadcard if kind == "lead" else notecard)(buf)); continue
        m = re.match(r"^##\s+(\d{2})｜\s*(.*)$", s)
        if m:
            sec_count += 1
            if sec_count > 1:
                out.append(f'<div style="margin:46px 0;"><span style="display:inline-block;width:36px;height:1px;background:{GOLD};opacity:.7;"></span></div>')
            out.append(section(m.group(1), m.group(2))); i += 1; continue
        m = re.match(r"^##\s+(.*)$", s)
        if m:
            sec_count += 1
            if sec_count > 1:
                out.append(f'<div style="margin:46px 0;"><span style="display:inline-block;width:36px;height:1px;background:{GOLD};opacity:.7;"></span></div>')
            out.append(f'<p style="margin:0 0 9px;{SERIF}font-size:22px;font-weight:700;color:{INK};">{inline(m.group(1))}</p>'); i += 1; continue
        if s.startswith("### "):
            out.append(f'<p style="margin:26px 0 12px;{FONT}font-size:17px;font-weight:700;color:{INK};">{inline(s[4:].strip())}</p>'); i += 1; continue
        if s.startswith("> "):
            out.append(quote(s[2:].strip())); i += 1; continue
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", s)
        if m:
            out.append(img_tag(m.group(2), m.group(1), base_dir)); i += 1; continue
        if re.match(r"^\d+\.\s", s):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip())); i += 1
            out.append(bullets(items, True)); continue
        if s.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:]); i += 1
            out.append(bullets(items)); continue
        buf = [s]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(## |### |!\[|> |- |\d+\.\s|:::)", lines[i].strip()):
            buf.append(lines[i].strip()); i += 1
        out.append(P(" ".join(buf)))
    return "\n".join(out)

def fix_align(doc):
    def _f(m):
        st = m.group(1)
        if "text-align" in st:
            return m.group(0)
        return f'style="text-align:left;{st}"'
    return re.sub(r'style="([^"]*)"', _f, doc)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--preview")
    ap.add_argument("--width", type=int, default=677)
    ap.add_argument("--brand", default="研 究 笔 记")
    a = ap.parse_args()
    base_dir = os.path.dirname(os.path.abspath(a.md))
    md = open(a.md, encoding="utf-8").read()
    body = parse(md, base_dir, a.brand)
    doc = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(re.search(r"^#\s+(.+)$", md, re.M).group(1) if re.search(r"^#\s+(.+)$", md, re.M) else "公众号文章")}</title>
<style>img{{max-width:100%;}} body{{margin:0;background:#fff;}}</style></head><body>
<article style="max-width:{a.width}px;margin:0 auto;padding:22px 20px 54px;background:#fff;">
{body}
<p style="margin:42px 0 0;text-align:center;{FONT}font-size:11px;color:#B0B4B8;letter-spacing:2px;">— 全文完 —</p>
</article></body></html>'''
    doc = fix_align(doc)
    open(a.out, "w", encoding="utf-8").write(doc)
    print("html:", a.out, round(os.path.getsize(a.out) / 1024 / 1024, 2), "MB")
    if a.preview:
        chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome):
            subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                            "--screenshot=" + a.preview, "--window-size=750,16000", "--virtual-time-budget=15000",
                            "file://" + os.path.abspath(a.out)], capture_output=True, timeout=180)
            print("preview:", a.preview)
        else:
            print("no Chrome, skip preview")

if __name__ == "__main__":
    main()
