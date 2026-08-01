# Gate 1 PRD/SPEC Review（PRD/SPEC 评审）2510631109-launchspec-ai

- Reviewer（评审者）: 徐驰宇（项目本人自审）+ 不同模型只读审查 `gpt-5.6-terra`；**独立真人评审人复述尚未完成**
- Date（日期）: 2026-08-02
- Project topic（项目主题）: LaunchSpec AI — 把产品想法转化为可编辑、可审查、可导出的 MVP 项目蓝图
- Delivery ID（交付标识）: 2510631109-launchspec-ai
- Main users（主要用户）: 创业团队负责人、外包项目经理、需要快速对齐产品范围的学生项目组
- Accepted scope（接受范围）: 本地单机项目创建与 JSON 持久化；demo 与真实 provider 的结构化蓝图生成；蓝图编辑保存；规则/模型审查；Markdown 导出；`/api/health`、单元测试、检查脚本与本地 API UAT
- Removed scope（移出范围）: 账号体系、多人实时协作、支付、积分、云端对象存储、项目管理工具同步、自动生成完整业务代码与部署配置
- Most important risk（最重要风险）: 模型输出空泛或格式不正确，导致草案不可测试。缓解：固定 JSON 契约 + 服务端 `validateBlueprint` 强校验 + 规则审查 + 人工编辑确认
- AI capability spike（AI 能力探针）: 已完成真实模型端到端运行。生成使用 `anthropic-compatible` 上游的 `gpt-5.6-sol`，审查使用 `openai-compatible` 上游的 `gpt-5.6-terra`，两端为不同模型
- Minimum vertical slice（最小纵切面）: 输入产品想法 → 生成结构化蓝图 → 人工编辑保存 → 模型审查 → 导出 Markdown，五步闭环全部落盘可验证
- Spike evidence（探针证据）: `evidence/real-ai-2026-07-22/README.md`、`generate-summary.json`、`review-summary.json`、`export.md`；生成 HTTP `200`、8 个结构板块通过校验；审查 HTTP `200`、`readiness=needs-revision`、9 条 findings、`source=model`；导出 HTTP `200`、10455 字节

## Requirement Coverage（需求覆盖核对）

| 手册要求 | 实际 | 结论 |
|---|---|---|
| 3 到 5 个用户故事 | US-1 创建产品想法、US-2 生成并编辑蓝图、US-3 审查并导出方案，共 3 个 | 满足下限 |
| 每个用户故事至少 2 条可测试验收标准 | 每个 US 各 2 条，均为「操作 -> 预期输出」句式，含状态码 | 满足 |
| 错误路径 | `400` 非法创建、`404` 项目不存在、`409` 未生成即审查、`500` 未生成即导出、`502/503` 上游失败 | 满足 |
| 非目标 | PRD 第 5 节 4 类非目标 | 满足 |
| AI capability spike 或最小纵切面 | 两者都有证据 | 满足 |
| 范围能在提交期内完成 | 已实现并通过本地检查 | 满足 |

## Loop Engineering Audit（闭环工程审计）

> 说明：本项目实际发生的两轮闭环分别是「AI 能力边界复审」与「运行时可用性复审」，与手册模板的 `PRD Review` / `SPEC Review` 标签不完全对应。此处按真实发生的内容记录，不套用未发生的标签。

### Loop-1 AI 能力与规格边界复审（2026-07-22）

- Hypothesis（假设）: demo provider 的确定性输出足以证明项目具备真实 AI 能力，SPEC 中的 provider 契约无需再验证。
- Action（行动）: 按 SPEC 第 4 节配置真实 provider，跑完「生成 → 人工编辑 → 审查 → 导出」全链路；生成与审查刻意使用不同上游与不同模型。
- Evidence command or artifact（证据命令或产物）: `AI_PROVIDER=anthropic-compatible` 生成、`AI_PROVIDER=openai-compatible` 审查、`GET /api/projects/{id}/export`；产物 `evidence/real-ai-2026-07-22/`。
- Evidence result（证据结果）: 生成 `200`（`gpt-5.6-sol`，8 板块通过 Blueprint 校验）；审查 `200`（`gpt-5.6-terra`，`needs-revision`，blocking 4 / warning 4 / info 1）；导出 `200`，10455 字节含人工编辑标记与审查结论。过程中 `anthropic-compatible` 上游一度返回 `502/503` 瞬时过载，改用 `openai-compatible` 后一次通过。
- Decision（结论）: demo 不得作为真实能力证据，必须在 README、PRD、DESIGN 与 evidence 索引中显式标注其非真实模型性质；SPEC 的 `502/503` 失败路径被真实上游故障验证为必要，保留「上游失败不伪造成功」约束。
- Next loop（下一轮）: 验证界面在真实环境下是否确实可用，而不只是 API 可用。

### Loop-2 运行时可用性与验收复审（2026-07-23）

- Hypothesis（假设）: API 与测试全绿，则本地页面对使用者可用。
- Action（行动）: 项目本人在浏览器执行人工 UAT，覆盖首页、创建、生成、编辑保存、刷新持久化、审查、导出。
- Evidence command or artifact（证据命令或产物）: `process/uat/launchspec-ai-human-uat-2026-07-23.md`；截图 `evidence/human-uat-2026-07-23/screenshots/`；修复提交 `6b2fe9c`。
- Evidence result（证据结果）: 假设被推翻。发现两个阻塞：①Next 16 默认 Turbopack 无法解析 `next/font/google` 内部模块，清缓存后首页 HTTP `500`；②以 `127.0.0.1` 访问时 dev origin 被拦截，React hydration 未完成，输入与按钮无响应。修复后 health `200`、页面 `demo · 可用`、控制台 0 error、Vitest 6 文件 13 测试通过。
- Decision（结论）: `package.json` 的 `dev`/`build` 固定为 Webpack 模式；`next.config.ts` 仅允许回环开发来源。同时确认「测试全绿」不能替代真人操作验收，修复前截图保留为故障复现证据，不得当作通过截图。
- Next loop（下一轮）: 最终收口——运行完整 `npm run check`、补齐 Gate 与提交文件、补独立真人结对 UAT。

## Pending（未满足项，不得记为通过）

1. **独立真人评审人复述未完成**。手册要求「至少一名其他项目组成员或评审者读完后能复述系统要做什么」。当前只有项目本人自审与不同模型只读审查；不同模型审查的对象是生成的蓝图内容，不等于有人读完本项目 PRD/SPEC 后能复述。需另一位真实评审者补充脱敏标识、日期与复述记录。

- Decision after review（评审后结论）: **修改后通过**。PRD/SPEC 的用户故事、验收标准、错误路径、非目标与 AI 能力探针均已满足并有证据；唯一未满足项为独立真人评审人复述，已如实列为待办。
