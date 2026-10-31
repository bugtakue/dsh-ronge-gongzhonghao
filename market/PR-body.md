### Add `bugtakue/dsh-ronge-gongzhonghao`

A DSH plugin + bundled skill for Chinese WeChat long-form writing.

**What it does**

- `gongzhonghao_check` — AI-flavor linter: score per 1000 Chinese chars, hit words, line numbers, replacement hints. Target < 3.
- `gongzhonghao_build` — Markdown → self-contained WeChat-safe HTML (inline styles, base64 images, `==highlight==`, `:::lead`, `:::note`).
- `gongzhonghao_install_skill` — installs the bundled `ronge-gongzhonghao` skill into `~/.dsh/skills`.
- Bundled skill: writing rules, ~200-entry banned-word list, 20 before/after examples, 750px mobile figure system, WeChat paste pitfalls.

**Manifest**

- `package.json` declares `dsh.bundle.patch: ./cordis.patch.yml`; patch file is at the repo root.
- `dsh-plugin` topic is set.
- npm package not published yet → browse-only; install from GitHub with `dsh plugin add github:bugtakue/dsh-ronge-gongzhonghao`.

**Related**

- Standalone skill repo: https://github.com/bugtakue/ronge-gongzhonghao
- Already listed in 1024Store catalog (PR imsai-sh/awesome-deepseek-harness-plugins#772).
