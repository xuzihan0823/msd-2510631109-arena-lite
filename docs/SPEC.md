# arena-lite SPEC v1.1 - 2510631109

- 文档状态：SPEC v1.1（provisional contract，临时但明确）
- 项目：`arena-lite-2510631109`
- 范围：集中期 M 阶段，只覆盖 US-1、US-2；不实现业务代码。
- PRD 来源：`docs/PRD.md`
- 参考对齐：`references/arena-lite-参考规格.md`
- 变更原则：D07 已依据课程 D10 主链路将本地鉴权细化为 role test token + Bearer header；D10 起，路径、字段、状态码、ELO 参数和状态迁移只能根据测试日志、接口响应或课程参考证据修订，并同步更新 PRD Traceability。

## 1. 产品范围、角色与非目标

### 1.1 范围

- US-1：admin 发起同题双回答对战，voter 在匿名状态下盲投。
- US-2：投票达到默认阈值后，admin 结算一次，系统揭盲并展示最新 ELO 排行榜。
- 本 SPEC 只定义 D10 可测试的 API、状态、错误路径和边界；不代表当前 `/health` 骨架已经实现这些业务端点。

### 1.2 预置角色

| 角色 | 课程演示标识 | 可执行操作 |
|---|---|---|
| voter | `2510631109-user-demo` | 查看 ready/scored 对战、盲投、查看排行榜 |
| admin | `2510631109-admin-demo` | 发起对战、结算对战 |

用户预置且仅使用演示身份；不提供注册、找回密码、真实账号体系或真实凭据。

### 1.3 非目标

- 不做注册、找回密码、真实账号、真实 API Key、Token、支付信息、私有服务地址或在线计费。
- 不做真实外部模型调用；D10 的适配层场景一律用 mock 进行可复现测试。
- 不做前端美化、回放、防刷、智能体选手、评论、分享、题库后台、多题赛程或并发投票竞态治理。
- 系统不解析或评价回答质量，只记录人类盲投。
- 本阶段不提供 tie、弃投、改票或撤销投票；`draws` 仅为排行榜数据结构和后续扩展保留，初始为 0。

## 2. 领域数据与状态机

### 2.1 最小数据模型

| 实体 | 必需字段 | 约束 |
|---|---|---|
| Contestant | `model_id`、`name`、`elo`、`wins`、`losses`、`draws`、`battles` | 初始 `elo=1500`，最低为 100；示例为 `2510631109-model-alpha`、`2510631109-model-beta` |
| Battle | `battle_id`、`prompt`、`contestant_a_id`、`contestant_b_id`、`answer_a`、`answer_b`、`status`、`required_votes`、`vote_count`、`error_message` | 两名 Contestant 必须不同；M 阶段 `required_votes=1`，初始 `vote_count=0`；示例 battle 为 `2510631109-battle-demo-01` |
| Vote | `battle_id`、`voter_id`、`choice` | `(battle_id, voter_id)` 唯一；`choice` 只能为 `A` 或 `B` |

### 2.2 状态机

```text
created -> answering -> ready -> voted -> scored
answering -> aborted
```

- admin 创建 battle 后，状态从 `created` 进入 `answering`。
- 两个 mock 适配层回答都就绪后，状态进入 `ready`。
- 适配层超时、返回空回答或 Contestant endpoint 不可达时，状态进入 `aborted`，保留 `error_message`，ELO 和榜单不变。
- voter 对 ready battle 的一次有效投票使状态进入 `voted`；投票响应不揭盲。
- 默认投票阈值为 1；达到阈值后，admin 的一次合法 settle 使状态从 `voted` 进入 `scored`，并在此时揭盲、结算 ELO。
- 对 `answering`、`aborted`、`scored` 的投票，以及对 `scored` 的重复 settle，均是非法状态迁移，返回 `409`，不得改状态、ELO 或排行榜。

## 3. 用户故事

### US-1：发起对战并盲投

作为 voter `2510631109-user-demo`，我希望看到同一道题的两个匿名回答，并选择 A 或 B，以便在不知道模型身份的情况下公平比较回答质量。

### US-2：揭盲与排行榜

作为完成投票且对战已 scored 的 voter `2510631109-user-demo`，我希望看到 A/B 对应模型、票数、ELO 变化和排行榜，以便理解盲投的结算结果。

## 4. API provisional contract

