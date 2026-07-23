# 真实模型 Capability Spike 记录（未通过）

- 日期：2026-07-20
- 项目输入：使用通用、脱敏的“课程项目方案助手”描述；不含真实用户、个人信息、API Key 或支付数据。
- 本机适配器：`AI_PROVIDER=anthropic-compatible`，只读 `CLAUDE_CONFIG_PATH` 指定的 Claude Code profile；未复制或输出 token。

## 已验证

| 步骤 | Profile | 结果 | 说明 |
| --- | --- | --- | --- |
| 本地健康检查 | `~/.claude/settings.json` | `200`, `ready=true` | 配置文件可读取，provider 状态可用 |
| 真实生成 | `~/.claude/settings.json` | `502`（上游 `HTTP 503`） | 服务端上游不可用，未生成 Blueprint |
| 本地健康检查 | `~/.claude/settings.anyrouter.json` | `200`, `ready=true` | 配置文件可读取，provider 状态可用 |
| 真实生成（含 Bearer 认证修正后重试） | `~/.claude/settings.anyrouter.json` | `502`（上游 `HTTP 401`） | profile 对该 Messages API 请求未授权，未生成 Blueprint |

## 结论

本次不能作为“真实 AI capability spike 通过”证据，也没有执行模型审查。应用正确保留了失败状态，没有用 demo 输出替代真实调用结果。

后续需要：用户确认一个仍有效、允许 `/v1/messages` 的 Anthropic-compatible profile，或提供一个经授权的 OpenAI-compatible 本地 `.env.local` 配置；之后重新执行生成和独立审查。
