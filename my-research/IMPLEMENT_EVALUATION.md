# Implementasi Sistem Penilaian/Evaluasi yang Baik

## Konsep Dasar Judging System

### Status/Verdict yang Standar dalam Competitive Programming

1. **AC (Accepted)** ✅
   - Semua test case passed
   - Output sesuai expected
   - Waktu dan memori dalam batas

2. **WA (Wrong Answer)** ❌
   - Output tidak sesuai expected
   - Logic error dalam kode

3. **TLE (Time Limit Exceeded)** ⏱️
   - Program terlalu lambat
   - Melebihi batas waktu yang ditentukan

4. **MLE (Memory Limit Exceeded)** 💾
   - Program menggunakan terlalu banyak memori
   - Melebihi batas memori yang ditentukan

5. **RE (Runtime Error)** 💥
   - Program crash saat runtime
   - Segmentation fault, division by zero, dll
   - Exit code != 0

6. **CE (Compilation Error)** 🔨
   - Kode tidak bisa dikompilasi (C/C++/Java)
   - Syntax error

7. **PE (Presentation Error)** 📄
   - Output benar tapi format salah
   - Extra spaces, newlines, dll

## Struktur Data yang Baik

### 1. Verdict Enum
```python
from enum import Enum

class Verdict(str, Enum):
    ACCEPTED = "AC"              # Accepted
    WRONG_ANSWER = "WA"          # Wrong Answer
    TIME_LIMIT_EXCEEDED = "TLE"  # Time Limit Exceeded
    MEMORY_LIMIT_EXCEEDED = "MLE" # Memory Limit Exceeded
    RUNTIME_ERROR = "RE"         # Runtime Error
    COMPILATION_ERROR = "CE"     # Compilation Error
    PRESENTATION_ERROR = "PE"    # Presentation Error (optional)
    PENDING = "PENDING"          # Belum dijudge
    JUDGING = "JUDGING"          # Sedang dijudge
```

### 2. TestCaseResult
Detail hasil untuk satu test case
```python
@dataclass
class TestCaseResult:
    case_number: int
    verdict: Verdict
    time_ms: float
    memory_kb: float
    input_data: str
    expected_output: str
    actual_output: str
    error_message: Optional[str] = None
```

### 3. JudgeResult
Hasil keseluruhan judging
```python
@dataclass
class JudgeResult:
    verdict: Verdict              # Verdict keseluruhan
    score: float                  # Score (0-100)
    total_cases: int              # Total test cases
    passed_cases: int             # Test cases yang passed
    
    # Metrics
    total_time_ms: float          # Total waktu semua test case
    max_time_ms: float            # Waktu terlama (bottleneck)
    avg_time_ms: float            # Rata-rata waktu
    max_memory_kb: float          # Memory tertinggi yang digunakan
    
    # Details
    test_results: List[TestCaseResult]  # Detail per test case
    error_message: Optional[str] = None # Error message jika ada
    
    # Timestamps
    judged_at: str = None         # Waktu dijudge
```

## Algoritma Evaluasi

### Prioritas Verdict

Ketika ada multiple test cases dengan hasil berbeda, prioritas verdict:

1. **CE** (Compilation Error) - Highest priority
   - Jika compile error, langsung return CE, tidak perlu run test
   
2. **RE** (Runtime Error)
   - Jika ada test case RE, verdict = RE
   
3. **TLE** (Time Limit Exceeded)
   - Jika ada test case TLE, verdict = TLE
   
4. **MLE** (Memory Limit Exceeded)
   - Jika ada test case MLE, verdict = MLE
   
5. **WA** (Wrong Answer)
   - Jika ada test case WA (tapi tidak ada RE/TLE/MLE), verdict = WA
   
6. **AC** (Accepted) - Lowest priority
   - Hanya jika SEMUA test case AC

### Flowchart Evaluasi

```
START
  ↓
Compile Code (untuk C/C++/Java)
  ↓
Compilation Success?
  ├─ NO → Return CE (Compilation Error)
  ↓
 YES
  ↓
FOR each test case:
  ↓
  Run code dengan input
  ↓
  Check Return Code
  ├─ exit_code == 124 → TLE
  ├─ exit_code != 0 → RE
  ↓
  Check Time
  ├─ time > time_limit → TLE
  ↓
  Check Memory
  ├─ memory > memory_limit → MLE
  ↓
  Compare Output
  ├─ exact match → AC
  ├─ match after strip → AC (or PE if strict)
  └─ no match → WA
  ↓
END FOR
  ↓
Determine Overall Verdict (by priority)
  ↓
Calculate Score
  ↓
Return JudgeResult
```

## Implementasi Lengkap

### 1. Update `models.py`

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
from datetime import datetime

class LanguageEnum(str, Enum):
    C = "c"
    CPP = "cpp"
    JAVA = "java"
    PYTHON = "python"

