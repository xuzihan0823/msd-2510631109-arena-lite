# 第 1 次周志（W1–W2）2510631109-launchspec-ai

- Delivery ID（交付标识）: 2510631109-launchspec-ai
- 项目名称: LaunchSpec AI
- 覆盖周次: W1（选题、PRD/SPEC、最小纵切面）、W2（DESIGN、ADR、核心骨架）
- 仓库: `https://github.com/xuzihan0823/msd-2510631109-arena-lite`，项目路径 `projects/launchspec-ai`
- 撰写日期: 2026-08-02

---

## 1. 项目题目与选题理由

**LaunchSpec AI** —— 把一句模糊的产品想法，转化为可编辑、可审查、可导出的 MVP 项目蓝图。

选题与集中期跟练项目 `arena-lite`（模型对战 + 匿名投票 + ELO 排行）在用户、场景、接口与 AI 能力上完全不同：

| 维度 | arena-lite（跟练） | LaunchSpec AI（自选） |
|---|---|---|
| 用户 | 投票者与管理员 | 创业团队负责人、外包 PM、学生项目组 |
| 核心动作 | 匿名投票、揭盲结算 | 想法结构化、蓝图编辑、方案审查 |
| AI 能力 | mock 适配器产出对战回答 | 真实模型生成结构化蓝图 + 不同模型只读审查 |
| 接口 | `POST /battles`、`POST /vote`、`GET /leaderboard` | `POST /api/projects`、`/generate`、`/review`、`/export` |
| 技术栈 | Python + FastAPI + SQLite | TypeScript + Next.js 16 + 本地 JSON |

沿用的只有方法：本地 CI 习惯、任务卡字段、UAT 表结构、安全扫描规则、`PROCESS.md` 索引方式与「命令 → 证据 → 决策」闭环。

## 2. 用户与场景

- **目标用户**：创业团队负责人、外包项目经理、需要快速对齐产品范围的学生项目组。
- **核心场景**：项目负责人在开始编码前输入产品想法，生成结构化草案；团队编辑、审查后导出为 Markdown 放进仓库。
- **要解决的问题**：产品想法分散在聊天记录与临时笔记里；即使用 AI 生成，结果也常是不可测试的长文，缺少范围、验收与风险约束。
- **成功指标（MVP）**：用户可在 5 分钟内完成创建 → 生成 → 编辑 → 审查 → 导出，产出一份不含占位符的方案草案。

## 3. PRD / SPEC 摘要

完整文档：`docs/PRD.md`、`docs/SPEC.md`。

**三个用户故事，每个 2 条可测试验收标准：**

- **US-1 创建产品想法**：≥2 字名称 + ≥20 字想法 → `POST /api/projects` 返回 `201`；过短或非 JSON → `400` 且不创建。
- **US-2 生成并编辑蓝图**：生成返回目标用户、问题、MVP 范围、非目标、≥2 条验收标准、风险、架构、AI 边界；`PUT` 保存后 `GET` 能读回修改。
- **US-3 审查并导出方案**：审查返回 `ready` 或 `needs-revision` 及结论；导出返回 `200` + Markdown + AI 使用边界。

**数据契约**：`Project`（含 `stage: draft | generated | reviewed`）、`Blueprint`（`acceptanceCriteria` 2–8 项、`risks` 1–8 项）、`ReviewReport`（`readiness`、`findings`、`source`）。

**错误路径**：`400` 非法输入、`404` 项目不存在、`409` 未生成即审查、`500` 未生成即导出、`502/503` 上游模型失败。

**非目标**：不自动生成完整业务代码或部署配置、不做账号/多人协作/支付/云存储、不把 demo provider 伪装为真实模型能力、不收集真实隐私与访问令牌。

## 4. Gate 1 结论

记录：`process/gate/2510631109-launchspec-ai-gate-1-prd-spec.md`

**结论：修改后通过。**

- 满足：3 个用户故事 × 2 条可测验收标准、5 类错误路径、4 类非目标、范围可完成。
- 满足：AI capability spike 与最小纵切面**两者都有证据**。
- 未满足：独立评审人的**文档阅读式**复述（当前仅本人自审 + 不同模型只读审查）。

### 复述验证的部分证据与发现

2026-07-29，未参与开发的测试者 TYX 在用完产品后被问「这个系统是做什么的」，回答是：

> 「这个系统应该是提出想法然后由 AI 进行总结最后给出项目的方案吧。」

这条**不算 Gate 1 通过**——手册要求的是读完 PRD/SPEC 后的复述，本条是用完产品后的复述，验证对象不同。

但它暴露了一个真实问题：测试者把 AI 的动作理解成「总结」（实际是从一句话**展开**成 8 个板块），并且复述中**完全没有出现人工编辑与审查环节**。也就是说，项目最核心的立场「AI 给草案，人做决策」，在完整用过一遍之后仍然没有传达到位。

**改进动作**：把「人工编辑与审查是必经环节」在 `docs/PRD.md` 第 1 节提到更显式的位置，界面上强化生成后仍需人工确认的提示，改后重新取一次文档阅读式复述验证效果。

### AI capability spike（真实模型能力探针）

2026-07-22 完成一次真实模型端到端运行，证据在 `evidence/real-ai-2026-07-22/`：