| 方法与路径 | 权限 | 请求字段 | 响应字段 | 成功状态码 | 失败状态码 |
|---|---|---|---|---|---|
| `POST /login` | 公开，仅本地测试 | `{ "role": "admin" | "voter" }` | `token`、`role` | `200`；admin 返回 `local-admin-token`，voter 返回 `local-voter-token` | `401` |
| `POST /battles` | admin | 头 `Authorization: Bearer local-admin-token`；体 `prompt`、`contestant_a_id`、`contestant_b_id` | `battle_id`、`status` | `201` | `401`、`422` |
| `GET /battles/{battle_id}` | voter | 路径 `battle_id`；头 `Authorization: Bearer local-voter-token` | ready 时为 `question`、匿名 `answer_a`、匿名 `answer_b`、`status`、`vote_count`、`required_votes`；scored 时额外为 `result`、`votes`、双方 ELO 变化 | `200` | `401`、`404` |
| `POST /battles/{battle_id}/vote` | voter | 路径 `battle_id`；头 `Authorization: Bearer local-voter-token`；体 `choice` | `battle_id`、`vote_id`、`choice`、`vote_count`、`required_votes`、`status=voted`；不含模型身份或 ELO | `200` | `401`、`404`、`409`、`422` |
| `POST /battles/{battle_id}/settle` | admin | 路径 `battle_id`；头 `Authorization: Bearer local-admin-token` | `status=scored`、A/B 身份、票数、双方 `elo_before`、`elo_after`、`elo_delta` | `200` | `401`、`404`、`409` |
| `GET /leaderboard` | voter | 头 `Authorization: Bearer local-voter-token`；可选 query `limit`，默认 20 | `{ "items": [...] }`；每行 `rank`、`model_id`、`name`、`elo`、`wins`、`losses`、`draws`、`battles` | `200` | `401` |

### 4.1 匿名与揭盲约束

- ready 匿名视图不得返回或泄露 `model_id`、`name`、`elo`、`rank`、头像、链接、隐藏文本或其他可推断身份的元数据。
- 同一对 Contestant 多次创建 battle 时，A/B slot 必须随机分配，不能固定位置。
- 只有 battle 进入 `scored` 后，`GET /battles/{battle_id}` 与 settle 成功响应才可以返回 A/B 身份、票数及 ELO 变化。

## 5. 可测试验收标准

所有验收标准均按“操作 -> 预期输出”编写，可直接转换为 D10 先失败的测试。

| 编号 | 操作 | 预期输出 |
|---|---|---|
| AC-1.1 | admin 以非空 `2510631109-example-question-01` 调用 `POST /battles`，并传入两个不同 Contestant | `201` 与 `battle_id`；状态 `created -> answering`；两个 mock 回答就绪后进入 `ready` |
| AC-1.2 | voter 对 ready battle 调用 `GET /battles/{battle_id}` | `200`，返回匿名 `answer_a` / `answer_b`；不含任何身份字段；多次开赛时 A/B 位置不恒定 |
| AC-1.3 | mock 注入适配层超时、endpoint 不可达或空回答 | battle 进入 `aborted`；GET 可见错误原因；ELO、胜负统计和榜单均不变 |
| AC-1.4 | voter 对 ready battle 调用 `POST /battles/{battle_id}/vote`，体为 `{"choice":"A"}` | `200`，状态 `ready -> voted`；同一 voter 重复投票返回 `409`，不产生第二条 Vote |
| AC-1.5 | voter 对 `answering`、`aborted` 或 `scored` battle 投票 | `409` 与状态说明；不改状态、不结算 ELO |
| AC-2.1 | 默认阈值 1 达到后，admin 调用 `POST /battles/{battle_id}/settle` | `200`，状态 `voted -> scored`；返回揭盲身份、票数和双方新 ELO |
| AC-2.2 | 两个 Contestant 初始均为 1500、A 胜、K=32 | A 为 1516，B 为 1484；变化量代数和为 0，任何 ELO 不低于 100 |
| AC-2.3 | voter 调用 `GET /leaderboard`，可传 `limit`，默认 20 | `200`；返回 `{ "items": [...] }`，按 ELO 降序；每行含 `rank`、`model_id`、`name`、`elo`、`wins`、`losses`、`draws`、`battles`；同分按 `model_id` 字典序稳定排序 |
| AC-2.4 | admin 对已 scored battle 再次调用 settle | `409`，状态机拒绝非法迁移，ELO 和榜单不变 |

## 6. 错误路径

所有错误响应使用 JSON 错误结构，示例：

```json
{
  "error": {
    "code": "INVALID_PROMPT_2510631109",
    "message": "prompt 不能为空且长度不得超过 2000"
  }
}
```

