/**
 * dsh-ronge-gongzhonghao — Host half.
 *
 * Tools:
 *   - gongzhonghao_check        score a draft for AI-flavored wording
 *   - gongzhonghao_build        markdown -> self-contained WeChat HTML
 *   - gongzhonghao_install_skill install the bundled skill into ~/.dsh/skills
 */
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const PACKAGE_DIR = path.dirname(fileURLToPath(import.meta.url))
const SKILL_DIR = path.join(PACKAGE_DIR, 'skill')
const SKILL_NAME = 'ronge-gongzhonghao'

export const inject = ['tools']

const SEVERE = {
  先说: '删掉，直接从事实开始', 本文: '删掉，用"我/我们"或直接说事', 本篇: '删掉',
  下面: '删掉', 接下来: '删掉', 本节: '删掉', 只做一件事: '删掉', 只问一句: '删掉',
  一句话总结: '删掉', 综上所述: '删掉', 综上: '删掉', 总之: '删掉', 总的来说: '删掉',
  简而言之: '删掉', 换句话说: '删掉，重新说', 也就是说: '删掉', 值得注意的是: '删掉',
  需要指出的是: '删掉', 不难发现: '删掉', 显而易见: '删掉', 众所周知: '删掉',
  事实上: '删掉', 实际上: '删掉', 从某种意义上: '删掉', 可以说: '删掉',
  由此可见: '删掉', 归根结底: '删掉', 说到底: '删掉', 本质上: '换成"说白了"或删掉',
  核心在于: '换成"关键是"或删掉', 关键在于: '删掉', 重点在于: '删掉', 问题在于: '删掉',
}

const MEDIUM = {
  首先: '删掉，用 01/02/03', 其次: '删掉', 再次: '删掉', 一方面: '拆成两段', 另一方面: '拆成两段',
  与此同时: '删掉', 此外: '删掉', 另外: '删掉', 然而: '删掉', 但是: '删掉', 因此: '删掉，句子并排',
  所以: '删掉，句子并排', 于是: '删掉', 从而: '删掉', 进而: '删掉', 因而: '删掉', 故而: '删掉',
  不仅如此: '删掉', 更重要的是: '删掉', 进一步: '删掉', 接着: '删掉', 然后: '删掉', 随后: '删掉',
  赋能: '换成"帮/给……提供"', 抓手: '换成"办法/入口"', 闭环: '换成"转起来"', 生态: '换成"圈子/上下游"',
  链路: '换成"链条/流程"', 颗粒度: '换成"细到什么程度"', 对齐: '换成"商量一致"', 沉淀: '换成"积累/留下"',
  复盘: '换成"回看/总结"', 打法: '换成"做法"', 组合拳: '删掉', 护城河: '删掉', 底层逻辑: '换成"真正原因"',
  长期主义: '换成"看长期"', 不确定性: '换成"说不准/风险"', 范式: '换成"做法/模式"', 维度: '换成"角度/方面"',
  张力: '换成"矛盾"', 叙事: '换成"说法/故事"', 锚点: '换成"参照"', 体感: '换成"感受"', 水位: '换成"水平"',
  斜率: '换成"速度"', 中枢: '换成"中心/均值"', 穿越周期: '换成"熬过周期"', 价值回归: '换成"跌回合理价"',
  势能: '换成"势头"', 动能: '换成"势头"', 变量: '换成"因素"', 增量: '换成"新增"', 存量: '换成"现有"',
  结构性: '具体说哪一块', 系统性: '删掉或具体说', 趋势性: '删掉', 周期性: '删掉', 边际: '换成"新增的"',
  拐点: '换成"转折"', 窗口期: '换成"时间窗口"', 新常态: '删掉', 高质量发展: '删掉', 转型升级: '删掉',
  进行: '直接换动词', 实现: '换成"做到/涨了/跌了"', 具有: '换成"有"', 存在: '换成"有"', 具备: '换成"有"',
  开展: '换成"做"', 推进: '换成"做/推"', 落实: '换成"做"', 构建: '换成"搭"', 打造: '换成"做"',
  营造: '删掉', 助力: '换成"帮/拉动"', 基于: '换成"用/按"', 针对: '换成"对"', 关于: '删掉',
  对于: '删掉', 鉴于: '删掉', 由于: '删掉', 为了: '删掉', 以便: '删掉', 随着: '删掉，直接说时间/主体',
  近年来: '换成具体年份', 当前: '换成具体时间', 如今: '换成具体时间',
}

