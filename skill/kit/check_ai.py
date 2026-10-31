#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 味扫描器：扫 Markdown 里的禁用词、公式句、长句、长段，给出分数和修改建议。

用法:
  python check_ai.py article.md
  python check_ai.py article.md --json
  python check_ai.py article.md --list
  python check_ai.py article.md --fail-over 8
"""
import argparse, json, re, sys

# severity: 5 = 元话语/硬雷区；2 = 连接词/大词/翻译腔；1 = 万能副词
SEVERE = {
    "先说": "删掉，直接从事实开始", "本文": "删掉，用'我/我们'或直接说事",
    "本篇": "删掉", "下面": "删掉", "接下来": "删掉", "本节": "删掉",
    "只做一件事": "删掉", "只问一句": "删掉", "一句话总结": "删掉",
    "综上所述": "删掉", "综上": "删掉", "总之": "删掉", "总的来说": "删掉",
    "简而言之": "删掉", "换句话说": "删掉，重新说", "也就是说": "删掉",
    "值得注意的是": "删掉", "需要指出的是": "删掉", "不难发现": "删掉",
    "显而易见": "删掉", "众所周知": "删掉", "事实上": "删掉",
    "实际上": "删掉", "从某种意义上": "删掉", "可以说": "删掉",
    "由此可见": "删掉", "归根结底": "删掉", "说到底": "删掉",
    "本质上": "换成'说白了'或删掉", "核心在于": "换成'关键是'或删",
    "关键在于": "删掉", "重点在于": "删掉", "问题在于": "删掉",
    "答案在于": "删掉",
}
MEDIUM = {
    "首先": "删掉，用 01/02/03", "其次": "删掉", "再次": "删掉",
    "一方面": "拆成两段", "另一方面": "拆成两段", "与此同时": "删掉",
    "此外": "删掉", "另外": "删掉", "然而": "删掉", "但是": "删掉",
    "因此": "删掉，句子并排", "所以": "删掉，句子并排", "于是": "删掉",
    "从而": "删掉", "进而": "删掉", "因而": "删掉", "故而": "删掉",
    "不仅如此": "删掉", "更重要的是": "删掉", "进一步": "删掉",
    "接着": "删掉", "然后": "删掉", "随后": "删掉",
    "赋能": "换成'帮/给……提供'", "抓手": "换成'办法/入口'",
    "闭环": "换成'转起来'", "生态": "换成'圈子/上下游'",
    "链路": "换成'链条/流程'", "颗粒度": "换成'细到什么程度'",
    "对齐": "换成'商量一致'", "沉淀": "换成'积累/留下'",
    "复盘": "换成'回看/总结'", "打法": "换成'做法'",
    "组合拳": "删掉", "护城河": "删掉", "底层逻辑": "换成'真正原因'",
    "长期主义": "换成'看长期'", "不确定性": "换成'说不准/风险'",
    "范式": "换成'做法/模式'", "维度": "换成'角度/方面'",
    "张力": "换成'矛盾'", "叙事": "换成'说法/故事'",
    "锚点": "换成'参照'", "体感": "换成'感受'", "水位": "换成'水平'",
    "斜率": "换成'速度'", "中枢": "换成'中心/均值'",
    "穿越周期": "换成'熬过周期'", "价值回归": "换成'跌回合理价'",
    "势能": "换成'势头'", "动能": "换成'势头'", "变量": "换成'因素'",
    "增量": "换成'新增'", "存量": "换成'现有'", "结构性": "具体说哪一块",
    "系统性": "删掉或具体说", "趋势性": "删掉", "周期性": "删掉",
    "边际": "换成'新增的/一点点'", "拐点": "换成'转折'",
    "窗口期": "换成'时间窗口'", "新常态": "删掉", "高质量发展": "删掉",
    "转型升级": "删掉", "提质增效": "删掉",
    "进行": "直接换动词", "实现": "换成'做到/涨了/跌了'",
    "具有": "换成'有'", "存在": "换成'有'", "具备": "换成'有'",
    "开展": "换成'做'", "推进": "换成'做/推'", "落实": "换成'做'",
    "构建": "换成'搭'", "打造": "换成'做'", "营造": "删掉",
    "助力": "换成'帮/拉动'", "基于": "换成'用/按'", "针对": "换成'对'",
    "关于": "删掉", "对于": "删掉", "鉴于": "删掉", "由于": "删掉",
    "为了": "删掉", "以便": "删掉",
    "在…背景下": "删掉，直接说事", "随着": "删掉，直接说时间/主体",
    "近年来": "换成具体年份", "当前": "换成具体时间", "如今": "换成具体时间",
}
LOW = {
    "显著": "换成数字", "明显": "换成数字", "大幅": "换成数字",
    "持续": "换成'连续 X 个月'", "不断": "删掉", "有效": "删掉或换'管用'",
    "充分": "删掉", "深入": "删掉", "全面": "删掉", "系统": "删掉或具体说",
    "科学": "删掉", "合理": "删掉", "精准": "删掉", "高效": "删掉",
    "稳健": "删掉", "强劲": "换成数字", "疲软": "换成数字",
    "温和": "换成数字", "严峻": "删掉", "复杂": "删掉", "多元": "删掉",
    "丰富": "删掉", "深刻": "删掉", "重大": "删掉", "关键": "删掉",
    "核心": "删掉", "重要": "删掉", "必要": "删掉",
    "毋庸置疑": "删掉", "不可否认": "删掉", "毫无疑问": "删掉",
    "可以预见": "删掉", "势必": "删掉", "将会": "删掉",
    "有望": "删掉或给条件", "或将": "删掉或给条件",
    "进一步推动": "删掉", "有效提升": "换成数字", "充分发挥": "删掉",
    "不断优化": "删掉", "持续完善": "删掉", "切实加强": "删掉",
    "深入推进": "删掉", "全面贯彻": "删掉", "落地见效": "删掉",
    "形成合力": "删掉", "协同发力": "删掉", "多点开花": "删掉",
    "稳步推进": "删掉", "有序推进": "删掉",
}
PATTERNS = [
    (r"不是[^。！？\n]{1,30}?而是", "不是……而是……对仗", "拆成两句，只留一半"),
    (r"既[^。！？\n]{1,20}?又", "既……又……", "删掉一半"),
    (r"不仅[^。！？\n]{1,20}?而且", "不仅……而且……", "删掉一半"),
    (r"一方面[^。！？\n]{1,40}?另一方面", "一方面……另一方面……", "拆成两段"),
    (r"只有[^。！？\n]{1,20}?才", "只有……才……", "直接说条件"),
    (r"只要[^。！？\n]{1,20}?就", "只要……就……", "直接说条件"),
    (r"越是[^。！？\n]{1,20}?越", "越是……越……", "删掉"),
    (r"看似[^。！？\n]{1,20}?实则", "看似……实则……", "拆成两句"),
    (r"与其[^。！？\n]{1,20}?不如", "与其……不如……", "删掉"),
]

def scan(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r":::note.*?:::", "", text, flags=re.S)
    hits = []
    for name, table, w in (("severe", SEVERE, 5), ("medium", MEDIUM, 2), ("low", LOW, 1)):
        for wd, fix in table.items():
            if "…" in wd:
                continue
            for m in re.finditer(re.escape(wd), text):
                line = text.count("\n", 0, m.start()) + 1
                ctx = text[max(0, m.start() - 18):m.end() + 18].replace("\n", " ")
                if wd == "显著" and ("统计" in ctx or "不显著" in ctx or "显著为" in ctx):
                    continue
                if wd == "中枢" and "点位中枢" in ctx:
                    continue
                hits.append({"word": wd, "level": name, "weight": w, "line": line,
                             "fix": fix, "context": ctx})
    for pat, label, fix in PATTERNS:
        for m in re.finditer(pat, text):
            line = text.count("\n", 0, m.start()) + 1
            hits.append({"word": label, "level": "pattern", "weight": 5, "line": line,
                         "fix": fix, "context": m.group(0)[:40]})
    return hits

def stats(text):
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    chars = len(re.findall(r"[\u4e00-\u9fff]", body))
    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip() and not p.strip().startswith(("#", "!"))]
    long_paras = [p for p in paras if len(p) > 180]
    sents = [s for s in re.split(r"[。！？!?]", body) if s.strip()]
    long_sents = [s for s in sents if len(s) > 60]
    return {"chars": chars, "paras": len(paras), "long_paras": len(long_paras),
            "sents": len(sents), "long_sents": len(long_sents),
            "dash": body.count("——"), "semicolon": body.count("；")}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--fail-over", type=float, default=None)
    a = ap.parse_args()
    if a.list:
        for name, table in (("SEVERE", SEVERE), ("MEDIUM", MEDIUM), ("LOW", LOW)):
            print(f"\n[{name}] " + "、".join(table.keys()))
        return
    text = open(a.md, encoding="utf-8").read()
    hits = scan(text); st = stats(text)
    score = sum(h["weight"] for h in hits) / max(1, st["chars"]) * 1000
    grade = "干净" if score < 3 else ("轻微 AI 味" if score < 8 else ("明显 AI 味" if score < 15 else "重灾区"))
    result = {"file": a.md, "score": round(score, 2), "grade": grade,
              "chars": st["chars"], "hits": len(hits),
              "long_paras": st["long_paras"], "long_sents": st["long_sents"],
              "dash": st["dash"], "semicolon": st["semicolon"],
              "top": sorted(hits, key=lambda x: -x["weight"])[:20]}
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print(f"文件: {a.md}")
        print(f"字数: {st['chars']}　AI 味分数: {score:.2f}/千字　评级: {grade}")
        print(f"命中: {len(hits)} 处　长段: {st['long_paras']}　长句: {st['long_sents']}　破折号: {st['dash']}　分号: {st['semicolon']}")
        if hits:
            print("\n高频词 / 建议：")
            freq = {}
            for h in hits:
                freq[h["word"]] = freq.get(h["word"], 0) + 1
            for w, c in sorted(freq.items(), key=lambda x: -x[1])[:15]:
                fix = next((h["fix"] for h in hits if h["word"] == w), "")
                print(f"  {w} ×{c}  → {fix}")
        print("\n最该先改的 10 处：")
        for h in result["top"][:10]:
            print(f"  L{h['line']:>4} [{h['level']}] {h['word']}  → {h['fix']}  …{h['context'].strip()}…")
    if a.fail_over is not None and score > a.fail_over:
        sys.exit(1)

if __name__ == "__main__":
    main()
