# LaunchSpec AI · 过程索引

## 项目身份与边界

- 项目名称：LaunchSpec AI
- 正式交付标识：`2510631109-launchspec-ai`（个人提交口径，见 `docs/PROJECT-IDENTITY.md`）
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
- 最终检查证据（2026-08-02）：`evidence/final-check-2026-08-02/check.txt`（`Test Files 6 passed`、`Tests 13 passed`、eslint 无告警、`next build` 成功、`check: passed`）与 `evidence/final-check-2026-08-02/diff-check.txt`（`git diff --check` 无输出）。`scripts/check.sh` 已内置密钥正则扫描，本次未命中。
- API UAT：`scripts/uat-smoke.sh`（`npm run uat`）
- 自动化 API UAT：`process/uat/launchspec-ai-draft-uat.md`
- 本人人工 UAT：`process/uat/launchspec-ai-human-uat-2026-07-23.md`（结论 `PASS WITH EVIDENCE LIMITS`；不冒充独立同伴反馈）
- **独立真人结对 UAT**：`process/uat/launchspec-ai-human-pair-uat-2026-07-29.md`（测试者 TYX，未参与开发；U-03 生成蓝图首次不可用，修复后复测通过，其余 6 项一次通过）
- 真实模型生成与不同模型审查：`evidence/real-ai-2026-07-22/`
- 人工验收截图：`evidence/human-uat-2026-07-23/screenshots/`
- 浏览器双会话自动化 UAT：`evidence/pair-uat-2026-07-22/uat_results.json`（22/22；不能替代真人同伴反馈）
- evidence 索引：`evidence/README.md`
- 健康检查：`GET /api/health`

## 已完成的提交期证据

1. 脱敏真实模型生成：`gpt-5.6-sol`，HTTP `200`，Blueprint 结构校验通过。
2. 不同模型只读审查：`gpt-5.6-terra`，HTTP `200`，`source=model`，结果为 `needs-revision`。
3. 项目本人人工验收：2026-07-23 确认“已确定完整可用”；截图、测试与证据边界见人工 UAT 记录。

## 正式 Gate 与最终提交（2026-08-02 补齐）

- Gate 1 PRD/SPEC 互审：`process/gate/2510631109-launchspec-ai-gate-1-prd-spec.md`（修改后通过；含两轮 Loop Engineering 审计）
- Gate 2 设计审计：`process/gate/2510631109-launchspec-ai-gate-2-design.md`（修改后通过；F-1 缺红绿证据已记录）
- Gate 3 交付审计：`process/gate/2510631109-launchspec-ai-gate-3-delivery.md`（修改后通过）
- 第 1 次周志（W1–W2）：`submissions/2510631109-launchspec-ai-weekly-1.md`
- 第 2 次周志（W3–W4）：`submissions/2510631109-launchspec-ai-weekly-2.md`
- 最终报告：`submissions/2510631109-launchspec-ai-final-report.md`
- 答辩 PPT：`submissions/2510631109-launchspec-ai-defense.pptx`（12 页，含演讲备注；由 `scripts/build-defense-pptx.py` 生成，可重建）

## 尚待人工完成（不得虚构）

1. 若课程要求小组提交，需 `MSD_GROUP_ID` 并按 `docs/PROJECT-IDENTITY.md` 规则改名。
2. 独立评审人对 PRD/SPEC 的复述记录（Gate 1 未满足项）。
3. 测试先行红绿序列：本项目未保留，不可事后补造；后续新增功能时真实执行并留独立的红、绿两次提交。
4. 学院系统周志提交与最终答辩时间。

## 已完成（原待办项）

- 独立真人结对 UAT：2026-07-29 由未参与开发的测试者 TYX 完成，记录见 `process/uat/launchspec-ai-human-pair-uat-2026-07-29.md`。
