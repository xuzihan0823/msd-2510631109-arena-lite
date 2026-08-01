#!/usr/bin/env python3
"""生成 LaunchSpec AI 答辩 PPT（2510631109-launchspec-ai）。

内容全部来自仓库内已落盘的真实证据，不含推测数据。
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

OUT = Path(__file__).resolve().parent.parent / "submissions" / "2510631109-launchspec-ai-defense.pptx"

INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x6B, 0x6B, 0x6B)
ACCENT = RGBColor(0x1B, 0x4D, 0xE4)
WARN = RGBColor(0xB4, 0x54, 0x09)
BG = RGBColor(0xFA, 0xFA, 0xF8)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def slide(bg=BG):
    s = prs.slides.add_slide(BLANK)
    bgshape = s.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
    bgshape.fill.solid()
    bgshape.fill.fore_color.rgb = bg
    bgshape.line.fill.background()
    bgshape.shadow.inherit = False
    s.shapes._spTree.remove(bgshape._element)
    s.shapes._spTree.insert(2, bgshape._element)
    return s


def textbox(s, left, top, width, height):
    tb = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    return tf


def para(tf, text, size=16, bold=False, color=INK, space_after=8, first=False,
         align=PP_ALIGN.LEFT, font="Helvetica Neue"):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.text = text
    p.alignment = align
    p.space_after = Pt(space_after)
    for run in p.runs:
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.name = font
    return p


def rule(s, top, left=0.9, width=11.5, color=ACCENT, height_pt=3):
    bar = s.shapes.add_shape(1, Inches(left), Inches(top), Inches(width), Pt(height_pt))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()
    bar.shadow.inherit = False
    return bar


def header(s, kicker, title):
    tf = textbox(s, 0.9, 0.55, 11.5, 1.4)
    para(tf, kicker, size=13, bold=True, color=ACCENT, space_after=4, first=True)
    para(tf, title, size=34, bold=True, color=INK, space_after=0)
    rule(s, 1.95)


def notes(s, text):
    s.notes_slide.notes_text_frame.text = text


def bullets(s, items, top=2.35, left=0.95, width=11.4, size=17, gap=13):
    tf = textbox(s, left, top, width, 4.5)
    for i, item in enumerate(items):
        if isinstance(item, tuple):
            label, body = item
            p = para(tf, f"{label}   {body}", size=size, space_after=gap, first=(i == 0))
            p.runs[0].font.bold = True
        else:
            para(tf, item, size=size, space_after=gap, first=(i == 0))
    return tf


def table(s, rows, left=0.95, top=2.35, width=11.4, height=3.6, col_widths=None,
          size=13, header_bold=True):
    shape = s.shapes.add_table(len(rows), len(rows[0]), Inches(left), Inches(top),
                               Inches(width), Inches(height))
    tbl = shape.table
    if col_widths:
        total = sum(col_widths)
        for i, w in enumerate(col_widths):
            tbl.columns[i].width = Emu(int(Inches(width) * w / total))
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = str(val)
            cell.margin_left = Inches(0.10)
            cell.margin_right = Inches(0.10)
            cell.margin_top = Inches(0.045)
            cell.margin_bottom = Inches(0.045)
            for p in cell.text_frame.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(size)
                    run.font.name = "Helvetica Neue"
                    run.font.color.rgb = INK if r else RGBColor(0xFF, 0xFF, 0xFF)
                    run.font.bold = bool(r == 0 and header_bold)
    return tbl


# ---------------------------------------------------------------- 1 封面
s = slide()
tf = textbox(s, 0.95, 2.15, 11.4, 3.0)
para(tf, "2510631109-launchspec-ai", size=15, bold=True, color=ACCENT,
     space_after=14, first=True)
para(tf, "LaunchSpec AI", size=56, bold=True, space_after=10)
para(tf, "把产品想法转化为可编辑、可审查、可导出的 MVP 项目蓝图",
     size=21, color=MUTED, space_after=26)
rule(s, 4.72, width=3.2)
tf2 = textbox(s, 0.95, 5.05, 11.4, 1.2)
para(tf2, "短学期实践 · 提交期自选项目答辩　|　徐驰宇　学号 2510631109",
     size=15, color=MUTED, space_after=4, first=True)
para(tf2, "Next.js 16 · TypeScript · 本地 JSON 存储　|　2026-08-02", size=13, color=MUTED)
notes(s, "自我介绍与项目一句话定位。强调这是提交期自选项目，与集中期跟练的 arena-lite "
         "在用户、场景、接口和技术栈上完全不同。控制在 30 秒内进入正题。")

# ---------------------------------------------------------------- 2 问题与价值
s = slide()
header(s, "01　问题与价值", "为什么需要 LaunchSpec AI")
bullets(s, [
    ("痛点", "产品想法分散在聊天记录、口头沟通和临时笔记里，团队以为理解一致，实际返工。"),
    ("现有 AI 的不足", "直接问模型会得到一段不可测试的长文，缺少范围、验收标准和风险约束。"),
    ("我们的做法", "把生成结果固定为可编辑、可验证的结构：目标用户、问题、MVP 范围、非目标、"
                   "验收标准、风险、架构、AI 边界共 8 个板块。"),
    ("目标用户", "创业团队负责人、外包项目经理、需要快速对齐范围的学生项目组。"),
    ("成功指标", "5 分钟内完成创建 → 生成 → 编辑 → 审查 → 导出，产出不含占位符的方案草案。"),
], top=2.45, gap=17)
tf = textbox(s, 0.95, 6.05, 11.4, 0.8)
para(tf, "核心立场：AI 给草案，人做决策。", size=19, bold=True, color=ACCENT, first=True)
notes(s, "先讲痛点再讲方案。关键差异点是『结构化』——不是让 AI 写得更长，而是逼它输出可被验证的结构。"
         "最后一句是全项目的价值主张，也是 AI 边界的出发点。")

# ---------------------------------------------------------------- 3 系统架构
s = slide()
header(s, "02　系统架构", "分层与单一校验点")
tf = textbox(s, 0.95, 2.3, 5.6, 4.3)
para(tf, "浏览器 React 工作台", size=17, bold=True, space_after=6, first=True)
para(tf, "项目列表 · 蓝图编辑器 · 审查面板", size=13, color=MUTED, space_after=14)
para(tf, "↓", size=15, color=ACCENT, space_after=14)
para(tf, "Next.js Route Handlers（Node runtime）", size=17, bold=True, space_after=6)
para(tf, "校验与错误映射 → repository → provider adapter\n→ review engine → exporter",
     size=13, color=MUTED, space_after=14)
para(tf, "↓", size=15, color=ACCENT, space_after=14)
para(tf, "data/launchspec.json", size=17, bold=True, space_after=6)
para(tf, "临时文件 + rename 原子替换", size=13, color=MUTED)

tf = textbox(s, 6.9, 2.3, 5.4, 4.3)
para(tf, "关键设计约束", size=17, bold=True, color=ACCENT, space_after=12, first=True)
para(tf, "validation.ts 是输入与模型 JSON 的唯一结构校验点。", size=15, bold=True, space_after=10)
para(tf, "无论 demo 还是真实模型，返回内容都必须通过同一份 validateBlueprint 才能入库——"
         "真实模型的不确定输出无法绕过结构约束。", size=14, color=MUTED, space_after=18)
para(tf, "8 条路由", size=15, bold=True, space_after=8)
para(tf, "/api/health\n/api/projects\n/api/projects/[id]\n/api/projects/[id]/generate\n"
         "/api/projects/[id]/review\n/api/projects/[id]/export", size=13, color=MUTED)
notes(s, "架构讲三层就够。真正要强调的是右侧：单一校验点。这是回答『模型输出不可控怎么办』的核心答案——"
         "不是相信模型，而是让所有 provider 走同一道校验闸门。")

# ---------------------------------------------------------------- 4 演示路径
s = slide()
header(s, "03　演示路径", "五步最小闭环，每步都可验证")
table(s, [
    ["步骤", "操作", "接口", "预期"],
    ["1", "输入脱敏产品想法，创建项目", "POST /api/projects", "201 + 项目 ID"],
    ["2", "生成结构化蓝图", "POST /generate", "200 + 8 个板块"],
    ["3", "编辑一个字段并保存", "PUT /api/projects/{id}", "200，旧审查被清除"],
    ["4", "刷新页面验证持久化", "GET /api/projects/{id}", "200，修改仍在"],
    ["5", "执行审查", "POST /review", "200 + ready/needs-revision"],
    ["6", "导出 Markdown", "GET /export", "200 + text/markdown"],
], top=2.4, height=3.5, col_widths=[0.7, 4.2, 3.6, 3.5], size=14)
tf = textbox(s, 0.95, 6.15, 11.4, 0.8)
para(tf, "启动：npm install → npm run dev → http://127.0.0.1:3000",
     size=15, bold=True, color=ACCENT, first=True)
para(tf, "现场演示使用 demo provider 保证确定性；真实模型证据另见 evidence/real-ai-2026-07-22/",
     size=13, color=MUTED)
notes(s, "演示时按表格顺序走。第 3、4 步是重点：证明『人可以改 AI 的结果，并且改动会被保留』。"
         "如果现场网络不稳，用 demo provider 演示，真实模型结果用证据页说明。")

# ---------------------------------------------------------------- 5 AI 使用边界
s = slide()
header(s, "04　AI 使用边界", "三种 provider，一道校验，失败不伪装")
tf = textbox(s, 0.95, 2.35, 5.55, 4.2)
para(tf, "provider 分层", size=16, bold=True, color=ACCENT, space_after=11, first=True)
para(tf, "demo　确定性实现，服务于测试与离线演示。UI 与 API 均标识其非真实模型性质。",
     size=14, space_after=11)
para(tf, "openai-compatible　从 .env.local 读取 base URL / key / 模型名，调用 /chat/completions。",
     size=14, space_after=11)
para(tf, "anthropic-compatible　运行时读取本机 Claude Code profile，调用 /v1/messages，"
         "token 不复制进项目。", size=14, space_after=0)

tf = textbox(s, 6.85, 2.35, 5.5, 4.2)
para(tf, "失败策略", size=16, bold=True, color=WARN, space_after=11, first=True)
para(tf, "缺配置、超时、HTTP 非 2xx、空内容、无效 JSON —— 一律返回明确错误，"
         "不降级为『假成功』。", size=14, space_after=11)
para(tf, "不把模型输出当作真相、最终决策、市场事实或法律建议。", size=14, space_after=11)
para(tf, "API Key 只从运行时环境读取，不出现在日志、数据文件、响应或导出文件中。",
     size=14, space_after=11)
para(tf, "真实模型测试只保存脱敏输入摘要、状态码、模型名与输出结构摘要。", size=14)
notes(s, "这一页对应 ADR-002。评委常问『你怎么保证 AI 不乱来』——答案是两句：结构上过统一校验，"
         "失败上绝不伪装成功。后者在真实运行中被验证过，上游确实返回过 502/503。")

# ---------------------------------------------------------------- 6 真实模型证据
s = slide()
header(s, "05　真实 AI 能力证据", "生成与审查使用不同模型")
table(s, [
    ["环节", "Provider", "模型", "结果"],
    ["生成蓝图", "anthropic-compatible", "gpt-5.6-sol", "HTTP 200，8 板块通过校验"],
    ["人工编辑保存", "—", "—", "浏览器验证，编辑标记落盘"],
    ["审查", "openai-compatible", "gpt-5.6-terra", "HTTP 200，needs-revision，9 findings"],
    ["导出 Markdown", "—", "—", "HTTP 200，10455 字节"],
], top=2.4, height=2.35, col_widths=[2.3, 3.4, 2.6, 5.1], size=14)
tf = textbox(s, 0.95, 5.05, 11.4, 1.9)
para(tf, "为什么用两个不同模型？", size=16, bold=True, color=ACCENT, space_after=8, first=True)
para(tf, "同一模型自我审查等于自己判自己及格。生成用 gpt-5.6-sol，审查用 gpt-5.6-terra，"
         "审查结论是 needs-revision（blocking 4 / warning 4 / info 1）——说明审查确实在起作用，"
         "而不是走过场。", size=14, space_after=10)
para(tf, "早期失败记录保留未重写：2026-07-20 的 capability spike 两个上游分别返回 503 和 401，"
         "该记录仍在 evidence/real-ai-2026-07-20/。", size=14, color=WARN)
notes(s, "这页是『真实 AI 能力』的核心证据。两个要点：不同模型交叉审查；失败记录不删。"
         "如果被问到 demo 是不是糊弄，指出 demo 只用于测试，真实证据在这里。")

# ---------------------------------------------------------------- 7 测试与 UAT
s = slide()
header(s, "06　测试与 UAT", "四层测试 + 三类验收")
table(s, [
    ["类型", "覆盖", "结果"],
    ["Vitest 单元/存储/provider", "6 个测试文件", "13 passed"],
    ["ESLint + next build", "静态检查与生产构建", "通过，8 条路由"],
    ["本地 API UAT（curl）", "health、非法创建、创建、生成、读取、保存、审查、导出、404", "9 场景全 passed"],
    ["浏览器双会话自动化", "边界输入、编辑持久化、并发可见性、20 张截图", "22 / 22"],
    ["项目本人人工 UAT", "6 个场景", "PASS WITH LIMITS"],
    ["独立真人结对 UAT", "测试者 TYX（未参与开发）· Edge · 7 个场景", "通过（U-03 复测）"],
], top=2.4, height=3.1, col_widths=[3.3, 5.6, 2.5], size=13)
tf = textbox(s, 0.95, 5.95, 11.4, 1.4)
para(tf, "最能证明质量的一项：两次真人验收都抓到了自动化完全没发现的问题。",
     size=16, bold=True, color=ACCENT, space_after=8, first=True)
para(tf, "13 个测试全绿、API 全部 200 的情况下，浏览器打开却是白屏；真人测试者 TYX 又发现生成蓝图首次不可用。",
     size=14, color=MUTED)
notes(s, "回答『哪个测试最能证明系统质量』：不是单元测试，是人工 UAT。两次真人验收各抓到一个自动化看不见的问题——"
         "7-23 本人发现白屏与 hydration 失败，7-29 测试者 TYX 发现生成蓝图不可用。这是本项目最有说服力的经验。")

# ---------------------------------------------------------------- 8 关键决策推翻
s = slide()
header(s, "07　被推翻的架构决策", "答辩必答题")
tf = textbox(s, 0.95, 2.35, 11.4, 4.3)
para(tf, "决策：开发与构建从 Next 16 默认的 Turbopack 改回 Webpack",
     size=20, bold=True, space_after=16, first=True)
para(tf, "原判断　使用框架默认构建器，无需干预。", size=16, space_after=12)
para(tf, "推翻依据　2026-07-23 人工 UAT 发现两个阻塞：", size=16, space_after=8)
para(tf, "① Turbopack 无法解析 next/font/google 内部模块，清缓存后首页 HTTP 500、浏览器白屏；"
         "② 以 127.0.0.1 访问时 dev origin 被拦截，React hydration 未完成，输入与按钮无响应。",
     size=14, color=MUTED, space_after=12)
para(tf, "修正动作　package.json 的 dev/build 固定 --webpack；next.config.ts 仅允许回环开发来源。",
     size=16, space_after=12)
para(tf, "回归结果　health 200、页面 demo·可用、控制台 0 error、13 个测试通过。",
     size=16, space_after=16)
para(tf, "得到的判断：自动化测试全绿不能替代真人打开页面。这两个故障在 API 层与单元测试层完全不可见。",
     size=16, bold=True, color=ACCENT)
notes(s, "这是必答题，务必讲完整：原判断 → 证据 → 修正 → 回归 → 得到的判断。"
         "最后一句是重点，体现的是工程判断力而不只是修了个 bug。")

# ---------------------------------------------------------------- 9 安全
s = slide()
header(s, "08　安全与凭据保护", "扫描内建在质量门禁里")
bullets(s, [
    ("扫描规则", "scripts/check.sh 内置正则：sk- / AKIA / gh[pousr]_ / github_pat_ / glpat- "
                 "及各类 PRIVATE KEY 头，排除 .git、node_modules、.next、.env*。"),
    ("最终结果", "无命中，check: passed，退出码 0。扫描是质量门禁的一环，不是提交前临时补跑。"),
    ("凭据处理", "API Key 只从运行时环境读取；anthropic-compatible 只读本机 profile，token 不复制进项目；"
                 "真实模型测试用一次性临时凭据，测试结束即停止服务。"),
    ("数据边界", "data/launchspec.json 与 .env.local 均被 Git 忽略；真实模型证据只存脱敏摘要、"
                 "状态码、模型名与输出结构。"),
    ("隐私", "不采集真实敏感个人信息；UAT 输入为脱敏测试想法。"),
], top=2.45, gap=16)
notes(s, "回答『密钥和访问令牌如何保护』。强调一点：扫描写进了 check.sh，属于门禁，"
         "每次 check 都会跑，不是提交前想起来才做。")

# ---------------------------------------------------------------- 10 三次 Gate
s = slide()
header(s, "09　三次 Gate 与已知缺口", "如实记录，不粉饰")
table(s, [
    ["Gate", "结论", "未满足项"],
    ["Gate 1　PRD/SPEC 互审", "修改后通过", "文档阅读式复述未完成（已有使用后复述）"],
    ["Gate 2　设计审计", "修改后通过", "缺测试先行红绿证据；独立审计人未指派"],
    ["Gate 3　交付审计", "修改后通过", "提交粒度缺口（真人 UAT 已于 07-29 补齐）"],
], top=2.4, height=1.85, col_widths=[3.6, 2.4, 5.4], size=14)
tf = textbox(s, 0.95, 4.5, 11.4, 2.5)
para(tf, "确认存在的缺口", size=17, bold=True, color=WARN, space_after=10, first=True)
para(tf, "提交 4414ea4 一次性引入 79 文件、11407 行，覆盖 C1–C7 全部任务卡，"
         "无法逐卡对应，也无法体现红绿顺序。", size=14, space_after=8)
para(tf, "已补齐：独立真人结对 UAT 于 2026-07-29 由未参与开发的测试者 TYX 完成，"
         "发现并复测了 1 项阻断问题。", size=14, space_after=8)
para(tf, "同一测试者用完后把系统复述为「AI 总结出方案」，未提到人工编辑与审查——"
         "说明「AI 给草案，人做决策」这一核心立场传达不足，已列入 PRD 改进动作。",
     size=14, space_after=12)
para(tf, "提交粒度缺口不做补救——补写『先失败的提交』等同伪造历史，属课程红线。"
         "处理方式是如实声明，并以集中期 arena-lite 的红绿证据说明方法已掌握。",
     size=15, bold=True, color=ACCENT)
notes(s, "主动交代缺口，不等评委问。特别是提交粒度问题——要讲清楚为什么不补：补了就是伪造。"
         "这个态度本身就是课程要考的工程诚实。真人 UAT 已补齐，可正面说明。")

# ---------------------------------------------------------------- 11 限制与下一步
s = slide()
header(s, "10　已知限制与后续计划", "边界清楚，用户可绕行")
tf = textbox(s, 0.95, 2.35, 5.55, 4.2)
para(tf, "已知限制", size=17, bold=True, color=WARN, space_after=11, first=True)
para(tf, "1　单机本地 MVP，无账号、权限、支付、多人实时协作与异步队列。", size=14, space_after=9)
para(tf, "2　JSON 存储不支持多进程并发写入与复杂查询。", size=14, space_after=9)
para(tf, "3　自动化测试固定 demo provider；demo 不是真实模型能力证据。", size=14, space_after=9)
para(tf, "4　真实模型证据为单次脱敏运行，非持续可用性保证。", size=14, space_after=9)
para(tf, "5　未保留测试先行的红绿提交序列。", size=14)

tf = textbox(s, 6.85, 2.35, 5.5, 4.2)
para(tf, "用户如何绕行", size=17, bold=True, color=ACCENT, space_after=11, first=True)
para(tf, "并发问题 → 单人单进程使用。", size=14, space_after=9)
para(tf, "真实模型不可用 → 切回 demo，界面与流程仍可用，但结果须标注为非真实模型。",
     size=14, space_after=18)
para(tf, "如果再给一周", size=17, bold=True, color=ACCENT, space_after=11)
para(tf, "补　独立评审人对 PRD/SPEC 的复述记录。", size=14, space_after=9)
para(tf, "补　新增功能真实走一次红绿流程，留独立的红、绿两次提交。", size=14, space_after=9)
para(tf, "砍　不做多人协作与云端存储，维持单机边界。", size=14)
notes(s, "回答『再给一周砍什么补什么』。补的是证据链缺口，砍的是范围诱惑——"
         "强调维持边界本身也是一种决策。")

# ---------------------------------------------------------------- 12 Q&A 备份
s = slide()
header(s, "11　Q&A 备份", "证据定位速查")
table(s, [
    ["问题", "回答要点", "证据路径"],
    ["服务哪类用户？最小场景？", "创业团队/外包 PM/学生组；想法→蓝图→审查→导出",
     "docs/PRD.md"],
    ["哪个架构决策被推翻？", "Turbopack 改回 Webpack；人工 UAT 发现",
     "gate-3-delivery.md"],
    ["哪个测试最能证明质量？", "两次真人验收各抓到一个自动化看不见的问题",
     "human-pair-uat-2026-07-29.md"],
    ["哪段 AI 生成内容被修改？", "蓝图字段人工编辑并落盘，导出含人工标记",
     "real-ai-2026-07-22/export.md"],
    ["密钥如何保护？", "运行时环境读取 + check.sh 内置扫描 + 数据文件 Git 忽略",
     "scripts/check.sh"],
    ["再给一周做什么？", "补独立真人 UAT 与红绿序列；砍多人协作",
     "final-report.md §12"],
    ["当前已知限制？", "单机、无并发、demo 非真实证据、红绿序列缺口",
     "final-report.md §12"],
], top=2.4, height=4.0, col_widths=[3.5, 5.3, 2.6], size=12)
notes(s, "备份页，正常不讲。被问到时直接定位到对应文件。所有回答都能落到仓库内的具体路径，"
         "不靠临场发挥。")

OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(OUT)
print(f"saved: {OUT}")
print(f"slides: {len(prs.slides.__iter__.__self__._sldIdLst)}")
