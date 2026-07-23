# LaunchSpec AI · 本地 API UAT 记录

- 执行时间：2026-07-20。
- 运行模式：demo provider；仅证明应用和 API 链路，不代表真实模型能力。
- 测试客户端：curl（由 `scripts/uat-smoke.sh` 调用）。
- 证据目录：`evidence/local-uat/uat-status.txt`。

| 场景 | 命令/证据 | 预期 | 实际 | 结论 |
| --- | --- | --- | --- | --- |
| Health | `GET /api/health` | `200`，返回 provider 状态 | `200` | passed |
| Invalid create | 短名称/短想法 `POST /api/projects` | `400` | `400` | passed |
| Create | 有效 `POST /api/projects` | `201` + 项目 ID | `201` | passed |
| Generate | `POST /generate` | `200` + Blueprint | `200` | passed（demo） |
| Read | `GET /api/projects/{id}` | `200` | `200` | passed |
| Save | `PUT /api/projects/{id}` | `200` + 修改持久化 | `200` | passed |
| Review | `POST /review` | `200` + 审查结论 | `200` | passed（demo-rules） |
| Export | `GET /export` | `200` + Markdown | `200` | passed |
| Missing project | `GET /api/projects/not-a-real-project` | `404` | `404` | passed |

## 真实模型边界

- `evidence/real-ai-2026-07-20/README.md` 记录了一次脱敏 capability spike：Claude Code profile 可被读取，但两个上游 profile 分别返回 HTTP 503 和 HTTP 401，因此**未通过**，也没有模型审查结果。
- 后续成功路径已于 2026-07-22 完成：`evidence/real-ai-2026-07-22/` 记录真实生成 HTTP `200`、不同模型审查 HTTP `200` 和 Markdown 导出；早期失败记录继续保留，不能重写成成功。
- 项目本人人工验收已于 2026-07-23 完成，记录见 `process/uat/launchspec-ai-human-uat-2026-07-23.md`；结论为 `PASS WITH EVIDENCE LIMITS`。
- 提交期答辩或独立用户试用仍应覆盖“输入想法 → 生成 → 人工编辑 → 审查 → 导出”完整路径。
- 真实模型 UAT 需要在授权 provider 下执行；记录模型名、时间、脱敏输入摘要和结构化输出摘要，不记录 key。
- 不同模型审查已完成；如果课程要求独立真人同伴反馈，仍须由未参与开发者实际完成并留脱敏标识，不能以 demo、自动化浏览器或本代理会话替代。
