# 最终报告 2510631109-launchspec-ai

- Delivery ID（交付标识）: 2510631109-launchspec-ai
- 项目名称: LaunchSpec AI
- 撰写日期: 2026-08-02

---

## 1. 仓库与最终提交号

| 项 | 内容 |
|---|---|
| 仓库地址 | `https://github.com/xuzihan0823/msd-2510631109-arena-lite` |
| 项目路径 | `projects/launchspec-ai` |
| 分支 | `feat/2510631109-local-ci` |
| 报告初稿撰写时 HEAD | `6b2fe9c`（2026-07-23） |
| **最终冻结提交号** | **`ab364f051ff81925fa9964539a6663d7bf0390ab`**（短号 `ab364f0`，2026-08-02） |

冻结口径：`ab364f0` 是本项目最后一次**内容提交**（记录测试者复述与 PRD 定位缺陷，同步 Gate 1、第 1 次周志、最终报告与答辩 PPT）。代码、测试、证据文件与全部评审结论均冻结于此。该提交之后只有一次提交号补录：把本字段与第 2 次周志第 8 节的占位表述替换为真实 SHA，并在答辩 PPT 封面与 Q&A 备份页加入同一 SHA；不改动任何代码、测试、证据或结论。

复核命令：

```bash
git log --oneline -1 ab364f0
git show --stat ab364f0
```

集中期跟练项目 `arena-lite` 位于仓库根目录，自选项目 LaunchSpec AI 位于 `projects/launchspec-ai`，两者主题、接口与技术栈完全不同。

## 2. 运行、测试与演示命令

```bash
cd projects/launchspec-ai
npm install

npm run dev      # 启动，打开 http://127.0.0.1:3000
npm run test     # Vitest：6 文件 13 测试
npm run lint     # ESLint
npm run build    # Next.js 生产构建（Webpack）
npm run check    # test + lint + build + git diff --check + 密钥扫描
npm run uat      # 启动本地服务并执行 9 场景 API UAT（demo 模式）
```

真实模型运行（二选一，凭据只经环境变量传入，不入库）：

```bash
# 方案 A：OpenAI-compatible
# 复制 .env.example 为 .env.local，设置 AI_PROVIDER / AI_BASE_URL / AI_API_KEY / AI_MODEL

# 方案 B：复用本机 Claude Code profile
AI_PROVIDER=anthropic-compatible \
CLAUDE_CONFIG_PATH="$HOME/.claude/settings.json" \
npm run dev
```

**演示路径**：创建项目 → 生成蓝图 → 编辑字段并保存 → 刷新验证持久化 → 执行审查 → 导出 Markdown。

## 3. PRD 摘要

- **目标用户**：创业团队负责人、外包项目经理、需要快速对齐产品范围的学生项目组。
- **核心场景**：开始编码前把一句想法转成结构化草案，团队编辑审查后导出进仓库。
- **成功指标**：5 分钟内完成创建 → 生成 → 编辑 → 审查 → 导出，产出不含占位符的方案草案。
- **用户故事**：US-1 创建产品想法、US-2 生成并编辑蓝图、US-3 审查并导出方案；每个各 2 条「操作 → 预期输出」验收标准。
- **非目标**：不自动生成完整业务代码或部署配置、不做账号/多人协作/支付/云存储、不把 demo 伪装为真实模型能力、不收集真实隐私与访问令牌。

## 4. SPEC 摘要

**数据模型**：`Project`（`stage: draft | generated | reviewed`）、`Blueprint`（`acceptanceCriteria` 2–8 项、`risks` 1–8 项、8 个结构板块）、`ReviewReport`（`readiness`、`findings`、`source`）。

**API 契约**：

