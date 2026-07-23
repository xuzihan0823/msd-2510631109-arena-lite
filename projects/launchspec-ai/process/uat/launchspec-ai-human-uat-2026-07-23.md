# LaunchSpec AI · 本人人工 UAT 记录 — 2026-07-23

> 结论：**PASS WITH EVIDENCE LIMITS**。项目本人已在本地浏览器中确认当前版本完整可用；本记录不把自动化测试或 AI 会话冒充真人反馈，也不把本人验收冒充未参与开发同伴的独立结对 UAT。

## 1. 基本信息

| 字段 | 内容 |
| --- | --- |
| 测试者 | 徐驰宇（项目本人） |
| 日期与时间 | 2026-07-23 20:51 CST |
| 设备 | macOS 本机；浏览器品牌未在截图中显示 |
| 本地地址 | `http://127.0.0.1:3000` / `http://localhost:3000` |
| 默认模式 | `demo provider`；真实模型运行另有脱敏证据 |
| 真人反馈原文 | “已确定完整可用” |

## 2. 人工验收范围与结果

| 场景 | 实际结果 | 结论 | 证据 |
| --- | --- | --- | --- |
| 打开首页并检查服务状态 | 修复后顶部显示 `demo · 可用`，项目列表加载 3 项 | pass | 浏览器现场验证；`evidence/human-uat-2026-07-23/screenshots/2510631109-demo-generated-workspace.png` |
| 创建脱敏测试项目 | 真实模型证据中的创建请求返回 HTTP `201` | pass | `evidence/human-uat-2026-07-23/screenshots/2510631109-real-provider-generate.png`；`evidence/real-ai-2026-07-22/generate-summary.json` |
| 生成蓝图 | Demo 生成后进入可编辑工作区；真实模型生成 HTTP `200`、项目阶段 `generated` | pass | 两张通过截图及 `evidence/real-ai-2026-07-22/` |
| 编辑、保存与刷新持久化 | 现有浏览器双会话 UAT 已覆盖编辑、保存和刷新持久化；项目本人最终确认当前版本完整可用 | pass with supporting automation | `evidence/pair-uat-2026-07-22/uat_results.json` 的 A-07、A-08、A-11、A-12 |
| 执行审查 | 不同模型审查成功，`source=model`，生成和审查模型不同 | pass | `evidence/real-ai-2026-07-22/review-summary.json` |
| 导出 Markdown | 已有真实模型导出文件，修复后截图可见下载完成辅助提示 | pass | `evidence/real-ai-2026-07-22/export.md`；Demo 工作区截图 |

## 3. 发现、修复与回归验证

### 已发现并修复

1. Next 16 默认 Turbopack 在当前环境无法解析 `next/font/google` 内部模块，导致清缓存后首页 HTTP `500`、浏览器空白。
2. 使用 `127.0.0.1` 访问 Next 16 开发服务时，dev origin 被拦截，导致页面仅有服务端 HTML、React hydration 未完成，输入和按钮不响应。

### 修复

- `package.json`：`dev` 与 `build` 固定为 Webpack 模式。
- `next.config.ts`：仅允许本机回环开发来源 `127.0.0.1`。

### 修复后实测

- `127.0.0.1:3000` health：HTTP `200`，`demo`、`ready=true`。
- 页面状态：`demo · 可用`。
- 项目列表：3 项正常加载。
- “重新生成”：成功，页面显示“已生成可编辑的 demo 草案”。
- 浏览器控制台：0 条 JavaScript error。
- Vitest：6 个测试文件、13 个测试全部通过。
- ESLint：通过。
- `git diff --check`：通过。

## 4. 截图索引与证据边界

| 文件 | 证据含义 |
| --- | --- |
| `screenshots/2510631109-before-fix-initial-state.png` | 修复前故障复现；不能作为通过截图 |
| `screenshots/2510631109-demo-generated-workspace.png` | 修复后 Demo 蓝图生成、可编辑工作区和导出完成辅助提示 |
| `screenshots/2510631109-real-provider-generate.png` | 真实 Provider 就绪、创建 `201`、真实生成 `200` |

## 5. 真人反馈与剩余边界

- 项目本人最终反馈：**已确定完整可用**。
- 当前未提供另一名未参与开发同伴的标识、操作记录和独立反馈，因此本记录是“本人人工 UAT”，不是“独立同伴结对 UAT”。
- 如果课程最终要求同伴/答辩用户签字，仍需另一位真实测试者补充：脱敏标识、日期、一条实际反馈和确认语句。
- 截图和记录中未保存 API Key、Token、密码、Authorization header、私有 endpoint 或支付信息。
