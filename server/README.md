# Pytest Runner Server

易威行 OA 自动化测试执行平台后端

## 技术栈

- **FastAPI** - 高性能 Web 框架
- **Uvicorn** - ASGI 服务器
- **SSE** - Server-Sent Events 实时日志

## 安装

```bash
cd server
pip install -r requirements.txt
```

## 启动

```bash
python -m uvicorn server.main:app --reload --port 8000
```

## API

- `GET /api/cases` - 获取测试用例列表
- `POST /api/execute` - 发起测试执行
- `GET /api/execute/{id}/stream` - SSE 日志流
- `DELETE /api/execute/{id}` - 停止执行