| 方法与路径 | 成功 | 失败 |
|---|---|---|
| `GET /api/health` | `200` 返回 provider 状态 | — |
| `GET /api/projects` | `200` 按 `updatedAt` 降序 | — |
| `POST /api/projects` | `201` | `400` |
| `GET /api/projects/{id}` | `200` | `404` |
| `PUT /api/projects/{id}` | `200`，清除旧审查 | `400`、`404` |
| `POST /api/projects/{id}/generate` | `200` | `404`、`502/503` |
| `POST /api/projects/{id}/review` | `200` | `404`、`409`、`502/503` |
| `GET /api/projects/{id}/export` | `200` text/markdown | `404`、`500` |

`/api/health` 不返回 API Key、endpoint query 或任何环境变量值。

## 5. DESIGN 与 ADR 摘要

**架构**：浏览器 React 工作台 → Next.js Route Handlers（校验/错误映射 → repository → provider adapter → review engine → exporter）→ `data/launchspec.json`。

**关键设计约束**：`src/lib/validation.ts` 是输入与模型 JSON 的单一结构校验点。任何 provider 的返回都必须通过同一份 `validateBlueprint` 才能入库，因此真实模型的不确定输出无法绕过结构约束。

**ADR-001 本地 JSON 原子写入**（已接受，2026-07-20）
候选：SQLite / PostgreSQL / 内存数组。决策：临时文件 + `rename` 原子替换。代价：不支持多进程并发与复杂查询——已在 README、PRD、DESIGN 三处显式声明为边界。

**ADR-002 AI provider 边界**（已接受，2026-07-20）
候选：页面内直连模型 / 只做 demo / 绑定单一商业 SDK。决策：统一契约 + 三种 provider。核心取舍：**上游失败不降级为假成功**；`anthropic-compatible` 运行时读取本机 Claude Code profile，token 不复制进项目。

## 6. 任务卡

`process/task_cards/launchspec-ai-project-cards.md`，7 张（C1–C7），每张含 Role、Context、Task、User Value、Acceptance Criteria、Test Command、Non-goals、Risk/response、Estimated Effort、Dependencies 十个字段。全部完成，验证方式见第 2 次周志第 2 节。

## 7. 三次 Gate

| Gate | 记录 | 结论 | 未满足项 |
|---|---|---|---|
| Gate 1 PRD/SPEC 互审 | `process/gate/2510631109-launchspec-ai-gate-1-prd-spec.md` | 修改后通过 | 独立评审人的文档阅读式复述未完成（已有独立使用者的使用后复述作为部分证据） |
| Gate 2 设计审计 | `process/gate/2510631109-launchspec-ai-gate-2-design.md` | 修改后通过 | F-1 缺测试先行红绿证据；F-2 独立审计人未指派 |
| Gate 3 交付审计 | `process/gate/2510631109-launchspec-ai-gate-3-delivery.md` | 修改后通过 | F-2 提交粒度缺口（F-1 独立真人 UAT 已于 07-29 补齐） |

Gate 1 含两轮 Loop Engineering 审计记录：Loop-1 AI 能力与规格边界复审（2026-07-22）、Loop-2 运行时可用性与验收复审（2026-07-23）。两轮均有证据命令与产物，且 Loop-2 的假设被实际推翻。

## 8. UAT

| 类型 | 记录 | 覆盖 | 结论 |
|---|---|---|---|
| 本地 API UAT | `process/uat/launchspec-ai-draft-uat.md` | 9 场景 | 全部 passed |
| 浏览器双会话自动化 | `evidence/pair-uat-2026-07-22/uat_results.json` | 22 项 + 20 截图 | 22/22 |
| 项目本人人工 UAT | `process/uat/launchspec-ai-human-uat-2026-07-23.md` | 6 场景 | PASS WITH EVIDENCE LIMITS |
| 独立真人结对 UAT | `process/uat/launchspec-ai-human-pair-uat-2026-07-29.md` | 7 场景（测试者 TYX） | 通过（U-03 修复后复测） |

主路径：health → 创建 `201` → 生成 `200` → 读取 `200` → 保存 `200` → 审查 `200` → 导出 `200`。
错误路径：非法创建 `400`、项目不存在 `404` 已落盘；`409`、`500`、`502/503` 已在 SPEC 定义，其中 `502/503` 在真实上游故障中被实际观测。

