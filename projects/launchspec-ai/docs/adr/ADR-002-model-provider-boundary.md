# ADR-002：将 AI 调用封装为 demo、OpenAI-compatible 与 Anthropic-compatible provider 边界

- 状态：已接受
- 日期：2026-07-20

## 背景

课程要求项目具备真实 AI 能力，但自动化测试不能依赖不可控的模型输出。当前机器也未检测到可直接调用的本地 Ollama 模型。

## 决策

定义统一的结构化蓝图和审查契约：

- `AI_PROVIDER=demo`：默认确定性实现，仅用于 UI、测试和离线 UAT。
- `AI_PROVIDER=openai-compatible`：从 `.env.local` 读取 base URL、key 与模型名，调用 `/chat/completions` 并要求 JSON 输出。
- `AI_PROVIDER=anthropic-compatible`：在运行时读取指定的 Claude Code profile，调用 `/v1/messages`；token 不复制进项目。
- 无论 provider，响应都必须经过同一份验证；上游失败不伪造成功。

## 备选方案

1. 把模型请求写在页面组件：实现快，但泄露 Key、测试困难、无法替换 provider。
2. 只实现 demo：可测试但不满足真实 AI 能力的最终证据要求。
3. 直接绑定单一商业 SDK：耦合供应商，且需要把认证/SDK 生命周期引入项目。

## 后果

- 优点：测试稳定，真实调用边界清晰，可接 OpenAI-compatible 服务或已存在的 Claude Code Anthropic-compatible profile。
- 代价：真实模型配置和独立模型审查仍需用户授权；在完成前必须如实标记 pending。
