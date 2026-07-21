# D11 Uvicorn 启动截图说明（2510631109）

- Screenshot（截图）: `2510631109-D11-uvicorn-startup.png`
- 证据阶段: D11 本地 UAT
- 操作环境: macOS 26.5.2 原生终端；WSL2/Ubuntu：N/A
- 项目: `msd-2510631109-arena-lite`

## 画面所证实的状态

截图显示项目虚拟环境已激活，并执行：

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8124
```

终端日志显示 `Application startup complete` 与 `Uvicorn running on http://127.0.0.1:8124`。这证明 FastAPI 服务在本机回环地址成功启动；`127.0.0.1` 不是公网或私有远程服务地址。

## 后续 CLI 验证

在另一终端执行：

```bash
curl -sS http://127.0.0.1:8124/health | python3 -m json.tool
```

对应健康检查成功截图为 `2510631109-D11-health.png`，完整 API 状态证据为 `../2510631109-D11-uat-status.txt`。

## 敏感信息处理

已核对截图：不显示真实账号、密码、API Key、Token、私钥、支付信息或远程私有 endpoint。截图中仅含本机用户目录、项目学号标识及本机回环地址，作为课程内部提交的环境证据保留。