class Verdict(str, Enum):
    ACCEPTED = "AC"
    WRONG_ANSWER = "WA"
    TIME_LIMIT_EXCEEDED = "TLE"
    MEMORY_LIMIT_EXCEEDED = "MLE"
    RUNTIME_ERROR = "RE"
    COMPILATION_ERROR = "CE"
    PRESENTATION_ERROR = "PE"
    PENDING = "PENDING"
    JUDGING = "JUDGING"

class TestCase(BaseModel):
    input: str
    expected_output: str
    time_limit_ms: Optional[float] = 1000  # Default 1 second
    memory_limit_kb: Optional[float] = 256000  # Default 256 MB

class JudgeRequest(BaseModel):
    code: str
    test_cases: List[TestCase]
    language: str = "c"
    time_limit_ms: Optional[float] = 1000  # Global time limit
    memory_limit_kb: Optional[float] = 256000  # Global memory limit
```

### 2. Update `docker_executor_v2.py`

Tambahkan handling untuk compilation error:

```python
@dataclass
class ExecutionResult:
    output: str
    status: str  # "completed", "timeout", "error", "compilation_error"
    return_code: int
    mem_kb_used: float | None = None
    time_ms_used: float | None = None
    error_output: str = ""  # Stderr output
    compilation_error: str = ""  # Compilation error message

# Di method execute, tambahkan:
def execute(self, payload: DockerExecutorRequest):
    # ... existing code ...
    
    # Check for compilation error
    compile_error_file = os.path.join(temp_dir, 'compile_error.txt')
    if os.path.exists(compile_error_file):
        with open(compile_error_file) as f:
            compile_error = f.read().strip()
            if compile_error:
                return ExecutionResult(
                    "",
                    status="compilation_error",
                    return_code=1,
                    compilation_error=compile_error
                )
```

### 3. Implementasi `judge_engine_v2.py` yang Lengkap

```python
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
            global_time_limit = payload.time_limit_ms or 1000  # 1 second
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
                time_limit = test_case.time_limit_ms or global_time_limit
                memory_limit = test_case.memory_limit_kb or global_memory_limit
                
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
                verdict_emoji = self._get_verdict_emoji(test_result.verdict)
                print(f'   {verdict_emoji} {test_result.verdict.value} | '
                      f'Time: {test_result.time_ms}ms | '
                      f'Memory: {test_result.memory_kb}KB')
                
                if test_result.error_message:
                    print(f'   ⚠️  {test_result.error_message}')
                
                print()
            
            # Calculate overall result
            final_result = self.calculate_final_result(test_results, len(test_cases))
            
            print(f'\n{"="*60}')
            print(f'📊 Final Verdict: {final_result.verdict.value}')
            print(f'🎯 Score: {final_result.score}/100')
            print(f'✅ Passed: {final_result.passed_cases}/{final_result.total_cases}')
            print(f'⏱️  Max Time: {final_result.max_time_ms}ms')
            print(f'💾 Max Memory: {final_result.max_memory_kb}KB')
            print(f'{"="*60}\n')
            
            return final_result
            
        except Exception as e:
            print(f'❌ Critical Error: {str(e)}')
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
        if result.status == "compilation_error":
            return TestCaseResult(
                case_number=case_number,
                verdict=Verdict.COMPILATION_ERROR,
                time_ms=0,
                memory_kb=0,
                input_data=test_case.input,
                expected_output=test_case.expected_output,
                actual_output="",
                error_message=f"Compilation Error: {result.compilation_error[:200]}"
            )
        
        # 2. Check Runtime Error (non-zero exit code)
        if result.return_code != 0 and result.status != "timeout":
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
        if result.status == "timeout" or result.return_code == 124:
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
    
    def _get_verdict_emoji(self, verdict: Verdict) -> str:
        """Get emoji for verdict"""
        emoji_map = {
            Verdict.ACCEPTED: "✅",
            Verdict.WRONG_ANSWER: "❌",
            Verdict.TIME_LIMIT_EXCEEDED: "⏱️",
            Verdict.MEMORY_LIMIT_EXCEEDED: "💾",
            Verdict.RUNTIME_ERROR: "💥",
            Verdict.COMPILATION_ERROR: "🔨",
            Verdict.PRESENTATION_ERROR: "📄",
            Verdict.PENDING: "⏳",
            Verdict.JUDGING: "🔄"
        }
        return emoji_map.get(verdict, "❓")


def judge_code_v2(payload: JudgeRequest):
    """
    Main entry point for judging
    """
    judge_engine = JudgeEngineV2()
    result = judge_engine.execute(payload)
    return result.to_dict()
