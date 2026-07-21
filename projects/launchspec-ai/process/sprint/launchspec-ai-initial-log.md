# LaunchSpec AI · 初始冲刺记录

- 日期：2026-07-20
- 范围：从空目录搭建本地可运行的 LaunchSpec AI MVP。
- 工作区：`/Users/mac/code/msd-launchspec-ai`
- 当前运行模式：`AI_PROVIDER=demo`（可测试，不可作为真实模型验收）。

## 已完成的实现动作

1. 初始化 Next.js 16 + TypeScript + Tailwind + ESLint，新增 Vitest。
2. 实现项目、蓝图、审查报告的类型和服务端验证。
3. 实现 JSON 原子持久化、demo/OpenAI-compatible provider、审查规则、Markdown 导出和 API 路由。
4. 实现创建、生成、编辑保存、审查、导出的响应式工作台 UI。
5. 添加纯函数、provider 与 repository 测试；添加全量 check 和本地 API UAT 脚本。
6. 编写 PRD、SPEC、DESIGN、ADR、任务卡、UAT 模板与证据索引。

## 初始验证记录

- `npm run test`：10 个测试通过。
- `npm run lint`：通过。
- `npm run build`：通过，Next.js 路由包含 `/api/health`、项目 CRUD、generate/review/export。
- 上述结果对应 2026-07-20 16:47 CST 的初始构建；脚本与文档新增后需要在最终收官阶段重新运行并把最新输出写入 evidence。

## 已知限制与下一步

- 正式 `MSD_DELIVERY_ID` 未提供，因此 Gate、周志、最终报告和答辩 PPT 命名尚未开始，见 `docs/PROJECT-IDENTITY.md`。
- 本机未发现可用 Ollama 模型；当前没有真实模型调用记录。
- 独立评审人/不同模型审查尚未授权或执行，不能标记为完成。
- 接下来运行 `npm run check` 与 `npm run uat`，确认完整本地链路；随后等待用户提供小组标识和授权真实模型/审查。
