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
- 提交期答辩或独立用户试用仍应覆盖“输入想法 → 生成 → 人工编辑 → 审查 → 导出”完整路径。
- 真实模型 UAT 需要在授权 provider 下执行；记录模型名、时间、脱敏输入摘要和结构化输出摘要，不记录 key。
- 真实同伴反馈与独立模型审查都必须由用户/组员实际完成并留名，不能以 demo 或本代理会话替代。
