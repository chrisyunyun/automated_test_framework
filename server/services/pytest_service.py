"""
Pytest 执行服务
支持用例收集、批量执行、SSE 实时日志
"""
import asyncio
import json
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import re


BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEST_DIR = BASE_DIR / "tests"


@dataclass
class TestCase:
    """测试用例数据结构"""
    id: str
    name: str
    module: str
    file: str
    marker: str
    status: str = "idle"


@dataclass
class ExecutionResult:
    """执行结果数据结构"""
    execution_id: str
    status: str
    passed: int
    failed: int
    skipped: int
    duration: float
    log: str
    timestamp: str


class PytestService:
    """Pytest 服务类"""

    def __init__(self):
        self._running_executions: Dict[str, asyncio.subprocess.Process] = {}

    def collect_cases(self) -> List[TestCase]:
        """收集所有测试用例"""
        cases = []
        result = subprocess.run(
            ["pytest", "--collect-only", "-q", "--rootdir", str(TEST_DIR)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True
        )

        output = result.stdout + result.stderr
        current_module = "unknown"
        marker_map = self._extract_markers()

        for line in output.splitlines():
            line = line.strip()
            if not line or line.startswith("="):
                continue

            if "<Module" in line:
                parts = line.split()
                if len(parts) >= 2:
                    current_module = parts[1].replace(".py>", "").replace(">", "")

            elif "<Function" in line:
                match = re.search(r'<Function (\S+)>', line)
                if match:
                    name = match.group(1)
                    test_id = f"{current_module}::{name}"
                    marker = marker_map.get(test_id, "regression")

                    cases.append(TestCase(
                        id=test_id,
                        name=name.replace("test_", "").replace("_", " ").title(),
                        module=current_module,
                        file=f"tests/{current_module}.py",
                        marker=marker
                    ))

        return cases

    def _extract_markers(self) -> Dict[str, str]:
        """从测试文件中提取 marker 信息"""
        marker_map = {}
        test_files = list(TEST_DIR.glob("test_*.py"))

        for test_file in test_files:
            content = test_file.read_text(encoding="utf-8")
            module_name = test_file.stem

            lines = content.split('\n')
            current_marker = None

            for line in lines:
                line = line.strip()
                mark_match = re.match(r'@pytest\.mark\.(\w+)', line)
                if mark_match:
                    current_marker = mark_match.group(1)
                func_match = re.match(r'def (test_\w+)', line)
                if func_match and current_marker:
                    func_name = func_match.group(1)
                    test_id = f"{module_name}::{func_name}"
                    marker_map[test_id] = current_marker
                    current_marker = None

        return marker_map

    async def execute_cases(
        self,
        case_ids: List[str],
        execution_id: str,
        sse_queue: asyncio.Queue
    ):
        """执行选定的测试用例，实时推送日志到 SSE"""
        start_time = datetime.now()

        if not case_ids:
            await sse_queue.put("data: {\"error\": \"No cases selected\"}\n\n")
            return

        await sse_queue.put(f"data: {json.dumps({'type': 'start', 'message': f'Starting {len(case_ids)} test cases...'})}\n\n")

        cmd = [
            "pytest",
            "--tb=short",
            "-v",
            "--capture=no",
            "-p", "no:warnings",
        ]

        if len(case_ids) == 1:
            cmd.extend(["-k", case_ids[0]])
        elif len(case_ids) > 1:
            case_str = " or ".join(case_ids)
            cmd.extend(["-k", case_str])

        cmd.extend(["--html=/dev/null", "--self-contained-html"])

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(BASE_DIR),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env={**subprocess.os.environ, "PYTHONUNBUFFERED": "1"}
            )

            self._running_executions[execution_id] = process

            log_output = []

            async for line in process.stdout:
                decoded_line = line.decode("utf-8", errors="replace").strip()
                if decoded_line:
                    log_output.append(decoded_line)
                    await sse_queue.put(f"data: {json.dumps({'type': 'log', 'content': decoded_line})}\n\n")

            await process.wait()

            duration = (datetime.now() - start_time).total_seconds()

            passed = sum(1 for l in log_output if "PASSED" in l)
            failed = sum(1 for l in log_output if "FAILED" in l)
            skipped = sum(1 for l in log_output if "SKIPPED" in l)

            final_status = "passed" if failed == 0 else "failed" if failed > 0 else "unknown"

            result = ExecutionResult(
                execution_id=execution_id,
                status=final_status,
                passed=passed,
                failed=failed,
                skipped=skipped,
                duration=duration,
                log="\n".join(log_output),
                timestamp=datetime.now().isoformat()
            )

            await sse_queue.put(f"data: {json.dumps({'type': 'result', **asdict(result)})}\n\n")
            await sse_queue.put("data: [DONE]\n\n")

        except Exception as e:
            await sse_queue.put(f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n")

        finally:
            if execution_id in self._running_executions:
                del self._running_executions[execution_id]

    def stop_execution(self, execution_id: str):
        """停止指定的执行"""
        if execution_id in self._running_executions:
            self._running_executions[execution_id].terminate()
            del self._running_executions[execution_id]


pytest_service = PytestService()
