from .docker_executor_v2 import DockerExecutorV2, DockerExecutorRequest, ExecutionResult
from .models import JudgeRequest, TestCase, Verdict
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class TestCaseResult:
    """Hasil evaluasi satu test case"""
    case_number: int
    verdict: Verdict
    time_ms: float
    memory_kb: float
    input_data: str
    expected_output: str
    actual_output: str
    error_message: Optional[str] = None
    
    def to_dict(self):
        return {
            "case_number": self.case_number,
            "verdict": self.verdict.value,
            "time_ms": round(self.time_ms, 2) if self.time_ms else 0,
            "memory_kb": round(self.memory_kb, 2) if self.memory_kb else 0,
            "input_data": self.input_data[:100] + "..." if len(self.input_data) > 100 else self.input_data,
            "expected_output": self.expected_output[:100] + "..." if len(self.expected_output) > 100 else self.expected_output,
            "actual_output": self.actual_output[:100] + "..." if len(self.actual_output) > 100 else self.actual_output,
            "error_message": self.error_message
        }

@dataclass
class JudgeResult:
    """Hasil evaluasi keseluruhan"""
    verdict: Verdict
    score: float
    total_cases: int
    passed_cases: int
    
    # Metrics
    total_time_ms: float
    max_time_ms: float
    avg_time_ms: float
    max_memory_kb: float
    
    # Details
    test_results: List[TestCaseResult] = field(default_factory=list)
    error_message: Optional[str] = None
    judged_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return {
            "verdict": self.verdict.value,
            "score": round(self.score, 2),
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "total_time_ms": round(self.total_time_ms, 2),
            "max_time_ms": round(self.max_time_ms, 2),
            "avg_time_ms": round(self.avg_time_ms, 2),
            "max_memory_kb": round(self.max_memory_kb, 2),
            "test_results": [tr.to_dict() for tr in self.test_results],
            "error_message": self.error_message,
            "judged_at": self.judged_at
        }


