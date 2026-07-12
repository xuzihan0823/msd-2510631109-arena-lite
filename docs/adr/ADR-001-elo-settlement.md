# ADR-001 - ELO Settlement Timing（ELO 结算时机）- 2510631109

## Status（状态）

Accepted（已接受）

## Context（背景）

arena-lite-2510631109 需要在盲投达到阈值后更新两个 Contestant 的 ELO 与排行榜。M 阶段默认 `required_votes` 为 1，但仍必须区分“记录 vote”和“揭盲并改分”：投票响应不得提前泄露模型身份，且任何重复操作都不能二次改分。

D06 SPEC 已要求 battle 按 `created -> answering -> ready -> voted -> scored` 流转，并规定重复投票、非法状态投票和重复 settle 返回 409。ELO 计算也必须固定为双方 1500、A 胜、K=32 时得到 1516/1484，并保持一次结算只影响本场两个 Contestant。

## Alternatives（备选方案）

1. 在 voter 投票成功时立即更新 ELO，并同时或随后揭盲。
2. 当 `vote_count >= required_votes` 时由系统自动结算 ELO。
3. 保持 battle 在 `voted`，由 admin 调用 `POST /battles/{id}/settle` 后统一揭盲和结算。

## Rejected Options（拒绝方案）

- 拒绝投票时立即更新：Vote、ELO 更新与揭盲被耦合，重复投票、撤销设计或故障恢复时容易出现分散的改分入口；还会削弱匿名投票和显式结算的可观察边界。
- 拒绝自动结算：对 M 阶段而言，自动动作不利于 curl、API 和状态机测试精确观察 `voted -> scored`；一旦后续阈值、异常处理或重试策略变化，也更难定位结算时机。

## Decision（决策）

采用显式 settle：首次有效投票使 battle 从 `ready` 进入 `voted`；只有 admin 调用 `POST /battles/{id}/settle` 时，系统才揭盲、计算并持久化双方 ELO，随后将 battle 转为 `scored`。

settle 是唯一的 ELO 持久化入口。它必须在一个 storage 事务中完成状态检查、读取 Vote、计算 ELO、更新两个 Contestant、更新统计、写入 StatusEvent 与 `voted -> scored`。同一 battle 已 scored 或未达到 `vote_count >= required_votes` 时返回 409，且不得修改 ELO、排行榜或事件记录。

## Consequences（影响）

- 好处：ELO 改分入口唯一；盲投与揭盲边界清楚；D10 可以独立验证 vote 成功但未揭盲、settle 后才改分，以及重复 settle 的 409。
- 代价：投票完成后排行榜不会立即变化；需要 admin 额外执行一次 settle。
- 测试要求：`pytest tests/test_elo.py` 固定 1500 对 1500 的胜、负与最低分用例；`pytest tests/test_api_contract.py` 覆盖 vote 后仍匿名、合法 settle、未投票 settle=409 与重复 settle=409；`pytest tests/test_storage.py` 覆盖 settlement 事务原子性。
- 运行约束：M 阶段使用本地测试 token 与 mock 适配层，不引入真实模型、真实账号或在线付费服务。

## Rollback（回滚方式）

若 D10 的测试或 curl 证据证明显式 settle 阻塞主链路，先保持 `POST /battles/{id}/settle` 路径和 `voted -> scored` 状态契约不变，将其内部实现退化为最小的同步结算流程；不得退回到投票即改分。

若未来产品需要自动结算，应新建一条 ADR，明确幂等键、并发策略、事件重放与失败补偿，并同步修订 PRD、SPEC、DESIGN、测试、D10 验收命令和 UAT；旧 ADR 保留为历史决策记录。