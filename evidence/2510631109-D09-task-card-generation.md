# D09 任务卡生成记录 - 2510631109

- 学号：2510631109
- 执行时间：2026-07-15 22:36:36 CST
- 项目路径：`/Users/mac/Desktop/短学期实践/msd-work/msd-2510631109-arena-lite`
- 阶段：D09 任务卡与冲刺准备。
- 生成工具：Hermes Agent CLI。
- 生成模型：`gpt-5.6-terra`。
- 生成角色：`pm-2510631109`、`architect-2510631109`、`qa-2510631109`。

## 已读取的输入

- `AGENTS.md`
- `docs/PRD.md`
- `docs/SPEC.md`
- `docs/DESIGN.md`
- `docs/adr/`
- `process/model-roster-2510631109.md`
- `evidence/2510631109-D08-pr.md`

## 生成提示词

```text
请在当前 arena-lite-2510631109 项目中工作，扮演 pm-2510631109、architect-2510631109 和 qa-2510631109。

先阅读 AGENTS.md、docs/PRD.md、docs/SPEC.md、docs/DESIGN.md、docs/adr/ 和 process/model-roster-2510631109.md。

只为 D10 的 US-1（创建对战、匿名查看、盲投）与 US-2（结算、揭盲、ELO、排行榜）拆 6 到 8 张纵切任务卡，写入 process/task_cards/2510631109-sprint-cards.md。

每张卡必须包含：带学号的编号和标题、用户可见增量、修改范围、操作 -> 预期输出的验收标准、先写的失败测试（红）、可复制测试命令与红绿预期、30/45/60/90 分钟工时、依赖关系、风险与处理。每张卡只能覆盖 30 到 90 分钟。

不得写完整业务实现代码，不得新增真实账号、API Key、Token、支付信息或私有 endpoint；结算只能使用 POST /battles/{id}/settle。自动化测试一律 mock 模型适配层。
```

## 生成输出摘要

已创建 `process/task_cards/2510631109-sprint-cards.md`，包含 8 张任务卡：

1. 存储骨架与预置演示数据。
2. ELO 纯函数与确定性边界。
3. Battle 状态机与配对安全规则。
4. 模型适配契约与可控 mock。
5. 创建对战与匿名查看 API。
6. 盲投与重复投票防护 API。
7. 结算、揭盲与 ELO 更新 API。
8. 排行榜与主链路冒烟。

任务卡末尾已包含实现顺序表、6 条风险与缓解清单，以及 D10 的红绿执行规则。每张卡的测试命令显式使用项目 `.venv/bin/python`，避免 macOS 原生终端误用 Conda Python。

## 前置检查与环境观察

D09 前置文件均存在：`docs/PRD.md`、`docs/SPEC.md`、`docs/DESIGN.md`、`evidence/2510631109-D08-pr.md` 和可执行的 `scripts/check.sh`。

直接执行 `scripts/check.sh` 时，当前 shell 解析到 `/opt/miniconda3/bin/python`，并报 `No module named pytest`。这不是项目测试失败：以项目虚拟环境运行

```text
PATH="$PWD/.venv/bin:$PATH" scripts/check.sh
```

实际输出为：`1 passed in 0.25s`、Python syntax check 通过、`git diff --check` 通过、`local checks passed`。

## 安全说明

本记录只引用脱敏的课程演示身份和本地项目路径；不包含真实账号、API Key、Token、支付信息或私有服务地址。未安装依赖、未调用外部模型、未提交、未推送。

## 复核状态

D09 复核记录写入 `evidence/2510631109-D09-task-card-review.md`。用户补充的 Claude Code 交互式只读复核已完成：截图可见 Claude Code 2.1.209、Opus 4.8（1M context）、`reviewer-2510631109` 和 `PASS` 结论。截图已归档为 `evidence/screenshots/2510631109-D09-claude-review.png`；根据其中的非阻断建议，已将 TC-01 至 TC-04 标注为基础层能力增量，并消除 TC-02 的依赖措辞歧义。此前一次无费用的 401 Provider 失败保留在复核记录中，未被误写为成功审查。