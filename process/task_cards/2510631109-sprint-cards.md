# D09 冲刺任务卡 - 2510631109

- 项目：`arena-lite-2510631109`
- 阶段：D09 任务卡与冲刺准备；供 D10 按卡测试先行实现。
- 输入：`docs/PRD.md`、`docs/SPEC.md`、`docs/DESIGN.md`、`docs/adr/`。
- 范围：仅 US-1（发起对战并盲投）与 US-2（揭盲、ELO 和排行榜）；不在本文件写业务实现代码。
- 任务卡生成角色：`pm-2510631109` / `architect-2510631109` / `qa-2510631109`。
- 生成模型：Hermes Agent `gpt-5.6-terra`。
- 复核状态：已获用户授权尝试 Claude Code 独立只读复核，但 Provider 返回 `401 无效的令牌`，未产生审查结论；不得声称已完成严格多模型复核。完整阻断记录见 `evidence/2510631109-D09-task-card-review.md`。

## 任务卡

### TC-2510631109-01 - 2510631109 存储骨架与预置演示数据

**学号标识**：2510631109

**用户可见增量**：
- 基础层能力增量：为后续所有接口提供可靠的预置数据、唯一投票约束和事务边界；用户端可见效果在 TC-2510631109-05 至 TC-2510631109-08 串联后体现。

**修改范围**：
- `storage/`：SQLite schema、初始化和仓储读写边界。
- `tests/test_storage.py`：预置数据、读写、Vote 唯一约束与事务边界测试。

**验收标准**：
- 初始化存储 -> 存在 `2510631109-admin-demo`、`2510631109-user-demo`、两个不同的预置 Contestant，初始 ELO 均为 1500。
- 写入同一 `(battle_id, voter_id)` 的第二条 Vote -> 被唯一约束拒绝，第一条 Vote 保持不变。
- 合法结算事务发生异常 -> Battle 状态、双方 ELO 和统计整体回滚，不出现“已 scored 但未改分”或“已改分但仍 voted”。

**先写的失败测试（红）**：
- 先在 `tests/test_storage.py` 写入预置 Contestant 可读取、重复 Vote 被拒绝、结算事务可回滚的断言；此时 `storage/` 尚未实现，测试应先失败。

**测试命令**：
```text
.venv/bin/python -m pytest tests/test_storage.py -q
```
预期：先写时失败（红）；实现后通过（绿），并覆盖预置数据、唯一投票约束和事务回滚。

**预计工作量**：90 分钟

**依赖关系**：无。

**风险与处理**：
- 风险：把领域状态转换或 ELO 公式塞进仓储层，破坏 `storage/` 只读写数据的边界。
- 处理：仓储只保证 schema、唯一约束和原子写入；状态合法性留给 `domain/`，HTTP 状态码留给 `api/`。

### TC-2510631109-02 - 2510631109 ELO 纯函数与确定性边界

**学号标识**：2510631109

**用户可见增量**：
- 基础层能力增量：以独立纯函数固化可解释、可复现的 ELO 规则；用户端的分数变化与排行榜效果在 TC-2510631109-07、TC-2510631109-08 串联后体现。

**修改范围**：
- `domain/elo.py`：期望胜率、半入向上取整、最低分与零和更新纯函数。
- `tests/test_elo.py`：同分、不同分差、A/B 胜、最低分与变化量守恒测试。

**验收标准**：
- 两位 Contestant 初始均为 1500，选择 A -> A 为 1516、B 为 1484，双方变化量代数和为 0。
- 选择 B -> B 获胜且结果与 A 胜的规则对称。
- 负方接近 100 -> 负方不低于 100，胜方仅增加实际扣减的分数，双方变化量仍为 0。

**先写的失败测试（红）**：
- 先在 `tests/test_elo.py` 固化 1500/1500、K=32、A 胜为 1516/1484 的断言，再补 B 胜、低分下限和零和断言；`domain/elo.py` 缺失或行为不符时应失败。

**测试命令**：
```text
.venv/bin/python -m pytest tests/test_elo.py -q
```
预期：先写时失败（红）；实现后通过（绿），且固定样例明确显示 A=1516、B=1484。

**预计工作量**：60 分钟

