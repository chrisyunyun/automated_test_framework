"""
测试运行器路由
提供用例列表、批量执行、SSE 日志流接口
"""
import asyncio
import uuid
from typing import List
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from server.services.pytest_service import pytest_service, TestCase

router = APIRouter()


@router.get("/cases", response_model=List[TestCase])
async def get_cases():
    """获取所有测试用例"""
    return pytest_service.collect_cases()


@router.post("/execute")
async def execute_cases(case_ids: List[str] = Query(...)):
    """发起测试执行，返回执行 ID"""
    execution_id = str(uuid.uuid4())
    return {"execution_id": execution_id}


@router.get("/execute/{execution_id}/stream")
async def stream_execution(execution_id: str, case_ids: str = Query(...)):
    """SSE 流式返回执行日志"""
    case_id_list = case_ids.split(",")

    queue = asyncio.Queue()

    asyncio.create_task(pytest_service.execute_cases(case_id_list, execution_id, queue))

    async def event_generator():
        while True:
            data = await queue.get()
            if data == "data: [DONE]\n\n":
                break
            yield data
            if "[DONE]" in data:
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.delete("/execute/{execution_id}")
async def stop_execution(execution_id: str):
    """停止指定的测试执行"""
    pytest_service.stop_execution(execution_id)
    return {"status": "stopped", "execution_id": execution_id}
