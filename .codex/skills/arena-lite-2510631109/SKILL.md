---
name: arena-lite-project-2510631109
description: Workflow for the arena-lite course project.
---

# arena-lite Project Skill - 2510631109

在学号为 2510631109 的 arena-lite 项目目录内工作时使用本 skill。

本 skill 覆盖角色、任务卡、PRD、SPEC、DESIGN、ADR、FastAPI 测试、安全检查和证据记录。

## Required Context（必读上下文）

- 修改前先阅读 `AGENTS.md`。
- 分配或复核任务时阅读 `roles.md`。
- 选择模型、分配角色或发送材料前先阅读 `process/model-roster-2510631109.md`。
- 路径、分支名、任务卡、文字记录、报告和提交信息都必须包含 `2510631109`。

## Safety（安全边界）

- 不得把真实账号、API Key、Token、支付信息或私有服务地址写入仓库、截图或文字记录。
- 安装新依赖、使用付费在线额度、删除文件、提交、推送或发布前，必须先获得人工确认。
- 未经同学明确确认，不读取或修改当前 arena-lite 项目目录之外的文件。
- 使用在线模型时，只发送脱敏后的必要文件片段；如果模型要求认证、付费或访问额外资料，先停止并报告。

## Workflow（工作流程）

- 实现前先把请求拆成小任务卡。
- 每次 Agent 工作前先指定角色和模型；生成与复核优先使用两个不同模型。
- 记录模型选择、预期优势、可发送数据、预算上限，以及该角色为什么使用该模型。
- 每张任务卡必须包含 Role、Context、Task、User Value、Acceptance Criteria、Test Command、Non-goals、Risk 和 Estimated Effort。
- 只从已接受的任务卡开始实现。
- 每次修改后运行相关测试命令，并报告关键输出。
- 优先小步提交，并留下清晰证据。

## D05 Boundary（D05 边界）

- D05 只建立角色、项目级 skill、model roster 和任务卡，不新增主要业务功能。
- 第一版任务卡生成后，必须由不同模型的 reviewer 给出只读审查结论。
- reviewer 只提出需要修改之处；修改任务卡后保留生成 prompt、review prompt、模型和最终结论到 `evidence/2510631109-D05-task-card-review.md`。