**依赖关系**：无硬依赖；与 TC-2510631109-01 解耦，可并行或在其后完成，不读取数据库或 HTTP 请求。

**风险与处理**：
- 风险：使用 Python 默认银行家舍入或在最低分边界只截断负方，导致不再零和。
- 处理：按 SPEC §7 的半入向上与“先算负方、再应用实际 delta”规则实现，并用低分边界测试锁定。

### TC-2510631109-03 - 2510631109 Battle 状态机与配对安全规则

**学号标识**：2510631109

**用户可见增量**：
- 基础层能力增量：集中固化 Battle 合法迁移、匿名 A/B 配对和自战拒绝规则；用户端状态反馈在 TC-2510631109-05 至 TC-2510631109-07 串联后体现。

**修改范围**：
- `domain/battle.py`：`created -> answering -> ready -> voted -> scored` 与 `answering -> aborted` 的合法迁移和前置条件。
- `domain/pairing.py`：A/B 随机位置、自战拒绝和投票幂等前置判断。
- `tests/test_battle_state.py`、`tests/test_pairing.py`：合法/非法迁移、A/B 位置、自战与重复操作测试。

**验收标准**：
- 两个 mock 回答成功 -> Battle 从 answering 进入 ready；超时、空回答或提供方异常 -> 进入 aborted 并保留脱敏原因。
- voter 对 ready Battle 首次有效投票 -> 进入 voted；对 answering、aborted 或 scored Battle 投票 -> `409` 的领域错误，状态、ELO 与 StatusEvent 不变。
- 创建 Battle 时传入相同 Contestant -> 拒绝；多次新建 Battle 时可注入确定性分配器分别验证 A/B 两种匿名位置，不允许固定暴露身份。

**先写的失败测试（红）**：
- 先写状态迁移表参数化测试、非法迁移不新增 StatusEvent 的断言，以及同 Contestant 被拒绝、A/B 两种 slot 均可出现的测试；领域模块缺失时应失败。

**测试命令**：
```text
.venv/bin/python -m pytest tests/test_battle_state.py tests/test_pairing.py -q
```
预期：先写时失败（红）；实现后通过（绿），非法操作的领域结果可由 API 层映射为 HTTP 409 或 422。

**预计工作量**：90 分钟

**依赖关系**：依赖 TC-2510631109-01 的 Battle/StatusEvent 持久化接口约定；不依赖 HTTP 路由。

**风险与处理**：
- 风险：把状态判断分散到 API 或仓储，导致重复 vote/settle 在不同入口表现不一致。
- 处理：所有迁移先集中在 `domain/battle.py`；仓储只在领域确认合法后写 StatusEvent。

### TC-2510631109-04 - 2510631109 模型适配契约与可控 mock

**学号标识**：2510631109

**用户可见增量**：
- 基础层能力增量：为后续 API 提供可控 mock 与统一失败分类，确保自动化测试不依赖外部模型；用户端成功或 aborted 状态在 TC-2510631109-05 串联后体现。

**修改范围**：
- `adapters/`：统一 `ask(contestant, prompt, timeout_seconds) -> ModelAnswer` 契约和错误分类。
- `tests/test_model_adapter.py`：mock 成功、timeout、empty_response、provider_error 测试。
- 与 `domain/battle.py` 的最小集成点：将非成功回答归一化为 aborted 原因。

**验收标准**：
- 注入两个成功 mock -> 返回各自的非空 `ModelAnswer`，可供 Battle 进入 ready。
- 注入 timeout、空回答或 provider_error -> 返回可分类的错误结果，Battle 进入 aborted，ELO、Vote、排行榜与胜负统计均不改变。
- 自动化测试 -> 全部 mock，不请求真实模型、在线服务、真实账号或私有 endpoint。

**先写的失败测试（红）**：
- 先在 `tests/test_model_adapter.py` 写成功和三种失败 mock 的断言，并在状态机测试中断言失败会进入 aborted；适配层缺失时应失败。

**测试命令**：
```text
.venv/bin/python -m pytest tests/test_model_adapter.py tests/test_battle_state.py -q
```
预期：先写时失败（红）；实现后通过（绿），且测试日志不依赖任何外部模型服务。

