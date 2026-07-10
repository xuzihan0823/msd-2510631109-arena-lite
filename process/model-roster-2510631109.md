# Model Roster 2510631109

## Available Models（可用模型）

| Model（模型） | Source（来源） | Capability（能力） | Cost | Latency | Context length | Privacy boundary | Best Role（适合角色） | Allowed data | Forbidden data | Budget cap | Fallback | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gpt-5.6-terra` | Hermes Agent 当前 D05 会话 | 角色定义、任务卡草案、结构化文档和自查 | 使用当前已配置 Provider 额度；本任务不购买、不新增订阅 | 中 | 当前会话可用；具体长度不在本仓库声明 | 脱敏材料会发送到当前配置 Provider | PM、Architect、Dev、QA 的草案生成 | 脱敏后的项目规则、角色、任务卡、测试摘要 | 真实账号、API Key、Token、支付信息、私有 endpoint、未脱敏个人数据 | 不新增付费；若工具要求付费或认证，立即停止等待人工确认 | Claude Code 独立审查；若不可用则记录单模型限制，不宣称多模型完成 | `evidence/2510631109-D05-task-card-review.md` |
| `claude-opus-4-8[1m]`（Opus 4.8，1M context） | Claude Code 2.1.196 的现有自建 Provider 路线 | 独立审查、范围控制、任务卡字段与风险复核 | 使用已有 Provider；本次进行一次交互式只读审查，不新增订阅 | 中 | 1M（Claude Code 模型选择截图可见） | 脱敏材料会发送到 Claude Code 当前 Provider | Reviewer | `roles.md`、项目 skill、model roster、任务卡等脱敏文本 | 真实账号、API Key、Token、支付信息、私有 endpoint、完整个人资料 | 已按交互式会话完成；后续额外调用仍须先确认 | 记录 blocked 原因；改用独立会话复核并注明不是多模型复核 | `evidence/screenshots/2510631109-D02-claude-code-provider.png`；`evidence/screenshots/2510631109-D05-claude-review.png`；`evidence/2510631109-D05-task-card-review.md` |

## Role to Model（角色到模型）

| Role（角色） | Assigned Model（分配模型） | Why（分配理由） | Evidence（证据） |
|---|---|---|---|
| `pm-2510631109` | `gpt-5.6-terra` | 生成第一版任务卡并控制需求范围 | `evidence/2510631109-D05-task-card-review.md` |
| `architect-2510631109` | `gpt-5.6-terra` | 为后续 SPEC、接口契约和错误路径准备结构化草案 | `evidence/2510631109-D05-task-card-review.md` |
| `dev-2510631109` | `gpt-5.6-terra` | 后续从已接受任务卡开始小步实现 | `roles.md`；D10 起的实现证据 |
| `qa-2510631109` | `gpt-5.6-terra` | 整理测试命令、失败路径和证据边界 | `evidence/2510631109-D05-task-card-review.md` |
| `reviewer-2510631109` | `claude-opus-4-8[1m]` | 与生成模型不同，已独立审查任务范围、字段、风险和敏感信息 | `evidence/2510631109-D05-task-card-review.md`；`evidence/screenshots/2510631109-D05-claude-review.png` |

## Constraint（限制说明）

- 本机 Ollama 本地模型在 D02 已如实记录为 blocked，不把它写成可用 reviewer。
- Claude Code 已安装且截图中可见 Opus 4.8；本次只发送脱敏的 D05 文本，并限制为只读审查。
- 2026-07-10 的 headless 调用在单次 US$0.10 上限下尝试 Opus 4.8、GLM 5.2 和 GLM 5.2 low effort，均以 `Exceeded USD budget (0.1)` 拦截；随后已通过 Claude Code 交互式 Opus 4.8 会话完成真实只读复核。详细记录见 `evidence/2510631109-D05-task-card-review.md`。
- 如果 Claude Code 因 Provider 认证、额度或网络不可用而无法审查，必须在 `evidence/2510631109-D05-task-card-review.md` 写明失败原因、影响和补救方式；可用不同 Hermes 会话做补充复核，但不得把该路径写成“多模型复核完成”。
