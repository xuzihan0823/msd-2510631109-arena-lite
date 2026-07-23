# arena-lite Process Index（过程索引）2510631109

## Environment（环境）

- D01 environment records（D01 环境文字记录）: `evidence/2510631109-D01-env.md`
- D01 workspace records（D01 工作区记录）: `evidence/2510631109-D01-workspace.md`
- D02 model/API evidence（D02 模型/API 证据）: `evidence/2510631109-D02-local-model-blocked.md`、`evidence/2510631109-D02-online-provider-blocked.md`
- Screenshot evidence index（截图证据索引）: `evidence/screenshots/`
- Main run command（主启动命令）: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8124`
- Platform exception（平台说明）: 本项目使用 macOS 26.5.2 原生终端；WSL2/Ubuntu 项目环境记录为 N/A，详见 D01 环境记录。

## Specification and Design（规格与设计）

- PRD: `docs/PRD.md`
- SPEC: `docs/SPEC.md`
- SPEC review（规格复审）: `process/spec-review-2510631109.md`
- DESIGN: `docs/DESIGN.md`
- ADR directory（ADR 目录）: `docs/adr/`
- Reference specification（参考规格）: `references/arena-lite-参考规格.md`

## Sprint Evidence（冲刺证据）

- D03 agent/build evidence（骨架与 Agent 证据）: `evidence/2510631109-D03-0a-agent-prompt.md`、`evidence/2510631109-D03-0b-agent-output.md`、`evidence/2510631109-D03-1-pytest.md`、`evidence/2510631109-D03-2-uvicorn.md`、`evidence/2510631109-D03-3-curl-health.md`
- D04 rules/permission evidence（规则与权限证据）: `AGENTS.md`、`evidence/2510631109-D04-agent-rules.md`
- D05 roles/model roster/skill evidence（角色、模型表与 skill 证据）: `roles.md`、`process/model-roster-2510631109.md`、`process/task_cards/2510631109-d5-task-cards.md`
- D06 PRD/SPEC evidence（需求与规格证据）: `evidence/2510631109-D06-prd-spec-v1-generation.md`、`evidence/2510631109-D06-loop-audit-record.md`、`evidence/2510631109-D06-spec-gate.md`
- D07 design/ADR evidence（设计与 ADR 证据）: `evidence/2510631109-D07-design-gate.md`
- D08 repository and PR/MR evidence（远程仓库与合并请求证据）: `evidence/2510631109-D08-repo.md`、`evidence/2510631109-D08-pr.md`
- D09 task-card evidence（任务卡证据）: `process/task_cards/2510631109-sprint-cards.md`、`evidence/2510631109-D09-task-card-check.md`、`evidence/2510631109-D09-task-card-review.md`
- Sprint log（冲刺日志）: `process/sprint/2510631109-d10-log.md`
- D10 implementation and review evidence（实现与复核证据）: `evidence/2510631109-D10-curl-status.txt`、`evidence/2510631109-D10-check.txt`、`evidence/2510631109-D10-code-review.md`
- UAT record（UAT 记录）: `process/uat/2510631109-uat.md`

## Verification（验证）

- Local CI command（本地 CI 命令）: `scripts/check.sh`
- API smoke evidence（API 冒烟证据）: `evidence/2510631109-D11-uat-status.txt`
- Model failure mock evidence（模型失败 mock 证据）: `evidence/2510631109-D11-model-failure-mock.txt`
- Security scan evidence（安全扫描证据）: `evidence/2510631109-D11-secret-scan.txt`
- D11 verification baseline（D11 验证基线）: `63d071a`；D11 本地验证在该提交的工作树上完成。D11 证据已提交为 `5dc11fb` 并推送至 `origin/feat/2510631109-local-ci`。

## Known Limits（已知限制）

- 项目是单进程、内存 SQLite 的课程 MVP，不处理并发投票竞争。
- 模型回答由 `MockModelAdapter` 生成；不调用真实模型、网络服务、私人 endpoint 或真实凭据。
- 不实现注册、密码、支付、前端美化、题库或并发治理等 D10 非目标。
- 真人结对互访尚未完成；当前 UAT 为自动化 CLI 验收，不能替代未参与开发者的实际使用反馈。

## Presentation Notes（展示备注）

- One decision changed during implementation（实现中变更过的一项决策）: 鉴权从早期草案的自定义演示头收敛为 `POST /login` 返回角色对应的本地演示身份，并对受保护接口统一使用标准 Authorization Bearer 请求头；决策与契约对齐记录见 `process/spec-review-2510631109.md`。
- One test that best proves quality（最能证明质量的一项测试）: `tests/test_api_contract.py::test_vote_settle_and_leaderboard_handle_main_and_error_paths`，覆盖投票、重复投票、错误角色结算、结算、重复结算、结算后投票、ELO 与排行榜排序。
- One AI-generated change reviewed manually（人工复核过的一项 AI 生成修改）: 已完成。本人已对 AI 辅助提交 `71fd253` 的 API、状态机、ELO、存储与测试完成手工确认；独立 AI reviewer 的实质分析与本人确认均记录于 `process/review/2510631109-human-review.md`。全量测试 `22 passed`、目标契约测试 `1 passed`，结论为 `PASS WITH NOTES`。

## Security Note（安全说明）

本索引只引用仓库内已脱敏的记录路径；不包含真实账号、密码、API Key、Token、支付信息、私有服务地址或数据库连接串。
