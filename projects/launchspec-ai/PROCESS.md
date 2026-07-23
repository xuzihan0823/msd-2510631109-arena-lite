# LaunchSpec AI · 过程索引

## 项目身份与边界

- 项目名称：LaunchSpec AI
- 正式交付标识：待课程公布 `MSD_GROUP_ID` 后确认，见 `docs/PROJECT-IDENTITY.md`。
- 本地代码目录：`projects/launchspec-ai/`（本仓库相对路径）
- 当前 provider：默认 `demo`；这不是真实模型调用证据。

## 需求、规格与设计

- PRD：`docs/PRD.md`
- SPEC：`docs/SPEC.md`
- DESIGN：`docs/DESIGN.md`
- ADR-001（本地 JSON）：`docs/adr/ADR-001-local-json-persistence.md`
- ADR-002（模型 provider 边界）：`docs/adr/ADR-002-model-provider-boundary.md`

## 开发过程

- 实现计划：`docs/plans/2026-07-20-launchspec-ai.md`
- 任务卡：`process/task_cards/launchspec-ai-project-cards.md`
- 初始冲刺记录：`process/sprint/launchspec-ai-initial-log.md`

## 验证与证据

- 本地 CI：`scripts/check.sh`（`npm run check`）
- API UAT：`scripts/uat-smoke.sh`（`npm run uat`）
- 自动化 API UAT：`process/uat/launchspec-ai-draft-uat.md`
- 本人人工 UAT：`process/uat/launchspec-ai-human-uat-2026-07-23.md`（结论 `PASS WITH EVIDENCE LIMITS`；不冒充独立同伴反馈）
- 真实模型生成与不同模型审查：`evidence/real-ai-2026-07-22/`
- 人工验收截图：`evidence/human-uat-2026-07-23/screenshots/`
- 浏览器双会话自动化 UAT：`evidence/pair-uat-2026-07-22/uat_results.json`（22/22；不能替代真人同伴反馈）
- evidence 索引：`evidence/README.md`
- 健康检查：`GET /api/health`

## 已完成的提交期证据

1. 脱敏真实模型生成：`gpt-5.6-sol`，HTTP `200`，Blueprint 结构校验通过。
2. 不同模型只读审查：`gpt-5.6-terra`，HTTP `200`，`source=model`，结果为 `needs-revision`。
3. 项目本人人工验收：2026-07-23 确认“已确定完整可用”；截图、测试与证据边界见人工 UAT 记录。

## 尚待人工完成（不得虚构）

1. 小组 ID / 正式交付 ID 与正式 Gate 文件。
2. 如果课程要求独立真人结对：补充一名未参与开发同伴/答辩用户的脱敏标识、日期和真实反馈；本人人工验收不替代该项。
3. 最终安全扫描、最终 Git 提交号、两次周志、最终报告和答辩 PPT。
