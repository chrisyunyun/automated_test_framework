"""
FastAPI 服务入口
测试用例运行平台后端
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routers import test_runner

app = FastAPI(title="Pytest Runner API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(test_runner.router, prefix="/api", tags=["test-runner"])


@app.get("/")
def root():
    return {"message": "Pytest Runner API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
