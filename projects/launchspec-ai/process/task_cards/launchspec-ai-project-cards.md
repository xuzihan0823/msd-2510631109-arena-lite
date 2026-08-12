# LaunchSpec AI · 项目任务卡

> 正式提交期文件名待 `MSD_DELIVERY_ID` 确认后迁移。本卡记录当前实现的纵切面，不把计划测试写成已通过。

## C1 · 项目想法与本地持久化

- Role：developer
- Context：用户需要从一句想法开始，刷新后仍能找到项目。
- Task：实现项目创建、JSON 原子写入、按更新时间读取和 `GET/POST /api/projects`。
- User Value：团队不再丢失最初的项目问题定义。
- Acceptance Criteria：有效名称/想法创建返回 `201`；无效输入返回 `400`；刷新后可读取已创建项目。
- Test Command：`npm run test -- src/lib/repository.test.ts`，预期 green；`npm run uat` 中检查 `create_project=201`。
- Non-goals：账号、多人并发、数据库迁移。
- Risk / response：JSON 损坏或并发写入；使用临时文件 + rename，明确仅限单机 MVP。
- Estimated Effort：2h；Dependencies：无。

## C2 · 结构化蓝图生成

- Role：AI integration developer
- Context：产品想法必须转换为可编辑、可测试的结构而不是一段长文。
- Task：实现 demo/OpenAI-compatible provider、Blueprint 结构验证和生成路由。
- User Value：用户立即获得范围、风险、验收和 AI 边界草案。
- Acceptance Criteria：demo 生成返回完整 Blueprint；真实 provider 配置缺失时明确报错而非假成功；无效模型 JSON 不入库。
- Test Command：`npm run test -- src/lib/ai-provider.test.ts src/lib/blueprint.test.ts`，预期 green。
- Non-goals：自动执行方案、生成完整业务代码、供应商计费。
- Risk / response：上游不稳定；30 秒超时、格式验证、脱敏错误提示。
- Estimated Effort：3h；Dependencies：C1。

## C3 · 蓝图编辑与保存

- Role：frontend developer
- Context：模型草案必须可被项目成员主动修改。
- Task：实现表单编辑器和 `PUT /api/projects/{id}`。
- User Value：团队能将泛化草案收敛成自己的可交付范围。
- Acceptance Criteria：可修改问题、范围、非目标、验收、风险、架构、AI 边界；保存后重新读取仍一致；保存会清除过期审查结论。
- Test Command：`npm run uat` 中检查 `save_blueprint=200`。
- Non-goals：多人实时编辑和版本 diff。
- Risk / response：编辑破坏结构；服务端重复执行 Blueprint 校验并返回 `400`。
- Estimated Effort：3h；Dependencies：C1、C2。

## C4 · 方案审查

- Role：reviewer
- Context：范围、非目标和验收标准经常被遗漏。
- Task：实现可重复规则检查与可选模型审查 provider。
- User Value：在设计/开发前发现范围膨胀和不可测试需求。
- Acceptance Criteria：缺少非目标或少于两条验收标准时返回 `needs-revision`；完整 demo 蓝图返回 `ready`；demo 来源明确为 `demo-rules`。
- Test Command：`npm run test -- src/lib/review.test.ts`，预期 green；`npm run uat` 中检查 `review_blueprint=200`。
- Non-goals：把同一模型会话伪装成独立审查。
- Risk / response：模型审查格式不稳定；验证 JSON 并要求不同模型/人工补充正式审查。
- Estimated Effort：2h；Dependencies：C2、C3。

## C5 · Markdown 导出

- Role：developer
- Context：团队要将已经确认的内容带入仓库文档和后续 Gate。
- Task：将当前项目、AI 边界和审查结论导出为 Markdown。
- User Value：方案可以被后续 PRD/SPEC/报告引用而非困在网页中。
- Acceptance Criteria：已生成蓝图导出返回 `200` 和 Markdown；内容包括验收标准和 AI 使用边界；未生成蓝图不伪造导出。
- Test Command：`npm run test -- src/lib/export.test.ts`，预期 green；`npm run uat` 中检查 `export_markdown=200`。
- Non-goals：PDF/PPT 自动生成。
- Risk / response：导出与已审查内容漂移；导出只读取当前持久化项目。
- Estimated Effort：1.5h；Dependencies：C3、C4。

## C6 · 本地质量门禁与 API UAT

- Role：QA
- Context：不能用“页面看起来正常”代替可复查交付。
- Task：编写 Vitest、`scripts/check.sh`、`scripts/uat-smoke.sh` 和 evidence 索引。
- User Value：他人可复现主路径和典型错误路径。
- Acceptance Criteria：test/lint/build 通过；UAT 覆盖 health、非法创建、创建、生成、读取、保存、审查、导出、404；密钥扫描无命中。
- Test Command：`npm run check && npm run uat`，预期退出码 `0`。
- Non-goals：E2E 浏览器自动化和线上性能压测。
- Risk / response：demo 误当模型证据；日志写明 `provider=demo (not real model evidence)`。
- Estimated Effort：2.5h；Dependencies：C1–C5。

## C7 · 课程过程资产与人工收官

- Role：PM / QA
- Context：应用完成不等于课程交付完成。
- Task：维护 PRD、SPEC、DESIGN、ADR、PROCESS、UAT、Gate 与正式提交文件索引。
- User Value：评审能定位决策、命令和证据，答辩能解释 AI 边界。
- Acceptance Criteria：文档能互相链接；没有虚构组号、真实模型运行或独立审查；提供待人工确认清单。
- Test Command：`rg -n "TODO|TBD|<[^>]+>" README.md docs process PROCESS.md` 后逐项人工确认；`git diff --check`。
- Non-goals：未获授权时替用户登录、购买 API 或伪造互评。
- Risk / response：过早宣称 Gate 通过；正式 Gate 等待 `MSD_GROUP_ID`、真实模型和独立审查后再填写。
- Estimated Effort：2h；Dependencies：C1–C6。
