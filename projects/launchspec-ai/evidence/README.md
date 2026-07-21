# Evidence Index

此目录只保留可复查、脱敏的命令输出和截图说明。

- `local-uat/`：由 `npm run uat` 生成的本地 API UAT 输出。它使用 `AI_PROVIDER=demo`，只能证明应用链路，不是真实模型调用证据。
- 真实模型验证：在获得授权和 `.env.local` 配置后，保存脱敏状态码、模型名、时间、输入摘要、输出结构摘要和失败情况；不得保存 API Key、Authorization header、完整敏感想法或支付信息。
- 独立审查：应另外保存审查人/模型身份、只读提示词摘要、结论和后续修正的可复查记录。

截图须配同名 Markdown 说明文件，写明界面状态、截图脱敏处理和可替代的 CLI 验证命令。