**预计工作量**：60 分钟

**依赖关系**：依赖 TC-2510631109-03 的 aborted 状态与原因记录契约。

**风险与处理**：
- 风险：测试偷偷依赖本机模型或网络，导致课堂环境不可复现。
- 处理：所有测试只注入 mock；真实模型调用不属于 D10 自动化验收范围，只能另做脱敏文字证据。

### TC-2510631109-05 - 2510631109 创建对战与匿名查看 API

**学号标识**：2510631109

**用户可见增量**：
- admin 能发起同题双回答对战；voter 能在 ready 状态看到题目和匿名回答 A/B，但看不到模型身份、ELO 或名次。

**修改范围**：
- `api/`：本地测试身份、`POST /login`、`POST /battles`、`GET /battles/{battle_id}` 的请求/响应 DTO 和错误映射。
- `domain/`、`storage/`、`adapters/` 的已有接口集成。
- `tests/test_api_contract.py`：登录、创建、匿名 GET、401/404/422 与匿名字段测试。

**验收标准**：
- admin 使用有效本地测试身份，提交非空 prompt 和两个不同 Contestant -> `POST /battles` 返回 `201`、`battle_id` 与 `answering`；两份 mock 回答就绪后可查看 ready 状态。
- voter 获取存在的 ready Battle -> `200`，含 `question`、`answer_a`、`answer_b`、`status`、`vote_count`、`required_votes`；不含 `contestant_a_id`、`contestant_b_id`、`model_id`、`name`、`elo` 或 `rank`。
- 缺失/错误身份 -> `401`；不存在 Battle -> `404`；空/超长 prompt 或相同 Contestant -> `422`，且不创建 Battle。

**先写的失败测试（红）**：
- 先写 API contract 测试，断言 `POST /login` 仅接受演示角色、创建成功为 201、ready GET 绝不泄露身份字段，并覆盖 401/404/422；路由不存在时测试应失败。

**测试命令**：
```text
.venv/bin/python -m pytest tests/test_api_contract.py -q -k "login or create_battle or anonymous_view or auth or invalid_prompt or same_contestant"
```
预期：先写时失败（红）；实现后通过（绿），匿名响应中不存在身份、ELO 和排名字段。

**预计工作量**：90 分钟

**依赖关系**：依赖 TC-2510631109-01、TC-2510631109-03、TC-2510631109-04。

**风险与处理**：
- 风险：DTO 或隐藏字段间接泄露 Contestant 身份，导致盲投失效。
- 处理：API 测试同时断言必需匿名字段存在与禁止字段完全缺失；只在 scored 响应中创建揭盲 DTO。

### TC-2510631109-06 - 2510631109 盲投与重复投票防护 API

**学号标识**：2510631109

**用户可见增量**：
- voter 可以对 ready 对战选择 A 或 B 完成一次盲投；再次提交同一对战会被明确拒绝，且投票响应不会提前揭盲。

**修改范围**：
- `api/`：`POST /battles/{battle_id}/vote` 路由、voter 权限与错误映射。
- `domain/battle.py`、`domain/pairing.py`、`storage/`：choice 校验、ready -> voted、一次性 Vote 约束。
- `tests/test_api_contract.py`、`tests/test_storage.py`：首次投票、重复投票、非法 choice、非法状态与不变量测试。

**验收标准**：
- voter 对 ready Battle 提交 choice A 或 B -> `200`，返回 `battle_id`、`choice`、`vote_count=1`、`required_votes=1`、`status=voted`，不包含模型身份或 ELO。
- 同一 voter 对同一 Battle 第二次投票 -> `409 ALREADY_VOTED_2510631109`，仅保留一条 Vote，不修改 ELO 或排行榜。
- choice 为空、缺失或为 C -> `422`；对 answering、aborted 或 scored Battle 投票 -> `409`，均不改变状态或结算。

**先写的失败测试（红）**：
- 先写 ready Battle 首次投票成功、同用户重复投票 409、非法 choice 422、非 ready 投票 409 的 API 测试；投票路由缺失或错误时应失败。