const LOW = {
  显著: '换成数字', 明显: '换成数字', 大幅: '换成数字', 持续: '换成"连续 X 个月"', 不断: '删掉',
  有效: '删掉或换"管用"', 充分: '删掉', 深入: '删掉', 全面: '删掉', 系统: '删掉或具体说',
  科学: '删掉', 合理: '删掉', 精准: '删掉', 高效: '删掉', 稳健: '删掉', 强劲: '换成数字',
  疲软: '换成数字', 温和: '换成数字', 严峻: '删掉', 复杂: '删掉', 多元: '删掉', 丰富: '删掉',
  深刻: '删掉', 重大: '删掉', 关键: '删掉', 核心: '删掉', 重要: '删掉', 必要: '删掉',
  毋庸置疑: '删掉', 不可否认: '删掉', 毫无疑问: '删掉', 可以预见: '删掉', 势必: '删掉',
  将会: '删掉', 有望: '删掉或给条件', 或将: '删掉或给条件', 进一步推动: '删掉', 有效提升: '换成数字',
  充分发挥: '删掉', 不断优化: '删掉', 持续完善: '删掉', 切实加强: '删掉', 深入推进: '删掉',
  全面贯彻: '删掉', 落地见效: '删掉', 形成合力: '删掉', 协同发力: '删掉', 多点开花: '删掉',
  稳步推进: '删掉', 有序推进: '删掉',
}

const PATTERNS = [
  [/不是[^。！？\n]{1,30}?而是/g, '不是……而是……对仗', '拆成两句，只留一半', 5],
  [/既[^。！？\n]{1,20}?又/g, '既……又……', '删掉一半', 5],
  [/不仅[^。！？\n]{1,20}?而且/g, '不仅……而且……', '删掉一半', 5],
  [/一方面[^。！？\n]{1,40}?另一方面/g, '一方面……另一方面……', '拆成两段', 5],
  [/只有[^。！？\n]{1,20}?才/g, '只有……才……', '直接说条件', 5],
  [/只要[^。！？\n]{1,20}?就/g, '只要……就……', '直接说条件', 5],
  [/看似[^。！？\n]{1,20}?实则/g, '看似……实则……', '拆成两句', 5],
  [/与其[^。！？\n]{1,20}?不如/g, '与其……不如……', '删掉', 5],
  [/——/g, '破折号', '每 500 字不超过 1 个', 1],
]

function stripBlocks(text) {
  return String(text || '')
    .replace(/```[\s\S]*?```/g, '')
    .replace(/:::note[\s\S]*?:::/g, '')
    .replace(/免责声明[\s\S]*$/g, '')
}

export function scanText(raw) {
  const text = stripBlocks(raw)
  const hits = []
  const add = (word, level, weight, fix, idx) => {
    const line = text.slice(0, idx).split('\n').length
    const ctx = text.slice(Math.max(0, idx - 16), idx + word.length + 16).replace(/\n/g, ' ')
    hits.push({ word, level, weight, line, fix, context: ctx })
  }
  for (const [table, level, weight] of [[SEVERE, 'severe', 5], [MEDIUM, 'medium', 2], [LOW, 'low', 1]]) {
    for (const [word, fix] of Object.entries(table)) {
      if (word.includes('…')) continue
      let idx = text.indexOf(word)
      while (idx !== -1) {
        if (word === '显著' && /统计|不显著/.test(text.slice(Math.max(0, idx - 6), idx + 8))) { idx = text.indexOf(word, idx + word.length); continue }
        if (word === '中枢' && text.slice(Math.max(0, idx - 4), idx + 4).includes('点位中枢')) { idx = text.indexOf(word, idx + word.length); continue }
        add(word, level, weight, fix, idx)
        idx = text.indexOf(word, idx + word.length)
      }
    }
  }
  for (const [re, label, fix, weight] of PATTERNS) {
    re.lastIndex = 0
    let m
    while ((m = re.exec(text))) {
      add(label, 'pattern', weight, fix, m.index)
      if (m.index === re.lastIndex) re.lastIndex += 1
    }
  }
  const chars = (text.match(/[\u4e00-\u9fff]/g) || []).length
  const score = Math.round((hits.reduce((s, h) => s + h.weight, 0) / Math.max(1, chars)) * 1000 * 100) / 100
  const grade = score < 3 ? '干净' : score < 8 ? '轻微 AI 味' : score < 15 ? '明显 AI 味' : '重灾区'
  const freq = {}
  for (const h of hits) freq[h.word] = (freq[h.word] || 0) + 1
  const top = hits.slice().sort((a, b) => b.weight - a.weight || a.line - b.line).slice(0, 20)
  return { chars, score, grade, hits: hits.length, top, freq }
}

