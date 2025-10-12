"""
Updated Judge Engine dengan Docker Integration

Cara menggunakan:
1. Backup file lama: mv core/judge_engine.py core/judge_engine.py.backup
2. Copy file ini: cp core/judge_engine_docker.py core/judge_engine.py
3. Restart aplikasi
"""

from .models import JudgeRequest, TestCase
from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .docker_executor import DockerExecutor  # Gunakan DockerExecutor
from typing import Optional

from dataclasses import dataclass
import uuid
import os
import glob


@dataclass
class JudgeResult:
    status: str
    total_case: int = 0
    total_case_benar: int = 0
    result: dict = None
    error_message: Optional[str] = None


class JudgeEngine:
    def __init__(self):
        # Gunakan DockerExecutor untuk menjalankan code dalam container
        self.executor = DockerExecutor(timeout=5)
    
    def judge_code(self, payload: JudgeRequest):
        session_id = str(uuid.uuid4())
        
        try:
            # Execute test cases langsung dengan Docker
            results = []
            total_passed = 0
            
            for idx, test_case in enumerate(payload.test_cases):
                # Execute code dalam Docker container
                execution_result = self.executor.execute(
                    language=payload.language,
                    code=payload.code,
                    input_data=test_case.input,
                    session_id=f"{session_id}_{idx}"
                )
                
                # Validasi output
                is_passed = self._validate_output(
                    execution_result.output,
                    test_case.expected_output
                )
                
                if is_passed:
                    total_passed += 1
                
                # Determine final status
                if execution_result.status == "timeout":
                    final_status = "timeout"
                elif execution_result.status == "runtime_error":
                    final_status = "runtime_error"
                elif execution_result.status == "execution_error":
                    final_status = "execution_error"
                elif execution_result.status == "unsupported_language":
                    final_status = "unsupported_language"
                elif is_passed:
                    final_status = "accepted"
                else:
                    final_status = "wrong_answer"
                
                results.append({
                    "test_case": idx + 1,
                    "input": test_case.input,
                    "expected_output": test_case.expected_output,
                    "actual_output": execution_result.output,
                    "passed": is_passed,
                    "status": final_status,
                    "execution_time": execution_result.execution_time,
                    "memory_used": execution_result.memory_used
                })
            
            return {
                "status": "finished",
                "total_case": len(payload.test_cases),
                "total_case_benar": total_passed,
                "results": results
            }
            
        except Exception as e:
            return {
                "status": "system_error",
                "total_case": len(payload.test_cases),
                "total_case_benar": 0,
                "results": [],
                "error_message": str(e)
            }
    
    def _validate_output(self, actual, expected):
        """Normalize dan compare output"""
        actual_normalized = actual.replace("\r\n", "\n").strip()
        expected_normalized = expected.replace("\r\n", "\n").strip()
        
        return actual_normalized == expected_normalized


def judge_code(payload: JudgeRequest):
    engine = JudgeEngine()
    return engine.judge_code(payload)