| 环节 | Provider | 模型 | 结果 |
|---|---|---|---|
| 生成蓝图 | `anthropic-compatible` | `gpt-5.6-sol` | HTTP `200`，8 个结构板块，通过 Blueprint 校验 |
| 人工编辑 + 保存 + 刷新 | — | — | 浏览器验证通过，编辑标记落盘 |
| 审查 | `openai-compatible` | `gpt-5.6-terra` | HTTP `200`，`needs-revision`，9 条 findings，`source=model` |
| 导出 Markdown | — | — | HTTP `200`，10455 字节，含人工标记与审查结论 |

生成与审查刻意使用**不同模型**，满足「独立评审人 / 不同模型只读审计」的设计意图。

### 最小纵切面

「输入想法 → 生成蓝图 → 人工编辑保存 → 审查 → 导出 Markdown」五步闭环，每步都有落盘证据，非纸面定义。

## 5. DESIGN / ADR 摘要

完整文档：`docs/DESIGN.md`、`docs/adr/`。

**分层**：浏览器 React 工作台 → Next.js Route Handlers（校验/错误映射、repository、provider adapter、review engine、exporter）→ `data/launchspec.json`。

**模块边界**：`validation.ts` 是输入与模型 JSON 的**单一结构校验点**——无论 demo 还是真实 provider，返回内容都必须过同一份 `validateBlueprint` 才能入库。

**ADR-001 本地 JSON 原子写入**：候选为 SQLite / PostgreSQL / 内存数组。选 JSON + 临时文件 rename 原子替换。代价（不支持多进程并发与复杂查询）已在 README、PRD、DESIGN 三处显式声明。

**ADR-002 AI provider 边界**：候选为页面内直连模型 / 只做 demo / 绑定单一商业 SDK。选统一契约 + 三种 provider（`demo`、`openai-compatible`、`anthropic-compatible`）。关键取舍：**上游失败不降级为假成功**，缺配置、超时、非 2xx、空内容、无效 JSON 一律报错。`anthropic-compatible` 在运行时读取本机 Claude Code profile，token 不复制进项目。

## 6. Gate 2 结论

记录：`process/gate/2510631109-launchspec-ai-gate-2-design.md`

**结论：修改后通过。**

- 满足：DESIGN 指向 SPEC 每条契约；2 条 ADR 均有真实候选与取舍；AI 边界与失败路径 7 条写清；测试策略四层分离。
- **未满足（F-1）：核心功能缺少测试先行的红绿证据。** 提交 `4414ea4` 一次性引入 79 文件、11407 行，实现与测试同提交落地，无法区分先后；冲刺记录写的是「实现完成后 10 个测试通过」。这同时触及 `提交期.md:309` 的红线「不用一个巨大提交掩盖过程」。
- 未满足（F-2）：独立设计审计人未指派。

**关于 F-1 的处理**：红绿序列不可事后伪造——补造一个「先失败的提交」属红线。本周志如实声明本项目未保留红绿序列；该方法本人已在集中期掌握并留有证据（`arena-lite` 的 `2030053 add D10 red tests` → `71fd253 implement us1 us2 api slice`）。后续如仍有新增功能，将真实执行一次红绿流程并留独立的红、绿两次提交。

## 7. 关键命令输出

```text
$ npm run check
> vitest run
 Test Files  6 passed (6)
      Tests  13 passed (13)
> eslint
（无告警）
> next build --webpack
✓ Compiled successfully in 4.4s
  Finished TypeScript in 1402ms
Route (app): / , /_not-found , /api/health , /api/projects ,
  /api/projects/[id] , /api/projects/[id]/export ,
  /api/projects/[id]/generate , /api/projects/[id]/review
$ git diff --check
（无输出）
check: passed
```

证据文件：`evidence/final-check-2026-08-02/check.txt`、`diff-check.txt`。

## 8. 风险与变化

| 风险 | 缓解 | 本阶段变化 |
|---|---|---|
| 模型输出空泛或格式错误 | 固定 JSON 契约 + 服务端强校验 + 规则审查 + 人工编辑 | 真实运行验证有效，`needs-revision` 正确拦下不完整草案 |
| 真实模型服务不可用 | demo 保持测试与 UI 可用；失败如实记录 | 已实际发生：`anthropic-compatible` 一度 `502/503`；早期 `503`/`401` 失败记录保留未重写 |
| JSON 存储不适合并发 | 明确仅限单机课程 MVP | 无变化 |
| 团队误把 AI 草案当事实 | UI、导出、文档均标注「AI 给草案，人做决策」 | 无变化 |
| **新增：框架默认构建器不可用** | 固定 Webpack + 限定回环 dev origin | 2026-07-23 人工 UAT 发现并修复 |

## 9. 下一步（进入 W3–W4）

1. 完成本地质量门禁与 API UAT 的最终运行并留证。（已完成，见第 2 次周志）
2. 补齐三次 Gate 记录与四个提交文件。（本次已完成）
3. 待人工：独立真人结对 UAT、独立评审人复述。
4. 待人工：若课程要求，补一次真实红绿序列提交。

## 10. 安全与脱敏

本周志不含真实账号、API Key、Token、支付信息、私有服务地址或数据库连接串。真实模型运行只保留脱敏输入摘要、状态码、模型名与输出结构摘要；测试所用为一次性临时凭据，仅通过环境变量传入进程，未写入任何文件或日志。
