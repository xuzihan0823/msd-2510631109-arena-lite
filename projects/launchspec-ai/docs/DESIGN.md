# DESIGN · LaunchSpec AI

## 架构概览

```text
浏览器（React Client Workspace）
  ├─ GET/POST /api/projects
  ├─ POST /api/projects/{id}/generate
  ├─ PUT /api/projects/{id}
  ├─ POST /api/projects/{id}/review
  └─ GET /api/projects/{id}/export
             │
Next.js Route Handlers（Node.js runtime）
  ├─ validation / error mapping
  ├─ repository（JSON 原子写入）
  ├─ AI provider adapter（demo / OpenAI-compatible / Anthropic-compatible）
  ├─ review engine
  └─ Markdown exporter
             │
       data/launchspec.json
```

## 模块职责

| 模块 | 职责 |
| --- | --- |
| `src/components/` | 本地工作台、项目列表、蓝图编辑器和审查面板 |
| `src/app/api/` | HTTP 状态码、请求路由和安全错误响应 |
| `src/lib/validation.ts` | 输入和模型 JSON 的单一结构校验点 |
| `src/lib/repository.ts` | JSON 读写、UUID、按更新时间排序 |
| `src/lib/ai-provider.ts` | demo、OpenAI-compatible 与 Claude profile 复用的 Anthropic-compatible provider；不记录密钥 |
| `src/lib/review.ts` | 可重复的范围/验收/非目标/AI 边界规则检查 |
| `src/lib/export.ts` | 统一的 Markdown 导出格式 |

## 主数据流

1. 用户创建项目，路由校验 `name`/`idea` 后写入本地 JSON。
2. 用户生成蓝图；provider 返回 JSON 后必须通过 `validateBlueprint` 才能保存。
3. 用户编辑蓝图；保存时再次校验，旧审查结果被清除，避免审查与内容不一致。
4. 用户执行审查；demo 返回规则结论，真实 provider 返回模型结论并做格式验证。
5. 导出端点从当前项目生成 Markdown，不接收客户端注入的导出内容。

## AI 边界与失败策略

- 不把模型输出作为真相、最终决策、市场事实或法律建议。
- `demo` 只服务于测试和演示，UI 与 API 均会标识其非真实模型性质。
- `openai-compatible` 或 `anthropic-compatible` 缺少配置、超时、网络失败、HTTP 非 2xx、空内容和无效 JSON 都返回错误；不降级为“假成功”。
- `anthropic-compatible` 只在运行时读取用户指定的 Claude Code profile，不把 token 复制到 `.env.local`、数据文件或日志。
- API Key 只从运行时环境读取，不出现在日志、数据文件、响应或导出文件中。
- 真实模型测试只保存脱敏输入摘要、状态、模型 ID 和输出结构摘要。

## 测试策略

| 层级 | 覆盖方式 |
| --- | --- |
| 纯函数 | Vitest 测试验证、demo 蓝图、规则审查、Markdown 导出 |
| 存储 | Vitest 使用临时目录验证原子持久化与排序 |
| provider | Vitest 固定 `AI_PROVIDER=demo`，避免测试依赖网络和模型随机性 |
| API 集成 | `scripts/uat-smoke.sh` 启动本地服务，用 curl 覆盖健康检查、非法创建、创建、生成、读取、保存、审查、导出、404 |
| 构建 | ESLint + `next build` |

## 可扩展性（不在当前 MVP）

把 `repository.ts` 替换为 SQLite/PostgreSQL adapter、把本地单机访问增加身份认证和多租户边界、将 provider 调用迁移到队列。这些不是当前课程 MVP 的实现范围。
