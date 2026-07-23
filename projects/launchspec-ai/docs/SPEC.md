# SPEC · LaunchSpec AI MVP

## 1. 运行边界

- Runtime：Next.js App Router，Node.js runtime。
- 存储：默认 `data/launchspec.json`，以临时文件 + rename 原子替换写入。
- AI provider：`demo`（确定性）、`openai-compatible` 或 `anthropic-compatible`（真实模型）。
- 权限：本地 MVP 暂不含登录或多租户；不得暴露到不受信任网络。

## 2. 数据模型

```text
Project
- id: UUID
- name: 2..120 字符
- idea: 20..4000 字符
- stage: draft | generated | reviewed
- blueprint?: Blueprint
- review?: ReviewReport
- createdAt / updatedAt: ISO-8601

Blueprint
- projectTitle, oneSentencePitch, targetUsers, problem, coreScenario
- mvpScope, nonGoals, architecture, aiBoundary: string[]
- acceptanceCriteria: { operation, expected }[]，2..8 项
- risks: { risk, mitigation }[]，1..8 项

ReviewReport
- readiness: ready | needs-revision
- summary
- findings: { id, severity, area, message, recommendation }[]
- source: demo-rules | model
- reviewedAt
```

## 3. API 契约

### `GET /api/health`

- `200`：返回 `{ status: "ok", storage: "local-json", provider: { mode, ready } }`。
- 不返回模型 API Key、endpoint query 或任何环境变量值。

### `GET /api/projects`

- `200`：返回 `{ projects: Project[] }`，按 `updatedAt` 降序。

### `POST /api/projects`

请求：`{ "name": string, "idea": string }`

- `201`：返回 `{ project }`，新项目 `stage=draft`。
- `400`：名称/想法不满足长度或请求不是 JSON 对象。

### `GET /api/projects/{id}`

- `200`：返回 `{ project }`。
- `404`：项目不存在。

### `PUT /api/projects/{id}`

请求：`{ "blueprint": Blueprint }`

- `200`：保存编辑后的蓝图，清除旧审查，`stage=generated`。
- `400`：蓝图字段、数组长度或验收标准不符合约束。
- `404`：项目不存在。

### `POST /api/projects/{id}/generate`

- `200`：返回 `{ project, provider }`；蓝图必须通过服务端结构验证。
- `404`：项目不存在。
- `502/503`：真实模型配置缺失、网络失败、上游失败、返回为空或 JSON 不合法。错误必须明确，不能伪造成功。

### `POST /api/projects/{id}/review`

- `200`：返回 `{ project, reviewer }`。
- `404`：项目不存在。
- `409`：尚未生成蓝图。
- `502/503`：真实模型审查失败或配置缺失。

### `GET /api/projects/{id}/export`

- `200`：`Content-Type: text/markdown; charset=utf-8`，文件含 AI 边界和审查结论。
- `404`：项目不存在。
- `500`：尚未生成蓝图，无法导出。

## 4. Provider 契约

### demo

`AI_PROVIDER=demo` 是默认值；其生成和审查结果固定、可测，并明确标记为 demo/规则检查。

### openai-compatible

```text
AI_PROVIDER=openai-compatible
AI_BASE_URL=https://provider.example/v1
AI_API_KEY=<仅在 .env.local>
AI_MODEL=<provider-model-id>
```

调用 `/chat/completions`，请求结构化 JSON。系统不记录 API Key；上游返回内容先解析 JSON，再执行同一份 `Blueprint`/审查结构验证。

### anthropic-compatible（Claude Code profile 复用）

```text
AI_PROVIDER=anthropic-compatible
CLAUDE_CONFIG_PATH=~/.claude/settings.json
```

运行时从指定 JSON 的 `env` 读取 `ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN` 和 `ANTHROPIC_MODEL`（缺失时回退顶层 `model`），调用 `/v1/messages`。本项目不复制、不记录或返回 token；无法读取 profile、配置字段缺失、上游失败、空内容或无效 JSON 均返回明确错误。