class JudgeEngineV2:
    def __init__(self):
        self.docker_executor = DockerExecutorV2()
    
    def execute(self, payload: JudgeRequest) -> JudgeResult:
        """
        Main execution method untuk judging
        """
        try:
            test_cases = payload.test_cases
            code = payload.code
            language = payload.language
            
            # Default limits
            global_time_limit = payload.time_limit_ms or 5000  # 5 second
            global_memory_limit = payload.memory_limit_kb or 256000  # 256 MB
            
            print(f'\n{"="*60}')
            print(f'🔍 Starting Judge Process')
            print(f'Language: {language}')
            print(f'Test Cases: {len(test_cases)}')
            print(f'Time Limit: {global_time_limit}ms')
            print(f'Memory Limit: {global_memory_limit}KB')
            print(f'{"="*60}\n')
            
            test_results = []
            
            # Execute each test case
            for idx, test_case in enumerate(test_cases, start=1):
                print(f'📝 Test Case {idx}/{len(test_cases)}:')
                
                # Get limits (per-test or global)
                time_limit = global_time_limit
                memory_limit =  global_memory_limit
                
                # Execute test case
                executor_payload = DockerExecutorRequest(
                    language,
                    code,
                    input_data=test_case.input,
                    timeout=int(time_limit / 1000) + 5  # Convert to seconds + buffer
                )
                
                execute_result = self.docker_executor.execute(executor_payload)
                
                # Evaluate result
                test_result = self.evaluate_result(
                    idx, 
                    test_case, 
                    execute_result,
                    time_limit,
                    memory_limit
                )
                
                test_results.append(test_result)
                
                # Print result
                print(f'{test_result.verdict.value} | '
                      f'Time: {test_result.time_ms}ms | '
                      f'Memory: {test_result.memory_kb}KB')
                
                if test_result.error_message:
                    print(f'   ⚠️  {test_result.error_message}')
                
                print()
            
            # Calculate overall result
            final_result = self.calculate_final_result(test_results, len(test_cases))
            
            print(f'\n{"="*60}')
            print(f' Final Verdict: {final_result.verdict.value}')
            print(f' Score: {final_result.score}/100')
            print(f' Passed: {final_result.passed_cases}/{final_result.total_cases}')
            print(f' Max Time: {final_result.max_time_ms}ms')
            print(f' Max Memory: {final_result.max_memory_kb}KB')
            print(f'{"="*60}\n')
            
            return final_result
            
        except Exception as e:
            print(f'Critical Error: {str(e)}')
            return JudgeResult(
                verdict=Verdict.RUNTIME_ERROR,
                score=0.0,
                total_cases=len(payload.test_cases),
                passed_cases=0,
                total_time_ms=0.0,
                max_time_ms=0.0,
                avg_time_ms=0.0,
                max_memory_kb=0.0,
                test_results=[],
                error_message=f"Critical error: {str(e)}"
            )
    
    def evaluate_result(
        self, 
        case_number: int,
        test_case: TestCase, 
        result: ExecutionResult,
        time_limit_ms: float,
        memory_limit_kb: float
    ) -> TestCaseResult:
        """
        Evaluasi hasil eksekusi satu test case
        
        Priority:
        1. Compilation Error (CE)
        2. Runtime Error (RE)
        3. Time Limit Exceeded (TLE)
        4. Memory Limit Exceeded (MLE)
        5. Wrong Answer (WA)
        6. Accepted (AC)
        """
        
        # 1. Check Compilation Error
        if result.status == "COMPILE_ERROR":
            return TestCaseResult(
                case_number=case_number,
                verdict=Verdict.COMPILATION_ERROR,
                time_ms=0,
                memory_kb=0,
                input_data=test_case.input,
                expected_output=test_case.expected_output,
                actual_output="",
                error_message=f"Compilation Error: {result.compilation_error}"
            )
        
        # 2. Check Runtime Error (non-zero exit code)
        if result.status == "RUNTIME_ERROR":
            return TestCaseResult(
                case_number=case_number,
                verdict=Verdict.RUNTIME_ERROR,
                time_ms=result.time_ms_used or 0,
                memory_kb=result.mem_kb_used or 0,
                input_data=test_case.input,
                expected_output=test_case.expected_output,
                actual_output=result.output,
                error_message=f"Runtime Error (exit code: {result.return_code})"
            )
        
        # 3. Check Timeout
        if result.status == "TIMEOUT" or result.return_code == 124:
            return TestCaseResult(
                case_number=case_number,
                verdict=Verdict.TIME_LIMIT_EXCEEDED,
                time_ms=time_limit_ms,  # Set to limit
                memory_kb=result.mem_kb_used or 0,
                input_data=test_case.input,
                expected_output=test_case.expected_output,
                actual_output=result.output,
                error_message=f"Time Limit Exceeded (>{time_limit_ms}ms)"
            )
        
        # 4. Check Time Limit Exceeded (dari metrics)
        if result.time_ms_used and result.time_ms_used > time_limit_ms:
            return TestCaseResult(
                case_number=case_number,
                verdict=Verdict.TIME_LIMIT_EXCEEDED,
                time_ms=result.time_ms_used,
                memory_kb=result.mem_kb_used or 0,
                input_data=test_case.input,
                expected_output=test_case.expected_output,
                actual_output=result.output,
                error_message=f"Time Limit Exceeded ({result.time_ms_used}ms > {time_limit_ms}ms)"
            )
        
        # 5. Check Memory Limit Exceeded
        if result.mem_kb_used and result.mem_kb_used > memory_limit_kb:
            return TestCaseResult(
                case_number=case_number,
                verdict=Verdict.MEMORY_LIMIT_EXCEEDED,
                time_ms=result.time_ms_used or 0,
                memory_kb=result.mem_kb_used,
                input_data=test_case.input,
                expected_output=test_case.expected_output,
                actual_output=result.output,
                error_message=f"Memory Limit Exceeded ({result.mem_kb_used}KB > {memory_limit_kb}KB)"
            )
        
        # 6. Compare Output (AC or WA)
        expected = test_case.expected_output.strip()
        actual = result.output.strip()
        
        if self._compare_output(expected, actual):
            return TestCaseResult(
                case_number=case_number,
                verdict=Verdict.ACCEPTED,
                time_ms=result.time_ms_used or 0,
                memory_kb=result.mem_kb_used or 0,
                input_data=test_case.input,
                expected_output=expected,
                actual_output=actual,
                error_message=None
            )
        else:
            return TestCaseResult(
                case_number=case_number,
                verdict=Verdict.WRONG_ANSWER,
                time_ms=result.time_ms_used or 0,
                memory_kb=result.mem_kb_used or 0,
                input_data=test_case.input,
                expected_output=expected,
                actual_output=actual,
                error_message="Wrong Answer: Output does not match expected output"
            )
    
    def _compare_output(self, expected: str, actual: str) -> bool:
        """
        Compare output dengan beberapa mode:
        1. Exact match (after strip)
        2. Line by line comparison (ignore trailing spaces)
        3. Token by token comparison (untuk numeric output)
        """
        
        # Mode 1: Exact match
        if expected == actual:
            return True
        
        # Mode 2: Line by line (ignore trailing spaces per line)
        expected_lines = [line.rstrip() for line in expected.split('\n')]
        actual_lines = [line.rstrip() for line in actual.split('\n')]
        
        if expected_lines == actual_lines:
            return True
        
        # Mode 3: Token comparison (split by whitespace)
        expected_tokens = expected.split()
        actual_tokens = actual.split()
        
        if expected_tokens == actual_tokens:
            return True
        
        return False
    
    def calculate_final_result(self, test_results: List[TestCaseResult], total_cases: int) -> JudgeResult:
        """
        Calculate final verdict and score based on all test results
        
        Verdict Priority (highest to lowest):
        1. CE (Compilation Error)
        2. RE (Runtime Error)
        3. TLE (Time Limit Exceeded)
        4. MLE (Memory Limit Exceeded)
        5. WA (Wrong Answer)
        6. AC (Accepted)
        """
        
        # Count verdicts
        verdict_counts = {}
        for result in test_results:
            verdict_counts[result.verdict] = verdict_counts.get(result.verdict, 0) + 1
        
        # Determine final verdict by priority
        if Verdict.COMPILATION_ERROR in verdict_counts:
            final_verdict = Verdict.COMPILATION_ERROR
        elif Verdict.RUNTIME_ERROR in verdict_counts:
            final_verdict = Verdict.RUNTIME_ERROR
        elif Verdict.TIME_LIMIT_EXCEEDED in verdict_counts:
            final_verdict = Verdict.TIME_LIMIT_EXCEEDED
        elif Verdict.MEMORY_LIMIT_EXCEEDED in verdict_counts:
            final_verdict = Verdict.MEMORY_LIMIT_EXCEEDED
        elif Verdict.WRONG_ANSWER in verdict_counts:
            final_verdict = Verdict.WRONG_ANSWER
        else:
            final_verdict = Verdict.ACCEPTED
        
        # Calculate passed cases
        passed_cases = verdict_counts.get(Verdict.ACCEPTED, 0)
        
        # Calculate score (0-100)
        score = (passed_cases / total_cases * 100) if total_cases > 0 else 0
        
        # Calculate metrics
        times = [r.time_ms for r in test_results if r.time_ms > 0]
        memories = [r.memory_kb for r in test_results if r.memory_kb > 0]
        
        total_time_ms = sum(times) if times else 0
        max_time_ms = max(times) if times else 0
        avg_time_ms = (total_time_ms / len(times)) if times else 0
        max_memory_kb = max(memories) if memories else 0
        
        return JudgeResult(
            verdict=final_verdict,
            score=score,
            total_cases=total_cases,
            passed_cases=passed_cases,
            total_time_ms=total_time_ms,
            max_time_ms=max_time_ms,
            avg_time_ms=avg_time_ms,
            max_memory_kb=max_memory_kb,
            test_results=test_results
        )
    

def judge_code_v2(payload: JudgeRequest):
    """
    Main entry point for judging
    """
    judge_engine = JudgeEngineV2()
    result = judge_engine.execute(payload)
    return result
