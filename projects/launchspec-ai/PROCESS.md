# LaunchSpec AI · 过程索引

## 项目身份与边界

- 项目名称：LaunchSpec AI
- 正式交付标识：待课程公布 `MSD_GROUP_ID` 后确认，见 `docs/PROJECT-IDENTITY.md`。
- 本地代码目录：`/Users/mac/code/msd-launchspec-ai`
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
- UAT 记录：`process/uat/launchspec-ai-draft-uat.md`
- evidence 索引：`evidence/README.md`
- 健康检查：`GET /api/health`

## 尚待人工完成（不得虚构）

1. 小组 ID / 正式交付 ID 与正式 Gate 文件。
2. 授权的真实模型配置与一次脱敏生成、审查证据。
3. 独立评审人或不同模型的只读审计记录。
4. 同伴/答辩用户的真实 UAT 反馈、最终安全扫描、最终 Git 提交号、两次周志、最终报告和答辩 PPT。