| 编号 | 操作 | 可观察预期输出与不变量 |
|---|---|---|
| ERR-1 | 不带或带未知预置身份请求受保护端点 | `401 AUTH_REQUIRED_2510631109`；不改任何业务状态 |
| ERR-2 | 获取不存在的 `2510631109-battle-missing` | `404 BATTLE_NOT_FOUND_2510631109`；不结算 ELO |
| ERR-3 | `POST /battles` 提交空 prompt 或超过 2000 字符的 prompt | `422 INVALID_PROMPT_2510631109`；不创建 battle |
| ERR-4 | `POST /battles` 传入相同 Contestant | `422 SAME_CONTESTANT_2510631109`；不创建 battle |
| ERR-5 | voter 提交 `choice="C"`、空 choice 或缺少 choice | `422 INVALID_CHOICE_2510631109`；不创建 Vote、不结算 ELO |
| ERR-6 | 适配层超时 | battle 进入 `aborted`；GET 显示超时原因；ELO、榜单和胜负统计不变 |
| ERR-7 | 适配层返回空回答 | battle 进入 `aborted`；GET 显示空回答原因；ELO、榜单和胜负统计不变 |
| ERR-8 | Contestant endpoint 不可达 | battle 进入 `aborted`；GET 显示不可达原因；ELO、榜单和胜负统计不变 |
| ERR-9 | 同一 voter 对同一 battle 重复投票 | `409 ALREADY_VOTED_2510631109`；Vote、ELO 和榜单不二次改变 |
| ERR-10 | 对非 ready battle 投票，或对 scored battle 重复 settle | `409 ILLEGAL_STATE_2510631109`；状态、ELO 和榜单不变 |

## 7. ELO 与排行榜规则

- 初始 ELO 为 `1500`，分数下限为 `100`，K 值固定为 `32`。
- 期望胜率：`E_A = 1 / (1 + 10 ^ ((R_B - R_A) / 400))`，`E_B = 1 - E_A`。
- 当 voter 选择 A 时，A 的实际得分为 1，B 的实际得分为 0；选择 B 时对称处理。
- 结算只发生在 `voted -> scored` 的一次合法 settle 中。重复投票、错误投票、失败 battle 或重复 settle 均不结算。
- 使用半入向上取整计算理论胜方增量 `theoretical_delta = round_half_up(32 × (1 - E_winner))`；先计算 `new_loser = max(100, loser_elo - theoretical_delta)`，再计算 `applied_delta = loser_elo - new_loser` 与 `new_winner = winner_elo + applied_delta`。因此胜方变化为 `+applied_delta`、负方变化为 `-applied_delta`，双方变化量代数和恒为 0 且负方不会低于 100。
- 两方同为 1500 且 A 胜时：A 从 1500 变为 1516，B 从 1500 变为 1484。
- 排行榜按 `elo` 降序；同分按 `model_id` 字典序升序稳定排序。

## 8. PRD Traceability

| SPEC 条目 | 对应 PRD 目标、场景或用户故事 |
|---|---|
| 角色、M 阶段范围、非目标 | PRD §3 目标用户与使用场景、§4 产品目标与非目标、§5 产品范围 |
| 状态机、AC-1.1 至 AC-1.5、ERR-1 至 ERR-10 | PRD US-1、§7 核心用户流程、§8.1 匿名规则、§8.2 投票规则、§10 风险 |
| settle、AC-2.1 至 AC-2.4、ELO 与排行榜规则 | PRD US-2、§7 核心用户流程、§8.3 ELO 与排行榜规则、§9 成功指标 |
| 匿名约束与 A/B 随机 | PRD §4.1 匿名目标、§8.1 匿名与揭盲规则、§9 匿名保护指标 |
| 预置身份、无注册、无真实外部模型 | PRD §3.1、§4.2、§10.2 假设 |

## 9. v1.1 修订与变更控制

- SPEC v1 在 `process/spec-review-2510631109.md` 的 Loop-1 中记录了差距：投票即揭盲、缺少创建/settle 边界、正式错误路径不足、排行榜字段不足。
- 本 SPEC v1.1 对齐 `references/arena-lite-参考规格.md`，明确采用 `created -> answering -> ready -> voted -> scored` 与 `answering -> aborted`。
- D07 设计对齐课程 D10 主链路：`POST /login` 接收 role 并返回本地测试 token；受保护端点使用 `Authorization: Bearer`。这不会引入注册、真实账号、密码或真实凭据。
- D10 只能以本 v1.1 的验收标准和错误路径先写测试，再实现满足测试的最小业务代码。
- 若未来测试、接口响应或课程更新证明本契约需要调整，必须在 `process/spec-review-2510631109.md` 中写明原因、证据和受影响的 PRD Traceability。
