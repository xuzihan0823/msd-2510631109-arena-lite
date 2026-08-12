# MSD 短学期实践工作区（2510631109）

此仓库集中保留短学期阶段性任务和提交期自选项目，但两者保持独立目录、独立运行方式和独立过程记录，避免将 `arena-lite` 误当作提交期项目。

## 目录

- 根目录：D01–D11 的 `arena-lite` 跟练项目、过程文档、测试与证据。
- `projects/launchspec-ai/`：提交期自选项目 LaunchSpec AI。它是一个独立的 Next.js 应用，主题为“AI 项目方案生成与审查工作台”，不复用 arena-lite 的业务故事、接口或演示流程。

## 运行与验证

### D01–D11 arena-lite

按照根目录 `README` / `PROCESS.md` 和 Python 环境说明执行。

### LaunchSpec AI

```bash
cd projects/launchspec-ai
npm install
npm run check
npm run uat
npm run dev
```

LaunchSpec 的真实模型适配器、课程过程资产和已知外部 provider 阻塞记录见：

- `projects/launchspec-ai/README.md`
- `projects/launchspec-ai/PROCESS.md`
- `projects/launchspec-ai/evidence/real-ai-2026-07-20/README.md`

## Git 约定

- 使用同一个 Git 历史与 `origin` remote 保存 D01–D11 及 LaunchSpec AI。
- 不提交 `.env*`（除 `.env.example`）、`node_modules`、`.next`、本地运行数据或任何凭据。
- LaunchSpec 的正式 `MSD_GROUP_ID` / `MSD_DELIVERY_ID` 仍待课程公布；不得在提交、文档或 Gate 中编造。
