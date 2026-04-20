"""
Pytest 执行服务
支持用例收集、批量执行、SSE 实时日志
"""
import asyncio
import json
import os
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
    case_ids: str = ""


class PytestService:
    """Pytest 服务类"""

    def __init__(self):
        self._running_executions: Dict[str, asyncio.subprocess.Process] = {}
        self._execution_history: List[ExecutionResult] = []

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
        docstring_map = self._extract_docstrings()

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
                    display_name = docstring_map.get(test_id, name.replace("test_", "").replace("_", " ").title())

                    cases.append(TestCase(
                        id=test_id,
                        name=display_name,
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

    def _extract_docstrings(self) -> Dict[str, str]:
        """从测试文件中提取 docstring 作为中文显示名"""
        docstring_map = {}
        test_files = list(TEST_DIR.glob("test_*.py"))

        for test_file in test_files:
            content = test_file.read_text(encoding="utf-8")
            module_name = test_file.stem

            lines = content.split('\n')
            current_func = None

            for i, line in enumerate(lines):
                line = line.strip()
                func_match = re.match(r'def (test_\w+)', line)
                if func_match:
                    current_func = func_match.group(1)

                if current_func and '"""' in line:
                    docstring_start = line.find('"""')
                    docstring_end = line.find('"""', docstring_start + 3)

                    if docstring_start != -1 and docstring_end != -1:
                        doc = line[docstring_start + 3:docstring_end].strip()
                        if ':' in doc:
                            doc = doc.split(':', 1)[1].strip()
                        test_id = f"{module_name}::{current_func}"
                        docstring_map[test_id] = doc
                        current_func = None

        return docstring_map

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

        report_name = datetime.now().strftime("%Y%m%d_%H%M%S") + ".html"
        cmd.extend(["--html=reports/" + report_name, "--self-contained-html"])

        def extract_name(case_id):
            return case_id.split("::")[-1]

        if len(case_ids) == 1:
            cmd.extend(["-k", extract_name(case_ids[0])])
        elif len(case_ids) > 1:
            case_str = " or ".join(extract_name(cid) for cid in case_ids)
            cmd.extend(["-k", case_str])

        cmd_str = " ".join(cmd)

        try:
            process = await asyncio.create_subprocess_shell(
                cmd_str,
                cwd=str(BASE_DIR),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env = {**os.environ, "PYTHONUNBUFFERED": "1", "HEADLESS": "false" if not headless else "true"}
            )

            self._running_executions[execution_id] = process

            stdout, _ = await process.communicate()
            log_output = stdout.decode("utf-8", errors="replace")

            for decoded_line in log_output.splitlines():
                line = decoded_line.strip()
                if line:
                    await sse_queue.put(f"data: {json.dumps({'type': 'log', 'content': line})}\n\n")

            duration = (datetime.now() - start_time).total_seconds()

            log_lines = log_output.splitlines()
            passed = sum(1 for l in log_lines if "PASSED" in l)
            failed = sum(1 for l in log_lines if "FAILED" in l)
            skipped = sum(1 for l in log_lines if "SKIPPED" in l)

            final_status = "passed" if failed == 0 else "failed" if failed > 0 else "unknown"

            result = ExecutionResult(
                execution_id=execution_id,
                status=final_status,
                passed=passed,
                failed=failed,
                skipped=skipped,
                duration=duration,
                log=log_output,
                timestamp=datetime.now().isoformat()
            )

            await sse_queue.put(f"data: {json.dumps({'type': 'result', **asdict(result)})}\n\n")
            await sse_queue.put("data: [DONE]\n\n")

        except Exception as e:
            await sse_queue.put(f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n")

        finally:
            if execution_id in self._running_executions:
                del self._running_executions[execution_id]

    async def execute_cases_sync(self, case_ids: List[str], execution_id: str, headless: bool = True) -> ExecutionResult:
        """同步执行测试用例，等待完成返回结果（不推送 SSE）"""
        start_time = datetime.now()

        if not case_ids:
            return ExecutionResult(
                execution_id=execution_id,
                status="error",
                passed=0,
                failed=0,
                skipped=0,
                duration=0,
                log="No cases selected",
                timestamp=datetime.now().isoformat()
            )

        cmd = [
            "pytest",
            "--tb=short",
            "-v",
            "--capture=no",
            "-p", "no:warnings",
        ]

        report_name = datetime.now().strftime("%Y%m%d_%H%M%S") + ".html"
        cmd.extend(["--html=reports/" + report_name, "--self-contained-html"])

        def extract_name(case_id):
            return case_id.split("::")[-1]

        if len(case_ids) == 1:
            cmd.extend(["-k", extract_name(case_ids[0])])
        elif len(case_ids) > 1:
            case_str = " or ".join(extract_name(cid) for cid in case_ids)
            cmd.extend(["-k", case_str])

        cmd_str = " ".join(cmd)

        try:
            result = subprocess.run(
                cmd_str,
                shell=True,
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1", "HEADLESS": "false" if not headless else "true"}
            )

            log_output = result.stdout + result.stderr
            duration = (datetime.now() - start_time).total_seconds()

            log_lines = log_output.splitlines()
            passed = sum(1 for l in log_lines if "PASSED" in l)
            failed = sum(1 for l in log_lines if "FAILED" in l)
            skipped = sum(1 for l in log_lines if "SKIPPED" in l)

            case_ids_str = ",".join(case_ids)

            final_status = "passed" if failed == 0 else "failed" if failed > 0 else "unknown"

            result = ExecutionResult(
                execution_id=execution_id,
                status=final_status,
                passed=passed,
                failed=failed,
                skipped=skipped,
                duration=duration,
                log=log_output,
                timestamp=datetime.now().isoformat(),
                case_ids=case_ids_str
            )

            self._execution_history.insert(0, result)
            if len(self._execution_history) > 50:
                self._execution_history = self._execution_history[:50]

            return result

        except Exception as e:
            result = ExecutionResult(
                execution_id=execution_id,
                status="error",
                passed=0,
                failed=0,
                skipped=0,
                duration=0,
                log=str(e),
                timestamp=datetime.now().isoformat(),
                case_ids=",".join(case_ids)
            )
            self._execution_history.insert(0, result)
            return result

    def get_execution_history(self) -> List[ExecutionResult]:
        """获取执行历史"""
        return self._execution_history

    def stop_execution(self, execution_id: str):
        """停止指定的执行"""
        if execution_id in self._running_executions:
            self._running_executions[execution_id].terminate()
            del self._running_executions[execution_id]


pytest_service = PytestService()
