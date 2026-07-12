# ADR-002 - Battle Status History（Battle 状态留痕）- 2510631109

## Status（状态）

Accepted（已接受）

## Context（背景）

arena-lite-2510631109 的 Battle 有 `created`、`answering`、`ready`、`aborted`、`voted`、`scored` 六类状态。D06 SPEC 要求超时、空回答和 provider 错误进入 `aborted`，非法投票或重复结算返回 409，且这些失败不得改动 ELO 或排行榜。

只保存当前 `Battle.status` 可以支持正常流程，但当需要解释“为什么 aborted”“谁在何时将 ready 变为 voted”“为什么重复 settle 被拒绝”时，无法保留最小审计线索。完整事件溯源又会为 M 阶段引入事件回放、快照、一致性与重放逻辑，超出 US-1、US-2 的交付范围。

## Alternatives（备选方案）

1. Battle 表只保存当前 `status`，不保存状态迁移历史。
2. 仅保存完整事件流，由事件回放计算 Battle 当前状态。
3. Battle 表保存当前 `status`，另用 `StatusEvent` 记录每次合法迁移。

## Rejected Options（拒绝方案）

- 拒绝只存当前 status：不能复查模型超时、空回答或非法迁移前后的状态证据；也难以验证“失败操作不写入新事件”的约束。
- 拒绝完整事件溯源：对 M 阶段而言需要事件版本化、重放、快照和恢复策略，存储与调试成本超过课程最小纵切面，且会挤占 API、ELO 和错误路径的实现时间。

## Decision（决策）

采用“双轨轻量留痕”：Battle 保存当前 `status` 以支持高频查询和领域判断；StatusEvent 保存每次成功的 `from_status`、`to_status`、`at`、`reason`，作为最小审计记录。

领域层先验证迁移合法性，再由 storage 在同一事务内更新 Battle 当前状态并插入 StatusEvent。非法迁移返回 409，不改变 Battle、不写入 StatusEvent。`answering -> aborted` 的 event reason 使用脱敏的 `timeout`、`empty_response` 或 `provider_error` 分类，不写真实 endpoint、Token 或提供方敏感信息。

## Consequences（影响）

- 好处：读取当前状态简单；同时能审查合法迁移顺序、aborted 分类和 ELO 结算前后状态；对 D10/D11 的错误路径证据更友好。
- 代价：每个合法迁移需要多一条写入；storage schema 与事务测试比仅存 status 稍复杂。
- 测试要求：`pytest tests/test_battle_state.py` 覆盖所有合法/非法迁移；`pytest tests/test_storage.py` 覆盖成功迁移写入事件、非法迁移不写事件、settle 时 Battle/ELO/StatusEvent 原子提交；`pytest tests/test_api_contract.py` 覆盖 409 不变性。
- 数据边界：StatusEvent 是调试和课程审计用途，不提供对战回放、用户行为分析或生产级事件溯源功能。

## Rollback（回滚方式）

若 D10 证据表明 StatusEvent 的独立表阻塞最小主链路，可保留 `Battle.status` 作为对外 contract，并把 StatusEvent 写入降级为同一 SQLite 表的简化迁移日志；不得删除对 `aborted` 原因和非法迁移 409 的可观察行为。

任何回滚必须在新的 ADR 中记录触发证据、受影响测试和恢复计划，并同步更新 DESIGN、任务卡和验收命令；不得静默删除已有迁移记录或把失败操作伪装成成功状态。