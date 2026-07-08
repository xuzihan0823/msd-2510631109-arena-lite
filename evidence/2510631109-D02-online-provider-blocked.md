# D02 在线 Provider 与模型配置说明

- 学号：2510631109
- 日期：2026-07-08 00:28:56 CST
- 平台：macOS 原生终端
- 状态：暂不选用 OpenCode Go 订阅与模型配置；使用已有 Claude Code 生态与自建中转服务作为个人 Provider 路线

## OpenCode Go 配置状态

本次 D02 暂不进行 OpenCode Go 的订阅、购买、登录、API Key 创建或模型配置。

原因说明：

- 当前本机 Claude Code 生态已经完整，可作为主要 AI 编程入口。
- 本机 Claude Code 已配置 skill，并存在可用 MCP。
- 本人已部署模型中转服务，用于对接上游模型渠道；在该使用场景中，Provider 方就是自建服务，因此暂不选用 OpenCode Go 订阅式 Provider。
- 不进行 OpenCode Go 购买或 Key 输入，避免无必要的支付、订阅和密钥管理风险。

因此，本次不提交 OpenCode Go `Provider 已连接` 的结论，也不伪造 OpenCode Go 模型页可用状态。

## Claude Code 生态证据

### Claude Code 版本

执行命令：

```bash
claude --version
```

复核结果摘要：

```text
2.1.196 (Claude Code)
```

### Claude Code MCP 状态

执行命令：

```bash
claude mcp list
```

复核结果摘要：

```text
Checking MCP server health…
js-reverse: npx js-reverse-mcp - ✔ Connected
```

### Claude Code Skill 状态

本机 Claude Code skill 目录：

```text
/Users/mac/.claude/skills
```

复核结果摘要：

```text
Claude Code skills directory exists.
Claude Code skills count: 114
```

## 自建 Provider / 中转服务说明

当前在线模型能力通过自建中转服务接入上游渠道。该路线的特点是：

- Provider 由本人自建和维护。
- 上游模型渠道由自建中转服务统一对接。
- 本课程仓库和证据文件中不记录任何真实 API Key、Token、私有 endpoint 或支付信息。
- 截图和文字记录只展示工具可用状态、模型选择状态或脱敏后的最小调用结果。

最小调用校验字符串：

```text
MSD API OK
```

截图证据：

```text
evidence/screenshots/2510631109-D02-claude-code-provider.png
```

该截图用于证明 Claude Code 可启动、可选择模型，并完成一次脱敏的最小问答校验。截图中如出现模型名或中转服务路线提示，仅作为 Provider 状态说明，不展示任何真实密钥。

## 相关截图

| 截图文件 | 说明 |
|---|---|
| `evidence/screenshots/2510631109-D02-claude-code-provider.png` | Claude Code 生态与自建 Provider 路线的可用状态证明，包含最小校验字符串。 |
| `evidence/screenshots/2510631109-D02-http200.png` | 本地 HTTP 200 验证截图。 |

## 检查结论

- OpenCode Go：本次暂不购买、暂不订阅、暂不配置 Key。
- Claude Code：本机已安装并可运行。
- MCP：存在可连接的 MCP server。
- Skill：本机 Claude Code skill 目录存在，且已有多项 skill。
- 自建 Provider：作为本人维护的模型中转路线使用，但不在证据中暴露任何私密 endpoint 或密钥。

