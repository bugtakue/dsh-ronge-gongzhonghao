# dsh-ronge-gongzhonghao

> DeepSeek Harness 插件 + 内置技能：**公众号长文写作、去 AI 味扫描、自包含 HTML 生成**。

Repo: https://github.com/bugtakue/dsh-ronge-gongzhonghao
Skill repo: https://github.com/bugtakue/ronge-gongzhonghao

## 它做什么

装一个插件，得到三个工具：

| 工具 | 作用 |
|---|---|
| `gongzhonghao_check` | 给中文草稿打"AI 味分数"，列出命中词、行号、上下文、替换建议 |
| `gongzhonghao_build` | 把 Markdown 生成自包含微信公众号 HTML（内联样式 + base64 图） |
| `gongzhonghao_install_skill` | 把内置的 `ronge-gongzhonghao` 技能装进 `~/.dsh/skills` |

内置技能就是 [ronge-gongzhonghao](https://github.com/bugtakue/ronge-gongzhonghao)：禁用词表、写法手册、排版规范、微信踩坑、构建器。

## 安装

从 GitHub 安装（`dsh` CLI 或 DSH 插件页）：

```bash
dsh plugin --profile web add github:bugtakue/dsh-ronge-gongzhonghao
# 桌面端
dsh plugin --profile desktop add github:bugtakue/dsh-ronge-gongzhonghao
```

装完后在会话里让 Agent 先装技能：

```text
调用 gongzhonghao_install_skill
```

然后就能用 `ronge-gongzhonghao` 技能了。

## 用法

### 扫 AI 味

```text
gongzhonghao_check({ path: "article.md" })
```

返回：

```json
{
  "ok": true,
  "score": 19.11,
  "grade": "重灾区",
  "hits": 9,
  "top": [
    { "word": "本文", "line": 129, "fix": "删掉，用'我/我们'或直接说事" }
  ]
}
```

目标：**分数 < 3/千字**。

### 生成公众号 HTML

```text
gongzhonghao_build({ mdPath: "article.md", outPath: "article.html", brand: "循 济 研 究" })
```

Markdown 约定见 [skill/SKILL.md](skill/SKILL.md)：

- `==文字==` → 淡金高亮
- `:::lead` → 开头结论卡
- `:::note` → 免责声明
- `## 01｜标题` → 金色编号小节

生成后用 Chrome 打开 HTML，全选复制，粘进公众号后台。

### 安装技能

```text
gongzhonghao_install_skill({ force: false })
```

装到 `~/.dsh/skills/ronge-gongzhonghao`（可用 `DSH_SKILLS_DIR` 覆盖）。

## 依赖

- Node.js ≥ 20（插件本身无依赖）；
- `gongzhonghao_build` 需要 `python3`（构建器只用标准库）；
- 预览图需要 Chrome（可选）。

## 文件

```
index.js              插件主逻辑（tools 注册）
cordis.patch.yml      DSH bundle patch
skill/                内置技能（SKILL.md / references / kit / examples）
screenshots.json      商店截图
docs/screenshot.png
package.json
```

## License

MIT © 2026 bugtakue
