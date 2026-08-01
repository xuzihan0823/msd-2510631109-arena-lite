# 第 2 次周志（W3–W4）2510631109-launchspec-ai

- Delivery ID（交付标识）: 2510631109-launchspec-ai
- 项目名称: LaunchSpec AI
- 覆盖周次: W3（核心功能小步实现）、W4（UAT、修正、冻结版本、答辩准备）
- 仓库: `https://github.com/xuzihan0823/msd-2510631109-arena-lite`，项目路径 `projects/launchspec-ai`
- 撰写日期: 2026-08-02

---

## 1. 实现进展

已交付的最小闭环共 5 步，全部可运行、可测试、可复现：

1. 创建并保存项目想法（JSON 原子持久化）
2. 通过 AI provider 生成结构化蓝图
3. 界面中编辑并持久化蓝图
4. 审查范围、非目标、验收标准、风险与人工确认边界
5. 导出含审查结论的 Markdown

**已实现的 8 条路由**：`/`、`/_not-found`、`/api/health`、`/api/projects`、`/api/projects/[id]`、`/api/projects/[id]/generate`、`/api/projects/[id]/review`、`/api/projects/[id]/export`。

**关键实现约束**：`src/lib/validation.ts` 是输入与模型输出的唯一结构校验点；provider 无论 demo 还是真实模型，返回内容都必须通过同一份 `validateBlueprint` 才能入库；保存编辑会清除过期审查结论，避免审查与内容不一致。

## 2. 任务卡完成情况

任务卡：`process/task_cards/launchspec-ai-project-cards.md`，共 7 张。

| 卡 | 内容 | 状态 | 验证 |
|---|---|---|---|
| C1 | 项目想法与本地持久化 | 完成 | `repository.test.ts` green；UAT `create_project=201`、非法 `400` |
| C2 | 结构化蓝图生成 | 完成 | `ai-provider.test.ts`、`blueprint.test.ts` green；真实 provider 缺配置明确报错 |
| C3 | 蓝图编辑与保存 | 完成 | UAT `save_blueprint=200`；保存清除旧审查 |
| C4 | 方案审查 | 完成 | `review.test.ts` green；缺非目标或 <2 条验收 → `needs-revision` |
| C5 | Markdown 导出 | 完成 | `export.test.ts` green；UAT `export_markdown=200` |
| C6 | 本地质量门禁与 API UAT | 完成 | `npm run check && npm run uat` 退出码 `0` |
| C7 | 课程过程资产与人工收官 | 完成（Gate 与提交文件已补齐） | 本次新增三份 Gate 与四个提交文件 |

## 3. 小步提交与 PR

**如实说明：本项目的提交粒度不满足手册要求。**

| 提交 | 范围 |
|---|---|
| `4414ea4` | 79 files changed, 11407 insertions —— 覆盖 C1–C7 全部任务卡 |
| `1d5bb2e` | 1 file changed |
| `ef4162a` | 1 file changed, 77 insertions（人工结对 UAT 模板） |
| `6b2fe9c` | 42 files changed, 1078 insertions, 11 deletions（运行时修复 + UAT 记录） |

`4414ea4` 属于 `提交期.md:309` 明确禁止的「用一个巨大提交掩盖过程」，且无法做到「提交或 PR 能对应任务卡」。此缺口已在 Gate 2（F-1）与 Gate 3（F-2）记录，不在本周志中掩饰。

补造历史提交等同伪造证据，因此不做补救；处理方式是如实声明，并以集中期 `arena-lite` 的红绿证据（`2030053 add D10 red tests` → `71fd253 implement us1 us2 api slice`）说明方法本身已掌握。

## 4. 测试输出

```text
$ npm run check
> vitest run
 Test Files  6 passed (6)
      Tests  13 passed (13)
   Duration  369ms
> eslint
（无告警）
> next build --webpack
✓ Compiled successfully in 4.4s
  Finished TypeScript in 1402ms
  Generating static pages (3/3)
$ git diff --check
（无输出）
check: passed        # 退出码 0，含内置密钥正则扫描
```

证据：`evidence/final-check-2026-08-02/check.txt`、`evidence/final-check-2026-08-02/diff-check.txt`（空文件）。

**六个测试文件**：`validation.test.ts`、`blueprint.test.ts`、`review.test.ts`、`export.test.ts`、`repository.test.ts`、`ai-provider.test.ts`。

## 5. UAT 与修正

三类 UAT，性质各不相同，不互相冒充；另有一次独立真人结对 UAT：

### 5.1 本地 API UAT（自动化 curl，9 场景全 passed）

`process/uat/launchspec-ai-draft-uat.md`、`evidence/local-uat/uat-status.txt`

Health `200`、非法创建 `400`、创建 `201`、生成 `200`、读取 `200`、保存 `200`、审查 `200`、导出 `200`、项目不存在 `404`。

**主路径 + 2 条以上错误路径**已覆盖，满足 Gate 3 要求。

### 5.2 浏览器双会话自动化 UAT（22/22）

`evidence/pair-uat-2026-07-22/uat_results.json`，含 20 张过程截图，覆盖边界输入（1 字名称、19 字想法）、编辑持久化、刷新后一致性、双会话并发可见性。**不替代真人反馈。**