**测试命令**：
```text
.venv/bin/python -m pytest tests/test_api_contract.py tests/test_storage.py -q -k "vote or already_voted or invalid_choice or illegal_state"
```
预期：先写时失败（红）；实现后通过（绿），重复操作前后的 Vote 数、ELO 和排行榜快照一致。

**预计工作量**：60 分钟

**依赖关系**：依赖 TC-2510631109-01、TC-2510631109-03、TC-2510631109-05。

**风险与处理**：
- 风险：只在 API 内存中判断重复，重启或多入口调用后仍可能重复写入。
- 处理：领域层做幂等前置判断，仓储层以 `(battle_id, voter_id)` 唯一约束兜底；失败路径不触发 ELO。

### TC-2510631109-07 - 2510631109 结算、揭盲与 ELO 更新 API

**学号标识**：2510631109

**用户可见增量**：
- 在有效盲投达到阈值后，admin 可以结算对应 Battle；用户能看到 A/B 的模型归属、票数和双方 ELO 前后变化，且每场只结算一次。

**修改范围**：
- `api/`：`POST /battles/{battle_id}/settle` 与 scored 查看响应。
- `domain/battle.py`、`domain/elo.py`：`voted -> scored` 前置条件和一次性结算。
- `storage/`：Battle、StatusEvent、Contestant ELO/统计的同一事务更新。
- `tests/test_api_contract.py`、`tests/test_elo.py`、`tests/test_storage.py`：揭盲、1516/1484、重复 settle 和回滚测试。

**验收标准**：
- admin 对已达到 `required_votes=1` 的 voted Battle 调用 `POST /battles/{battle_id}/settle` -> `200`、`status=scored`，返回 A/B 身份、票数、`elo_before`、`elo_after`、`elo_delta`。
- 双方初始为 1500、A 获胜 -> A=1516、B=1484；胜方增加、负方减少、变化量代数和为 0。
- 未投票 Battle 或已 scored Battle 调用 settle -> `409 ILLEGAL_STATE_2510631109`；状态、ELO、排行榜、统计与 StatusEvent 不二次改变。

**先写的失败测试（红）**：
- 先写 voted Battle 结算并揭盲、1500/1500 固定结果、未投票和重复 settle 的 409、事务不二次改分测试；settle 路由尚未实现时应失败。

**测试命令**：
```text
.venv/bin/python -m pytest tests/test_api_contract.py tests/test_elo.py tests/test_storage.py -q -k "settle or scored or reveal or elo"
```
预期：先写时失败（红）；实现后通过（绿），且重复 settle 前后的 ELO 快照相同。

**预计工作量**：90 分钟

**依赖关系**：依赖 TC-2510631109-01、TC-2510631109-02、TC-2510631109-03、TC-2510631109-06。

**风险与处理**：
- 风险：把结算做成没有 Battle ID 的独立端点，或状态与 ELO 分开写入，造成契约漂移和部分更新。
- 处理：唯一结算入口固定为 `POST /battles/{id}/settle`；在同一事务中处理状态、事件、ELO 和统计，失败整体回滚。

### TC-2510631109-08 - 2510631109 排行榜与主链路冒烟

**学号标识**：2510631109

**用户可见增量**：
- voter 能查看按当前 ELO 排序的榜单，并通过一次端到端主路径确认“创建 -> 匿名查看 -> 投票 -> 结算 -> 排行榜”完整可观察。

**修改范围**：
- `api/`：`GET /leaderboard`、limit 参数、voter 权限和响应 DTO。
- `storage/`：按 ELO 降序、同分按 `model_id` 字典序的稳定查询。
- `client/`：如 DESIGN 所述的最小 CLI 或页面展示入口；若无独立 client，实现等价的 API 冒烟脚本。
- `tests/test_api_contract.py`、`tests/test_client_smoke.py`、`scripts/check.sh`：排行榜和端到端回归。

**验收标准**：
- voter 请求 `GET /leaderboard` -> `200`，返回 `{ "items": [...] }`；每项含 `rank`、`model_id`、`name`、`elo`、`wins`、`losses`、`draws`、`battles`。
- ELO 不同 -> 按 ELO 降序；ELO 相同 -> 按 `model_id` 字典序升序；`limit` 缺省为 20。
- 使用 mock 完成创建、匿名查看、首次投票、admin settle、排行榜查询 -> 全量测试和 `scripts/check.sh` 通过；主路径不调用真实模型或外部服务。

