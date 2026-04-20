"""
测试运行器路由
提供用例列表、批量执行、历史记录接口
"""
import uuid
from typing import List
from fastapi import APIRouter, Query
from pydantic import BaseModel
from server.services.pytest_service import pytest_service, TestCase, ExecutionResult

router = APIRouter()


class ExecuteResponse(BaseModel):
    execution_id: str
    status: str
    passed: int
    failed: int
    skipped: int
    duration: float
    log: str


class HistoryItem(BaseModel):
    execution_id: str
    status: str
    passed: int
    failed: int
    skipped: int
    duration: float
    case_ids: str
    timestamp: str


@router.get("/cases", response_model=List[TestCase])
async def get_cases():
    """获取所有测试用例"""
    return pytest_service.collect_cases()


@router.post("/execute", response_model=ExecuteResponse)
async def execute_cases(case_ids: str = Query(...), headless: bool = Query(True)):
    """执行测试用例，等待完成返回结果"""
    case_id_list = case_ids.split(",") if case_ids else []
    execution_id = str(uuid.uuid4())
    result = await pytest_service.execute_cases_sync(case_id_list, execution_id, headless=headless)
    return ExecuteResponse(
        execution_id=execution_id,
        status=result.status,
        passed=result.passed,
        failed=result.failed,
        skipped=result.skipped,
        duration=result.duration,
        log=result.log
    )


@router.get("/history", response_model=List[HistoryItem])
async def get_history():
    """获取执行历史记录"""
    history = pytest_service.get_execution_history()
    return [
        HistoryItem(
            execution_id=h.execution_id,
            status=h.status,
            passed=h.passed,
            failed=h.failed,
            skipped=h.skipped,
            duration=h.duration,
            case_ids=h.case_ids,
            timestamp=h.timestamp
        )
        for h in history
    ]


@router.delete("/execute/{execution_id}")
async def stop_execution(execution_id: str):
    """停止指定的测试执行"""
    pytest_service.stop_execution(execution_id)
    return {"status": "stopped", "execution_id": execution_id}
