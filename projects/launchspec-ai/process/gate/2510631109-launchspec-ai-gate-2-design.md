# Gate 2 Design Audit（设计审计）2510631109-launchspec-ai

- Reviewer（评审者）: 徐驰宇（项目本人自审）；**独立设计审计人尚未指派**
- Date（日期）: 2026-08-02
- Delivery ID（交付标识）: 2510631109-launchspec-ai
- Key modules（关键模块）: `src/components/`（工作台 UI）、`src/app/api/`（路由与状态码）、`src/lib/validation.ts`（唯一结构校验点）、`src/lib/repository.ts`（JSON 原子读写）、`src/lib/ai-provider.ts`（三种 provider 边界）、`src/lib/review.ts`（规则审查）、`src/lib/export.ts`（Markdown 导出）
- ADR checked（已检查 ADR）: `docs/adr/ADR-001-local-json-persistence.md`、`docs/adr/ADR-002-model-provider-boundary.md`
- Highest-risk dependency（最高风险依赖）: 外部模型上游。已在 2026-07-22 真实运行中观测到 `anthropic-compatible` 上游返回 `502/503` 瞬时过载；设计上以「失败不降级为假成功」与 demo 兜底测试隔离该风险
- Test strategy summary（测试策略摘要）: 分四层——纯函数（Vitest 覆盖验证、demo 蓝图、规则审查、导出）、存储（临时目录验证原子持久化与排序）、provider（固定 `AI_PROVIDER=demo` 隔离网络与随机性）、API 集成（`scripts/uat-smoke.sh` 用 curl 覆盖 health、非法创建、创建、生成、读取、保存、审查、导出、404），外加 ESLint + `next build`

## Pass Criteria Check（通过标准逐条核对）

| 手册通过标准 | 实际 | 结论 |
|---|---|---|
| DESIGN 能指向 SPEC 的每条核心验收标准 | DESIGN「主数据流」5 步与 SPEC 第 3 节 7 个端点逐一对应；模块职责表标明每条契约的落点 | 满足 |
| ADR 有真实候选方案和取舍 | ADR-001 列 SQLite / PostgreSQL / 内存数组三个候选及代价；ADR-002 列页面内直连 / 只做 demo / 绑定单一商业 SDK 三个候选及代价 | 满足 |
| AI 调用边界、失败路径、重试和预算保护写清楚 | DESIGN「AI 边界与失败策略」7 条：不把输出当真相、demo 标识、缺配置/超时/非 2xx/空内容/无效 JSON 均报错、token 不落盘、Key 不进日志与导出、真实测试只存脱敏摘要。provider 设 30 秒超时（任务卡 C2） | 满足 |
| 测试策略区分纯函数、API/UI 集成、真实模型运行证据 | 三类分离且各有产物：Vitest 13 测试、`uat-smoke.sh` API UAT、`evidence/real-ai-2026-07-22/` 真实模型记录 | 满足 |
| 核心功能遵循测试先行（红绿） | **未满足，见下** | 不满足 |

## Findings（审计发现）

### F-1（阻塞性缺口）核心功能缺少测试先行的红绿证据

手册要求关键接口/算法能从提交历史或过程记录看出「先写失败测试再实现」。本项目不满足：

- 提交 `4414ea4` 一次性引入 79 个文件、11407 行，实现与测试在同一提交中落地，无法区分先后。
- `process/sprint/launchspec-ai-initial-log.md` 记录的是「实现完成后 10 个测试通过」，属于实现后补测试的顺序。
- 与集中期 `arena-lite` 形成对照：后者有 `2030053 add D10 red tests` → `71fd253 implement us1 us2 api slice` 的明确红绿序列，本项目没有对应痕迹。

同时这也触及 `提交期.md:309` 的红线「不用一个巨大提交掩盖过程；提交或 PR 要能对应任务卡」——`4414ea4` 覆盖了 C1–C7 全部七张任务卡，无法逐卡对应。

**影响范围**：评分 rubric「工程实现与质量」（25 分）明确把测试先行红绿证据列为主要证据之一。

**处理计划**：本缺口不可事后伪造——补写一个「先失败的提交」等于伪造历史，属红线。可行的诚实处理是二选一：
1. 在后续仍需修改或新增的功能上，真实执行一次红绿流程并留下独立的红、绿两个提交，作为方法掌握度的证据；
2. 在周志与最终报告中如实声明本项目未保留红绿序列，并以集中期 `arena-lite` 的红绿证据说明该方法已掌握。

当前记录采用第 2 种，并保留第 1 种作为后续可补动作。

### F-2 独立设计审计人未指派

手册的 Gate 2 定位为「设计审计」，期望有互审对象。当前只有项目本人自审，未获得独立审计人。

- Decision after audit（审计后结论）: **修改后通过**。架构、ADR、AI 边界与测试策略四项均满足且有产物支撑；测试先行红绿证据（F-1）确认缺失并已如实记录影响与处理计划，不作为通过项掩盖。