function toolText(value) {
  return JSON.stringify(value, null, 2)
}

function registerTools(ctx) {
  const tools = ctx.get ? ctx.get('tools') : ctx.tools
  if (!tools || typeof tools.register !== 'function') return []
  const disposers = []

  disposers.push(tools.register({
    name: 'gongzhonghao_check',
    description:
      'Score a Chinese WeChat article draft for AI-flavored wording. Returns score per 1000 Chinese chars, grade, hit words with line/context and a replacement hint. Use before publishing; target below 3.',
    parameters: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Draft text. Ignored when path is set.' },
        path: { type: 'string', description: 'Optional path to a markdown file.' },
      },
      additionalProperties: false,
    },
    output: { schema: { type: 'object', additionalProperties: true }, render: (args, value) => toolText(value) },
    async execute(args = {}) {
      let text = String(args.text || '')
      const p = String(args.path || '')
      if (p) text = fs.readFileSync(p, 'utf8')
      if (!text.trim()) return { ok: false, error: 'text or path is required' }
      const result = scanText(text)
      return { ok: true, ...result, top: result.top.slice(0, 15) }
    },
  }))

  disposers.push(tools.register({
    name: 'gongzhonghao_build',
    description:
      'Build a self-contained WeChat HTML from a markdown draft that follows ronge-gongzhonghao conventions (==highlight==, :::lead, :::note, ## 01｜title). Requires python3.',
    parameters: {
      type: 'object',
      properties: {
        mdPath: { type: 'string', description: 'Markdown file path.' },
        outPath: { type: 'string', description: 'Optional output HTML path. Defaults to <md>.html.' },
        brand: { type: 'string', description: 'Optional brand label, default "研 究 笔 记".' },
      },
      required: ['mdPath'],
      additionalProperties: false,
    },
    output: { schema: { type: 'object', additionalProperties: true }, render: (args, value) => toolText(value) },
    async execute(args = {}) {
      const md = path.resolve(String(args.mdPath || ''))
      if (!fs.existsSync(md)) return { ok: false, error: `markdown not found: ${md}` }
      const out = path.resolve(String(args.outPath || md.replace(/\.md$/i, '.html')))
      const py = process.env.PYTHON || 'python3'
      const script = path.join(SKILL_DIR, 'kit', 'build_wx.py')
      const cmd = [script, '--md', md, '--out', out]
      if (args.brand) cmd.push('--brand', String(args.brand))
      try {
        const stdout = execFileSync(py, cmd, { encoding: 'utf8', timeout: 120000 })
        return { ok: true, out, bytes: fs.statSync(out).size, log: stdout.trim().slice(-500) }
      } catch (e) {
        return { ok: false, error: String(e.message || e), hint: 'Need Python 3. Run `python3 --version`; or use the skill kit manually.' }
      }
    },
  }))

  disposers.push(tools.register({
    name: 'gongzhonghao_install_skill',
    description:
      'Install the bundled ronge-gongzhonghao skill into ~/.dsh/skills (or DSH_SKILLS_DIR) so it appears in the skill catalog. Idempotent unless force is true.',
    parameters: {
      type: 'object',
      properties: {
        force: { type: 'boolean', description: 'Overwrite an existing installation.' },
      },
      additionalProperties: false,
    },
    output: { schema: { type: 'object', additionalProperties: true }, render: (args, value) => toolText(value) },
    async execute(args = {}) {
      const base = process.env.DSH_SKILLS_DIR || path.join(os.homedir(), '.dsh', 'skills')
      const dest = path.join(base, SKILL_NAME)
      if (fs.existsSync(dest) && !args.force) {
        return { ok: true, installed: false, path: dest, note: 'already installed; set force=true to overwrite' }
      }
      fs.mkdirSync(path.dirname(dest), { recursive: true })
      fs.rmSync(dest, { recursive: true, force: true })
      fs.cpSync(SKILL_DIR, dest, { recursive: true })
      return { ok: true, installed: true, path: dest, note: 'restart DSH or reload skills to pick it up' }
    },
  }))

  return disposers
}

export function apply(ctx) {
  const disposers = registerTools(ctx)
  const dispose = () => {
    for (const d of disposers) {
      try { if (typeof d === 'function') d() } catch { /* noop */ }
    }
  }
  if (ctx && typeof ctx.effect === 'function') {
    ctx.effect(() => dispose)
  }
  return dispose
}
