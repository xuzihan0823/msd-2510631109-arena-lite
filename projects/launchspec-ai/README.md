# LaunchSpec AI

> 把产品想法转化为可编辑、可审查、可导出的 MVP 项目蓝图。

LaunchSpec AI 面向小型创业团队和项目负责人：输入一段产品想法，生成结构化方案草案，明确 MVP 范围、非目标、验收标准、风险、架构与 AI 使用边界；团队编辑后再执行审查并导出 Markdown。

## 已实现的最小闭环

1. 创建并保存项目想法。
2. 通过 AI provider 生成结构化蓝图。
3. 在界面中编辑并持久化蓝图。
4. 审查范围、非目标、验收标准、风险与人工确认边界。
5. 导出包含审查结论的 Markdown。

默认是确定性的 `demo` provider，便于离线演示、自动化测试和 UAT。它**不是**真实模型运行证据。应用提供 OpenAI-compatible 与 Anthropic-compatible 接口，配置真实模型后可以完成一次脱敏的真实能力验证。

## 本地运行

```bash
npm install
npm run dev
```

打开 http://127.0.0.1:3000 。本地 JSON 数据会写入 `data/launchspec.json`，该文件被 Git 忽略。

## 测试、构建与 UAT

```bash
npm run test     # Vitest 纯逻辑与持久化测试
npm run lint     # ESLint
npm run build    # Next.js 生产构建
npm run check    # 全部检查 + diff/敏感信息扫描
npm run uat      # 启动本地服务并执行 API 主路径 UAT（demo 模式）
```

`npm run uat` 生成本地 UAT 输出到 `evidence/local-uat/`，其中含项目方案内容但不含模型 API Key。提交前请人工检查是否含有不应公开的业务想法或个人信息。

## 真实模型配置

### 方案 A：OpenAI-compatible 服务

1. 复制 `.env.example` 为 `.env.local`。
2. 在 `.env.local` 设置 `AI_PROVIDER=openai-compatible`，并填写 `AI_BASE_URL`、`AI_API_KEY` 与 `AI_MODEL`。

### 方案 B：复用本机 Claude Code provider profile

本机已有 Anthropic-compatible Claude Code profile 时，不需要复制 token 到项目中：

```bash
AI_PROVIDER=anthropic-compatible \
CLAUDE_CONFIG_PATH="$HOME/.claude/settings.json" \
npm run dev
```

也可将 `CLAUDE_CONFIG_PATH` 指向其他 `~/.claude/settings.<provider>.json` profile。应用只读取 `ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN` 和模型名；不会把 token 写入响应、数据文件、证据或仓库。

重启服务后，页面右上角应显示 `anthropic-compatible · 可用`。新建一个脱敏项目并点击“生成蓝图”和“执行审查”；保存命令状态和脱敏响应摘要作为真实模型证据。

不要把 `.env.local`、访问令牌、真实用户数据或支付信息提交进仓库。模型输出始终只是草案，必须由人确认后才能作为项目决策。

## API 概览

| 方法 | 路径 | 作用 |
| --- | --- | --- |
| `GET` | `/api/health` | 查看本地存储与 provider 配置状态 |
| `GET/POST` | `/api/projects` | 列表项目 / 创建项目 |
| `GET/PUT` | `/api/projects/{id}` | 读取项目 / 保存蓝图编辑 |
| `POST` | `/api/projects/{id}/generate` | 生成结构化蓝图 |
| `POST` | `/api/projects/{id}/review` | 执行规则或模型审查 |
| `GET` | `/api/projects/{id}/export` | 下载 Markdown 方案 |

完整契约见 `docs/SPEC.md`；架构与决策见 `docs/DESIGN.md`、`docs/adr/`。

## 项目边界

- 当前是本地优先的单机 MVP，没有账号、权限、支付、多人实时协作或异步队列。
- JSON 文件存储适用于课程演示和小数据量，不适用于多进程并发生产环境。
- 自动化测试使用 demo provider，避免依赖不稳定的真实模型输出。
- 项目仍需要在提交期内以真实模型完成一次脱敏运行，并由另一位项目成员或不同模型完成独立审查。

## 课程过程资产

- `docs/PRD.md`：需求、用户故事和验收标准
- `docs/SPEC.md`：数据与 API 契约
- `docs/DESIGN.md`：模块边界、数据流和测试策略
- `docs/adr/`：架构决策记录
- `process/task_cards/`：开发任务卡
- `process/sprint/`：冲刺记录
- `process/uat/`：UAT 记录
- `PROCESS.md`：评审入口索引

正式提交期命名依赖课程公布的 `MSD_GROUP_ID`。当前待填写项见 `docs/PROJECT-IDENTITY.md`，不会用虚构组号替代。