```

## Keuntungan Implementasi Ini

### 1. **Verdict yang Jelas dan Standar**
- Menggunakan verdict standar competitive programming
- Priority yang jelas untuk multiple errors
- Mudah dipahami user

### 2. **Detailed Metrics**
- Per test case metrics (time, memory)
- Overall metrics (total, max, average)
- Berguna untuk optimasi kode

### 3. **Score Calculation**
- Score 0-100 berdasarkan passed cases
- Mudah untuk grading system
- Bisa custom formula jika perlu

### 4. **Flexible Output Comparison**
- Exact match
- Line by line (ignore trailing spaces)
- Token based (untuk numeric output)
- Bisa extend untuk floating point comparison

### 5. **Good Logging**
- Console output yang informatif
- Emoji untuk visual feedback
- Easy debugging

### 6. **API Response yang Lengkap**
- Verdict keseluruhan
- Detail per test case
- Metrics lengkap
- Timestamp

## Contoh Response JSON

```json
{
  "verdict": "AC",
  "score": 100.0,
  "total_cases": 3,
  "passed_cases": 3,
  "total_time_ms": 45.23,
  "max_time_ms": 18.50,
  "avg_time_ms": 15.08,
  "max_memory_kb": 2048.00,
  "test_results": [
    {
      "case_number": 1,
      "verdict": "AC",
      "time_ms": 12.34,
      "memory_kb": 1024.00,
      "input_data": "5 3",
      "expected_output": "8",
      "actual_output": "8",
      "error_message": null
    },
    {
      "case_number": 2,
      "verdict": "AC",
      "time_ms": 14.39,
      "memory_kb": 2048.00,
      "input_data": "10 20",
      "expected_output": "30",
      "actual_output": "30",
      "error_message": null
    },
    {
      "case_number": 3,
      "verdict": "AC",
      "time_ms": 18.50,
      "memory_kb": 1536.00,
      "input_data": "100 200",
      "expected_output": "300",
      "actual_output": "300",
      "error_message": null
    }
  ],
  "error_message": null,
  "judged_at": "2025-10-12T10:30:45.123456"
}
```

## Advanced Features (Optional)

### 1. Partial Scoring
Untuk problem dengan multiple subtask:
```python
def calculate_score_with_subtasks(test_results, subtasks):
    """
    subtasks = [
        {"cases": [1, 2, 3], "points": 30},
        {"cases": [4, 5], "points": 40},
        {"cases": [6, 7, 8], "points": 30}
    ]
    """
    score = 0
    for subtask in subtasks:
        all_passed = all(
            test_results[i-1].verdict == Verdict.ACCEPTED 
            for i in subtask["cases"]
        )
        if all_passed:
            score += subtask["points"]
    return score
```

### 2. Floating Point Comparison
Untuk output berupa floating point:
```python
def compare_float_output(expected: str, actual: str, epsilon=1e-6) -> bool:
    try:
        exp_val = float(expected)
        act_val = float(actual)
        return abs(exp_val - act_val) < epsilon
    except ValueError:
        return expected == actual
```

### 3. Special Judge (Checker)
Untuk problem dengan multiple valid answer:
```python
def special_judge(input_data: str, expected: str, actual: str, code: str) -> bool:
    """
    Custom checker untuk problem tertentu
    Return True jika jawaban valid
    """
    # Implement custom logic
    pass
```

## Testing

### Test Case 1: All Accepted
```python
payload = {
    "code": "print(int(input()) + int(input()))",
    "language": "python",
    "test_cases": [
        {"input": "2\n3", "expected_output": "5"},
        {"input": "10\n20", "expected_output": "30"},
    ]
}
# Expected: AC, Score: 100
```

### Test Case 2: Wrong Answer
```python
payload = {
    "code": "print(int(input()) * int(input()))",  # Wrong: multiply instead of add
    "language": "python",
    "test_cases": [
        {"input": "2\n3", "expected_output": "5"},  # Actual: 6
    ]
}
# Expected: WA, Score: 0
```

### Test Case 3: Time Limit Exceeded
```python
payload = {
    "code": "while True: pass",
    "language": "python",
    "time_limit_ms": 1000,
    "test_cases": [
        {"input": "", "expected_output": ""},
    ]
}
# Expected: TLE, Score: 0
```

### Test Case 4: Runtime Error
```python
payload = {
    "code": "print(1/0)",
    "language": "python",
    "test_cases": [
        {"input": "", "expected_output": ""},
    ]
}
# Expected: RE, Score: 0
```

## Kesimpulan

Sistem evaluasi yang baik harus:
1. ✅ Menggunakan verdict standar (AC, WA, TLE, MLE, RE, CE)
2. ✅ Priority yang jelas untuk multiple errors
3. ✅ Metrics lengkap (time, memory) per test case dan overall
4. ✅ Score calculation yang fair
5. ✅ Output comparison yang flexible
6. ✅ Logging dan debugging yang baik
7. ✅ API response yang informatif
8. ✅ Extensible untuk advanced features

Implementasi di atas sudah production-ready dan bisa langsung digunakan! 🚀