人工验收发现了两批自动化测试无法发现的问题：本人 UAT（2026-07-23）发现 Turbopack 模块解析与 dev origin 拦截两个阻塞；独立真人 UAT（2026-07-29，测试者 TYX）发现「生成蓝图」首次不可用、内容不显示，处理后复测通过。

## 9. Evidence 索引

| 目录 | 内容 | 性质 |
|---|---|---|
| `evidence/final-check-2026-08-02/` | `npm run check` 与 `git diff --check` 最终输出 | 收官检查 |
| `evidence/local-uat/` | `npm run uat` 生成的 API UAT 输出 | demo provider，非真实模型证据 |
| `evidence/pair-uat-2026-07-22/` | 浏览器双会话 UAT 结果与 20 张截图 | 不替代真人反馈 |
| `evidence/human-uat-2026-07-23/` | 本人人工验收截图与同名说明 | 含修复前故障复现，不可混用 |
| `evidence/real-ai-2026-07-22/` | 真实模型生成、不同模型审查、导出摘要 | 真实模型证据 |
| `evidence/real-ai-2026-07-20/` | 早期 capability spike 失败记录（`503`、`401`） | **保留未重写为成功** |

索引说明见 `evidence/README.md`；全仓过程入口见 `PROCESS.md`。

## 10. 安全与隐私

- **密钥扫描**：`scripts/check.sh` 内置正则覆盖 `sk-`、`AKIA`、`gh[pousr]_`、`github_pat_`、`glpat-` 及各类 PRIVATE KEY 头；最终扫描无命中。
- **凭据处理**：API Key 只从运行时环境读取，不出现在日志、数据文件、响应或导出文件中；`anthropic-compatible` 只读取本机 profile，不复制 token；真实模型测试使用一次性临时凭据，测试结束即停止服务。
- **数据边界**：`data/launchspec.json` 与 `.env.local` 均被 Git 忽略；真实模型证据只保存脱敏输入摘要、状态码、模型名与输出结构摘要。
- **隐私**：不采集真实敏感个人信息；UAT 输入为脱敏测试想法。

## 11. 成员分工

个人提交，全部角色由徐驰宇（学号 2510631109）承担：需求与规格、架构与 ADR、实现、测试与 UAT、安全扫描与文档收口。

AI 使用边界：AI 承担样板代码、测试脚手架与文档草稿；范围判断、架构取舍、验收标准与最终结论由本人确认。真实模型的生成与审查分别使用 `gpt-5.6-sol` 与 `gpt-5.6-terra` 两个不同模型，避免同一模型自我审查。

## 12. 已知限制与后续计划

**已知限制**

1. 单机本地 MVP，无账号、权限、支付、多人实时协作与异步队列。
2. JSON 存储不支持多进程并发写入与复杂查询。
3. 自动化测试固定 demo provider；demo 不是真实模型能力证据。
4. 真实模型证据为单次脱敏运行，非持续可用性保证。
5. **未保留测试先行的红绿提交序列**；`4414ea4` 为 79 文件、11407 行的单次大提交，不满足「提交对应任务卡」的要求。

第 5 项属于确认存在的交付缺口，已在 Gate 2、Gate 3 与第 2 次周志中如实记录。该项不可事后补造——补写「先失败的提交」等同伪造历史，属课程红线。

**后续计划**

1. 后续新增功能真实执行红绿流程，留独立的红、绿两次提交。
2. 若需支持并发，按 ADR-001 的 later 路径把 `repository.ts` 替换为 SQLite/PostgreSQL adapter。
3. 补独立评审人对 PRD/SPEC 的**文档阅读式**复述记录（Gate 1 未满足项）。
4. 依据 TYX 的使用后复述反馈，强化 PRD 第 1 节与界面对「人工编辑与审查为必经环节」的表述，改后重新验证复述效果。
