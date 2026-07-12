# ADR-003 - SQLite Storage for the M-Stage（M 阶段 SQLite 存储）- 2510631109

## Status（状态）

Accepted（已接受）

## Context（背景）

arena-lite-2510631109 的 M 阶段需要在一个本地、单进程课程演示中保存 Contestant、Battle、Vote 和 StatusEvent，并保证一次 settle 同时更新 Battle 状态、双方 ELO、统计数据和状态事件。PRD/SPEC 明确不要求生产级高可用、跨进程并发治理、真实外部服务或云数据库。

D10 需要可重复运行的 storage 测试；内存对象无法提供进程重启后的持久性、数据库唯一约束或事务语义，且不能证明 `(battle_id, voter_id)` 的重复投票保护。

## Alternatives（备选方案）

1. 只使用 Python 内存字典。
2. 使用 SQLite 本地文件数据库。
3. 使用 PostgreSQL 或其他独立数据库服务。

## Rejected Options（拒绝方案）

- 拒绝只使用内存字典：实现最短，但没有持久化、数据库唯一约束或真实事务，无法可靠验证 Vote 幂等和 settle 原子性。
- 拒绝 PostgreSQL 或其他独立数据库：需要额外服务、凭据和运维配置，超过单机 M 阶段范围，并增加同学复现实验的成本。

## Decision（决策）

M 阶段的 `storage/` 使用 SQLite。创建可重复初始化的 schema，至少包含 Contestant、Battle、Vote、StatusEvent；对 `(battle_id, voter_id)` 建立唯一约束。settle 使用单个 SQLite 事务完成：检查 `voted` 状态、读取 Vote、计算 ELO、更新两个 Contestant、将 Battle 写为 `scored` 并新增 StatusEvent。

SQLite 仅是内部存储技术；领域层通过仓储接口读取和保存数据，不直接依赖 SQLite 连接、SQL 或 FastAPI。

## Consequences（影响）

- 好处：无需外部服务或凭据，适合课程本机运行；可用唯一约束和事务测试重复投票、重复 settle 与原子性。
- 代价：不以多进程、高并发写入、分布式事务或生产级迁移为目标。
- 测试要求：`pytest tests/test_storage.py` 必须覆盖 schema 初始化、Vote 唯一约束、合法状态迁移写入 StatusEvent、非法迁移不写入事件，以及 settle 对 Battle/ELO/StatusEvent 的原子提交。
- 范围约束：不加入 ORM、远程数据库、账户表或跨服务消息队列；这些均不是 US-1、US-2 的必要条件。

## Rollback（回滚方式）

若 SQLite 在目标环境不可用，保留领域仓储接口与所有 API contract，使用同样实现唯一 Vote 约束和原子 settle 的本地替代存储，并在新的 ADR 中记录替代方案、测试证据和限制。不得回退到无法防止重复投票或无法保证 settle 原子性的纯内存字典实现。