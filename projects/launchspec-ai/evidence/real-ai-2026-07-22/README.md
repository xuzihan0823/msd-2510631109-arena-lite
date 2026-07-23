# LaunchSpec AI 真实模型完整运行记录 — 2026-07-22

本目录记录一次**真实模型**（非 demo）端到端运行证据。所有 API Key、Token、私有服务地址均未写入本目录及仓库。

## 结论

**通过（真实模型完整链路跑通）。** 真实生成 → 人工编辑 → 真实审查 → 导出四个环节全部成功，导出产物包含人工编辑标记与真实模型审查结论。

## 环境

- 项目：`projects/launchspec-ai`（Next.js 16 + 本地 JSON 存储）
- 测试项目 ID：`34c2071a-a3f1-46d3-95e8-02f20a5005d6`
- 测试输入：脱敏的学生需求对齐工具想法（不含个人信息、私有数据、凭据）
- 运行方式：本机 `npm run dev`，逐环节 curl + 浏览器验证

## 各环节结果

| 环节 | Provider 模式 | 模型 | 结果 |
|---|---|---|---|
| 生成蓝图 | `anthropic-compatible` | `gpt-5.6-sol` | HTTP 200，8 个结构板块，通过 Blueprint 校验 |
| 人工编辑 + 保存 + 刷新持久化 | — | — | 浏览器 UAT 通过，标记 `[真人UAT编辑确认-2026-07-22]` 落盘 |
| 审查 | `openai-compatible` | `gpt-5.6-terra` | HTTP 200，`readiness=needs-revision`，9 条 findings，`source=model` |
| 导出 Markdown | — | — | HTTP 200，10455 字节，含人工标记 + 审查结论 |

审查结论概览（详见 `review-summary.json` / `export.md`）：

- 就绪度：`needs-revision`
- findings：blocking 4 / warning 4 / info 1

## 说明与限制

- 生成与审查使用了**不同模型**（生成 `gpt-5.6-sol`，审查 `gpt-5.6-terra`），符合项目“独立评审人 / 不同模型只读审计”的设计意图。
- 生成阶段曾用 `anthropic-compatible` 上游，`gpt-5.6-sol` / `claude-opus-4-8` 审查请求一度因上游 `502/503`（瞬时过载）失败；改用 `openai-compatible` 上游的 `gpt-5.6-terra` 后审查一次通过。这属于上游可用性问题，非项目缺陷。
- 本次审查所用 key 为一次性临时凭据，仅通过环境变量传入运行进程，测试结束即停止服务，未写入任何文件、日志或本记录。
- Step3 浏览器截图为过程性证据，保存在临时目录，未长期留存；人工编辑结果已通过落盘数据与本次导出产物间接佐证。

## 复现要点（不含凭据）

1. `AI_PROVIDER=anthropic-compatible` + `CLAUDE_CONFIG_PATH` 指向含 `ANTHROPIC_BASE_URL/ANTHROPIC_AUTH_TOKEN/ANTHROPIC_MODEL` 的配置 → 生成。
2. 浏览器编辑蓝图字段并保存。
3. `AI_PROVIDER=openai-compatible` + `AI_BASE_URL/AI_API_KEY/AI_MODEL` → 审查。
4. `GET /api/projects/{id}/export` → 导出。
5. `GET /api/health` 应显示对应 provider `ready:true`。
