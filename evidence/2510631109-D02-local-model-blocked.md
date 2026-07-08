# D02 本地模型说明与 HTTP 200 证据

- 学号：2510631109
- 日期：2026-07-08 00:28:56 CST
- 平台：macOS 原生终端
- 状态：本地 Ollama 模型暂不执行；本地 HTTP 200 验证已完成

## 本地模型执行状态

D02 手册主线要求使用 Ollama 拉取并运行 `qwen3.5:4b`。本机当前开发环境暂不支持/暂不采用 Ollama 本地模型路线，因此本次 D02 不声明 `qwen3.5:4b` 已在本机跑通。

当前处理方式：

- 本地 Ollama：暂不安装、暂不配置。
- `qwen3.5:4b`：暂不拉取、暂不运行。
- 本地模型证据：标记为 blocked / alternative，不伪造 `ollama list` 或模型回答。
- 后续如果课程强制要求本地模型证据，再单独补装 Ollama 并重新生成 `ollama --version`、`ollama list` 和模型回答记录。

原因说明：

- 本机主要开发环境已经集中在 macOS 原生终端、Claude Code 生态和自建模型中转服务上。
- 当前本机配置暂不以 Ollama 作为主要模型运行入口。
- 为避免新增本地模型服务带来的环境冲突和无效排障，本次先如实记录 blocked 状态。

## 本地 HTTP 200 验证

虽然本地 Ollama 模型暂不执行，但 D02 的本地 HTTP 200 验证已完成。

执行命令：

```bash
cd /Users/mac/Desktop/短学期实践/msd-work/msd-2510631109-arena-lite
python -m http.server 8765 --bind 127.0.0.1
curl -I http://127.0.0.1:8765
```

复核结果摘要：

```text
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.13.12
Content-Type: text/html; charset=utf-8
```

截图证据：

```text
evidence/screenshots/2510631109-D02-http200.png
```

## 检查结论

- 本地 HTTP 服务可以在 `127.0.0.1` 上启动。
- `curl -I http://127.0.0.1:8765` 返回 `200 OK`。
- 本地 Ollama / `qwen3.5:4b` 本次未跑通，不作为已完成项声明。