**先写的失败测试（红）**：
- 先写排行榜字段、降序、同分稳定排序、limit 和未鉴权 401 测试，再写主链路 smoke 测试；排行榜路由未实现时应失败。

**测试命令**：
```text
.venv/bin/python -m pytest tests/test_api_contract.py tests/test_client_smoke.py -q
PATH="$PWD/.venv/bin:$PATH" scripts/check.sh
```
预期：先写时失败（红）；实现后通过（绿），`scripts/check.sh` 输出 `local checks passed`。

**预计工作量**：90 分钟

**依赖关系**：依赖 TC-2510631109-01、TC-2510631109-02、TC-2510631109-05、TC-2510631109-06、TC-2510631109-07。

**风险与处理**：
- 风险：排行榜只排序不稳定，或冒烟测试依赖真实模型/网络，导致展示和回归不可复现。
- 处理：将同分排序写成确定性测试；主链路统一使用 TC-2510631109-04 的 mock 适配层。

## 实现顺序表

| 顺序 | 任务 | 原因 |
|---|---|---|
| 1 | TC-2510631109-01 存储骨架与预置演示数据 | 后续模块需要可靠的预置用户、Contestant、Battle、Vote 和事务入口。 |
| 2 | TC-2510631109-02 ELO 纯函数与确定性边界 | 独立于 HTTP/SQLite，可先用 TDD 固化 1516/1484 与最低分规则。 |
| 3 | TC-2510631109-03 Battle 状态机与配对安全规则 | 先确定合法迁移、409 前置条件和匿名 A/B 分配边界。 |
| 4 | TC-2510631109-04 模型适配契约与可控 mock | 让 API 测试不依赖真实模型、网络或私有配置。 |
| 5 | TC-2510631109-05 创建对战与匿名查看 API | 覆盖 US-1 的“发起 -> 匿名查看”前半段。 |
| 6 | TC-2510631109-06 盲投与重复投票防护 API | 覆盖 US-1 的投票后半段与幂等错误路径。 |
| 7 | TC-2510631109-07 结算、揭盲与 ELO 更新 API | 覆盖 US-2 唯一结算入口和可解释分数变化。 |
| 8 | TC-2510631109-08 排行榜与主链路冒烟 | 从用户视角串起完整链路并完成全量回归。 |

## 风险与缓解清单

| 风险 | 影响 | 缓解方式 |
|---|---|---|
| 真实模型慢、不可用或需要凭据 | D10 API 测试不稳定，且可能泄露或消耗外部资源 | 适配层自动化测试全部 mock；真实模型不作为通过条件。 |
| A/B 匿名字段或 slot 泄露身份 | 盲投失效，用户受模型品牌影响 | ready DTO 禁止身份、ELO、rank 字段；配对和 API 测试分别覆盖。 |
| 重复 vote 或重复 settle | ELO 被二次放大，排行榜失真 | `(battle_id, voter_id)` 唯一约束、状态机 409 和同一事务结算三重保护。 |
| ELO 公式、取整或最低分处理错误 | 结果不可解释或不再零和 | TDD 固化 1500/1500 的 1516/1484、B 胜、低分下限与总变化量守恒。 |
| 单张任务卡过大或跨越层级过多 | D10 无法小步测试、排错成本升高 | 所有卡限定 60 或 90 分钟；若实现时超时，拆为同一验收链路的相邻卡。 |
| 接口契约漂移 | D10 实现、curl 与 D11 UAT 不一致 | 结算唯一使用 `POST /battles/{id}/settle`；变更先同步 SPEC、DESIGN、测试与追溯记录。 |

## D10 开工规则

- 每次只处理一张任务卡；先创建本卡的失败测试（红），确认失败原因与 SPEC 一致后再实现到通过（绿）。
- 完成每张卡后运行本卡测试命令和 `git diff --check`；业务实现、测试结果和提交记录不得提前写成已经完成。
- 所有自动化测试使用脱敏预置数据与 mock；不得加入真实账号、API Key、Token、支付信息或私有 endpoint。