### 5.3 项目本人人工 UAT（6 场景 pass，结论 PASS WITH EVIDENCE LIMITS）

`process/uat/launchspec-ai-human-uat-2026-07-23.md`

**本轮发现并修复两个阻塞问题**，这是自动化测试完全没能发现的：

1. Next 16 默认 Turbopack 无法解析 `next/font/google` 内部模块 → 清缓存后首页 HTTP `500`、浏览器白屏。
2. 以 `127.0.0.1` 访问时 dev origin 被拦截 → 仅有服务端 HTML，React hydration 未完成，输入与按钮无响应。

**修正**：`package.json` 的 `dev`/`build` 固定 `--webpack`；`next.config.ts` 仅允许回环开发来源。

**回归验证**：health `200`、`demo · 可用`、项目列表 3 项、重新生成成功、控制台 0 JavaScript error、Vitest 13 通过、ESLint 通过、`git diff --check` 通过。

截图区分严格：`before-fix-initial-state.png` 是故障复现证据，**不能作为通过截图**。

### 5.4 独立真人结对 UAT（2026-07-29，7 场景通过）

`process/uat/launchspec-ai-human-pair-uat-2026-07-29.md`

测试者 **TYX（未参与开发）**，使用 Microsoft Edge，demo provider，完成 U-01 至 U-07 主链路。

**发现 1 项阻断问题**：U-03「生成蓝图」首次不可用、蓝图内容无法显示。处理后测试者重新执行 U-03 至 U-07，全部通过；其余 6 项一次通过，未发现其他问题。

该次处理**未产生新的业务代码提交**——仓库在 `6b2fe9c`（2026-07-23）与 `5a3b56d`（2026-08-02）之间无提交记录，工作区干净。记录中据此未引用修复提交号，避免与实际提交历史不符。

测试者对「最容易理解的部分」与「是否愿意在实际项目中使用」未作表述，记录中如实留空，未代写测试者原话。

### 5.5 真实模型运行（2026-07-22）

`evidence/real-ai-2026-07-22/`：生成 `gpt-5.6-sol` HTTP `200`；审查 `gpt-5.6-terra` HTTP `200`、`needs-revision`、blocking 4 / warning 4 / info 1；导出 `200`、10455 字节。生成与审查为不同模型。

早期失败记录 `evidence/real-ai-2026-07-20/`（两个上游分别 `503` 与 `401`）**保留未重写为成功**。

## 6. Gate 3 结论

记录：`process/gate/2510631109-launchspec-ai-gate-3-delivery.md`

**结论：修改后通过。**

满足：本地检查通过（退出码 0）、UAT 覆盖主路径 + 2 条以上错误路径、密钥扫描无真实凭据、README 可让评审者独立启动、能解释被推翻的架构决策。**F-1 独立真人结对 UAT 已于 2026-07-29 完成。**

未满足：F-2 提交粒度缺口（承接 Gate 2）。

## 7. 安全扫描

`scripts/check.sh` 内置密钥正则，覆盖 `sk-[A-Za-z0-9_-]{20,}`、`AKIA[0-9A-Z]{16}`、`gh[pousr]_`、`github_pat_`、`glpat-` 及各类 PRIVATE KEY 头，排除 `.git`、`node_modules`、`.next`、`.env*`。

**本次扫描结果：无命中**，`check: passed`。

数据边界：`data/launchspec.json` 被 Git 忽略；`.env.local` 不入库；`anthropic-compatible` 只在运行时读取本机 Claude Code profile，token 不复制进项目、不写入响应/数据文件/证据/日志；真实模型测试所用为一次性临时凭据，测试结束即停止服务。

## 8. 最终提交号

- 分支：`feat/2510631109-local-ci`
- 本周志撰写时 HEAD：`6b2fe9c`
- 最终冻结提交号：见本次收官提交的 `git log --oneline -1` 输出

## 9. 已知限制

1. 单机本地 MVP，无账号、权限、支付、多人实时协作与异步队列。
2. JSON 文件存储适用于课程演示与小数据量，不适用于多进程并发生产环境。
3. 自动化测试固定使用 demo provider，不依赖真实模型输出；demo **不是**真实模型能力证据。
4. 真实模型证据为 2026-07-22 的一次脱敏运行，非持续可用性保证；上游曾出现 `502/503` 瞬时过载。
5. 未保留测试先行的红绿提交序列。

**用户绕行方式**：并发问题——单人单进程使用；真实模型不可用——切回 demo provider 保证界面与流程可用，但需明确标注非真实模型结果。

## 10. 答辩准备

答辩 PPT：`submissions/2510631109-launchspec-ai-defense.pptx`（12 页，含演示路径、AI 边界、UAT、安全、关键决策与 Q&A 备份）。

**演示路径**（5–8 分钟）：`npm run dev` → 打开 `http://127.0.0.1:3000` → 输入脱敏产品想法创建项目 → 生成蓝图 → 编辑一个字段并保存 → 刷新验证持久化 → 执行审查 → 导出 Markdown。

**必答准备**：被推翻的决策 = Turbopack 改回 Webpack（详见 Gate 3）；最能证明质量的测试 = `npm run check` 全链路 + 9 场景 API UAT；密钥保护 = 运行时环境变量读取 + 内置扫描 + 数据文件 Git 忽略。
