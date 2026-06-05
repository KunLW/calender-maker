# Calendar Maker

把一句自然语言转成可订阅的 `.ics` 日历。

## 功能

- 网页输入一句话
- 调用 AI 返回结构化日历事件
- Pydantic 校验 AI 输出
- 用户确认后保存到 SQLite
- 通过 `/calendar.ics` 输出订阅日历

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

打开：

```text
http://127.0.0.1:8000/
```

订阅地址：

```text
http://127.0.0.1:8000/calendar.ics?token=change-me
```

部署到 ECS 后，把 `127.0.0.1` 换成公网 IP 或域名。

## 配置

见 `.env.example`。

第一版优先读取 `QWEN_API_KEY` 调用 Qwen。也保留 `OPENAI_API_KEY` 作为备用。`CALENDAR_TOKEN` 用来保护 `.ics` 订阅地址，请部署时改成随机字符串。

Qwen 配置示例。推荐本地开发直接在 `.env` 填真实 key，线上部署用进程环境变量或 systemd `EnvironmentFile`：

```env
QWEN_API_KEY=sk-...
QWEN_MODEL=qwen-plus
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

页面会通过 `/api/config/status` 显示当前服务是否能看到 AI key。注意环境变量必须在启动服务前存在，服务运行后再 `export QWEN_API_KEY=...` 不会影响已运行进程。

如果部署在公网，建议同时设置 `APP_TOKEN`。设置后网页使用：

```text
http://127.0.0.1:8000/?token=your-app-token
```

## 测试

```bash
pytest
```
