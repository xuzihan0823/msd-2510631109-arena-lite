# 2510631109 · LaunchSpec AI 真实 Provider 生成截图

- 原始文件：`/Users/mac/Desktop/uat.png`
- 原始修改时间：2026-07-22 17:20:17 CST
- 归档日期：2026-07-23
- 尺寸：1892 × 1412
- SHA-256：`a20b24c3166b3376814a5e9179a024da60fbeb65f130df89946d8fe76f3d5bbe`

## 截图可证明的状态

- 本机 LaunchSpec AI 使用 `anthropic-compatible` provider，health 返回 `status=ok`、`ready=true`。
- 脱敏测试项目创建返回 HTTP `201`。
- 真实模型生成返回 HTTP `200`。
- 项目阶段为 `generated`，并返回目标用户、MVP 范围、非目标、架构和 AI 使用边界等结构化板块。
- 可见生成模型标识为 `gpt-5.6-sol`；完整脱敏摘要见 `evidence/real-ai-2026-07-22/generate-summary.json`。

## 证据边界与安全

- 本图是命令/API 结果证据，不单独证明真人在浏览器内完成全部点击。
- 截图未显示 API Key、Token、Authorization header 或密码。
- 截图包含本机路径、课程项目编号和测试项目 UUID；它们不是认证凭据，但对外分享时可继续遮挡。
- 临时 provider 配置只用于运行过程；截图不包含其值。本记录不要求提交任何 `.env*` 或临时配置文件。

## 关联证据

- `evidence/real-ai-2026-07-22/README.md`
- `evidence/real-ai-2026-07-22/generate-summary.json`
- `evidence/real-ai-2026-07-22/review-summary.json`
- `evidence/real-ai-2026-07-22/export.md`
