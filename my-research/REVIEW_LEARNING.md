# 📚 Review Pembelajaran Docker Executor

## ✅ Yang Sudah Anda Pelajari

### 1. **`executor.py`** - Docker Executor Class (SANGAT BAGUS! ⭐⭐⭐⭐⭐)

```python
class DockerExecutor:
    def execute(self, language, code, input_data):
        # Membuat temporary directory
        # Menulis code dan input ke file
        # Menjalankan docker container
        # Membaca output
        # Cleanup
```

**✅ Kelebihan:**
- ✅ Menggunakan `tempfile.mkdtemp()` untuk isolasi
- ✅ Multi-language support dengan dictionary mapping
- ✅ Proper cleanup dengan `finally` block
- ✅ Return dataclass `ExecutionResult` (clean API)
- ✅ Error handling sudah ada

**⚠️ Yang Bisa Ditingkatkan:**
1. **Parsing metrics** - Belum membaca `metrics.txt` untuk TIME dan MEM
2. **Error handling** - Belum membaca `runtime_error.txt`
3. **Timeout** - Belum ada timeout untuk docker run
4. **Compile error** - Java/C/C++ perlu kompilasi dulu

---

### 2. **`executor1A.py`** - Versi Sederhana (BAGUS UNTUK BELAJAR! ⭐⭐⭐⭐)

```python
def run_dockerfile(code: str, test_input: str):
    # Membuat temp directory
    # Menulis code dan input
    # Jalankan docker
    # Cleanup
```

**✅ Konsep yang Benar:**
- ✅ Menggunakan `subprocess.run()` dengan `capture_output=True`
- ✅ Volume mounting: `-v {temp_dir}:/code`
- ✅ `--rm` flag untuk auto cleanup container

**📝 Catatan:**
- Ini versi proof-of-concept yang bagus
- Cocok untuk testing cepat
- Perlu dikembangkan untuk production

---

### 3. **`test_docker.py`** - Testing Docker SDK (SIMPLE & WORK! ⭐⭐⭐)

```python
client = docker.from_env()
container = client.containers.run(...)
```

**✅ Belajar:**
- Docker SDK Python (`docker` package)
- Cara run container programmatically
- Basic docker automation

**📝 Catatan:**
- Untuk judger, menggunakan `subprocess` lebih baik
- Karena kita butuh `docker run` dengan shell command

---

### 4. **`judger-python/`** - Docker Image Testing (EXCELLENT! ⭐⭐⭐⭐⭐)

#### Dockerfile:
```dockerfile
FROM python:3.12-slim
RUN apt-get install -y time bc  # ✅ Untuk metrics
COPY run.sh /run.sh
ENTRYPOINT [ "/run.sh" ]
```

#### run.sh:
```bash
/usr/bin/time -f "TIME:%e\nMEM:%M" -o /code/metrics.txt \
    python3 /code/main.py < /code/input.txt > /code/output.txt 2> /code/runtime_error.txt
```

**✅ PERFECT!** Ini sudah sangat bagus karena:
- ✅ Menggunakan `/usr/bin/time` untuk tracking performa
- ✅ Redirect input dari `input.txt`
- ✅ Output ke `output.txt`
- ✅ Error ke `runtime_error.txt`
- ✅ Metrics ke `metrics.txt`

---

### 5. **`test-run/`** - Test Results (WORKING! ⭐⭐⭐⭐⭐)

```
main.py          → Hello from python
input.txt        → (kosong)
output.txt       → Hello from python
metrics.txt      → TIME:0.02, MEM:8344
runtime_error.txt → (kosong karena no error)
```

**✅ SUDAH BERJALAN DENGAN BAIK!**

---

## 🎯 Next Steps - Implementasi ke Main Project

### Langkah 1: Build Semua Docker Images

```bash
cd /Users/fajryariansyah/Documents/Kuliah/seka-judger

# Python
docker build -f docker/python_runner.dockerfile -t judger-python docker/

# C
docker build -f docker/c_runner.dockerfile -t judger-c docker/

# C++
docker build -f docker/cpp_runner.dockerfile -t judger-cpp docker/

# Java
docker build -f docker/java_runner.dockerfile -t judger-java docker/
```

### Langkah 2: Integrasikan `executor.py` ke Main Project

Pindahkan konsep dari `testing/executor.py` ke `core/docker_executor.py`:

```python
# core/docker_executor.py
from dataclasses import dataclass
import tempfile, shutil, os, subprocess
from typing import Optional

@dataclass
class ExecutionResult:
    output: str
    status: str  # "completed", "timeout", "runtime_error", "compile_error"
    return_code: int
    time_used: Optional[float] = None
    mem_used: Optional[float] = None
    error_message: Optional[str] = None

class DockerExecutor:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.images = {
            "python": "judger-python",
            "c": "judger-c",
            "cpp": "judger-cpp",
            "java": "judger-java"
        }
        self.code_files = {
            "python": "main.py",
            "c": "main.c",
            "cpp": "main.cpp",
            "java": "Main.java"
        }
        
    def execute(self, language: str, code: str, input_data: str) -> ExecutionResult:
        """Execute code in isolated Docker container"""
        
        if language not in self.images:
            return ExecutionResult(
                output="",
                status="error",
                return_code=-1,
                error_message=f"Unsupported language: {language}"
            )
        
        temp_dir = None
        try:
            # 1. Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # 2. Write code and input files
            code_file = os.path.join(temp_dir, self.code_files[language])
            input_file = os.path.join(temp_dir, "input.txt")
            
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(input_data)
            
            # 3. Run Docker container
            docker_image = self.images[language]
            command = [
                'docker', 'run',
                '--rm',                          # Auto remove after execution
                '--network', 'none',             # No network access (security)
                '--memory', '256m',              # Memory limit
                '--cpus', '1',                   # CPU limit
                '-v', f'{temp_dir}:/code:rw',   # Mount code directory
                docker_image
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # 4. Read output files
            output = self._read_file(temp_dir, "output.txt")
            error_msg = self._read_file(temp_dir, "runtime_error.txt")
            metrics = self._parse_metrics(temp_dir)
            
            # 5. Determine status
            if result.returncode != 0:
                status = "runtime_error"
            else:
                status = "completed"
            
            return ExecutionResult(
                output=output,
                status=status,
                return_code=result.returncode,
                time_used=metrics.get("time"),
                mem_used=metrics.get("mem"),
                error_message=error_msg if error_msg else None
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                output="",
                status="timeout",
                return_code=-1,
                error_message=f"Execution exceeded {self.timeout} seconds"
            )
        except Exception as e:
            return ExecutionResult(
                output="",
                status="error",
                return_code=-1,
                error_message=str(e)
            )
        finally:
            # 6. Cleanup
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _read_file(self, temp_dir: str, filename: str) -> str:
        """Read file from temp directory"""
        filepath = os.path.join(temp_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return ""
    
    def _parse_metrics(self, temp_dir: str) -> dict:
        """Parse metrics.txt for TIME and MEM"""
        metrics = {}
        metrics_file = os.path.join(temp_dir, "metrics.txt")
        
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r') as f:
                for line in f:
                    if line.startswith("TIME:"):
                        metrics["time"] = float(line.split(":")[1].strip())
                    elif line.startswith("MEM:"):
                        metrics["mem"] = float(line.split(":")[1].strip())
        
        return metrics
```

### Langkah 3: Update `main.py` untuk Menggunakan Docker

```python
# main.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from core.docker_executor import DockerExecutor
from core.models import JudgeRequest

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

executor = DockerExecutor(timeout=5)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/judge")
async def judge(request: JudgeRequest):
    """Judge endpoint with Docker execution"""
    
    # Execute code in Docker
    result = executor.execute(
        language=request.language,
        code=request.code,
        input_data=request.test_input
    )
    
    # Check result
    if result.status == "completed":
        # Compare output with expected
        actual = result.output.strip()
        expected = request.expected_output.strip()
        
        if actual == expected:
            verdict = "accepted"
        else:
            verdict = "wrong_answer"
    else:
        verdict = result.status  # timeout, runtime_error, etc.
    
    return {
        "verdict": verdict,
        "output": result.output,
        "expected": request.expected_output,
        "time_used": result.time_used,
        "mem_used": result.mem_used,
        "error_message": result.error_message
    }
```

---

## 🧪 Testing Plan

### Test 1: Python
```python
code = """
a = int(input())
b = int(input())
print(a + b)
"""
input_data = "5\n3"
expected = "8"
```

### Test 2: C
```c
#include <stdio.h>
int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d", a + b);
    return 0;
}
```

### Test 3: Java
```java
import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.print(a + b);
    }
}
```

---

## 📊 Diagram Flow yang Anda Sudah Pelajari

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCKER EXECUTOR FLOW                      │
└─────────────────────────────────────────────────────────────┘

1. User Submit Code
   │
   ▼
2. Create Temp Directory
   ├── main.py (atau main.c, Main.java, dll)
   └── input.txt
   │
   ▼
3. Run Docker Container
   docker run --rm -v {temp_dir}:/code judger-{language}
   │
   ▼
4. Inside Container (via run.sh)
   /usr/bin/time -f "TIME:%e\nMEM:%M" \
       {command} < input.txt > output.txt 2> runtime_error.txt
   │
   ▼
5. Read Results
   ├── output.txt       → stdout
   ├── metrics.txt      → TIME, MEM
   └── runtime_error.txt → stderr
   │
   ▼
6. Cleanup Temp Directory
   │
   ▼
7. Return ExecutionResult
```

---

## 🎓 Kesimpulan

### Yang Sudah Anda Kuasai: ✅

1. ✅ **Docker basics** - Build, run, volume mounting
2. ✅ **Subprocess** - Menjalankan command dari Python
3. ✅ **Temporary files** - `tempfile.mkdtemp()` untuk isolasi
4. ✅ **File I/O** - Read/write files untuk code execution
5. ✅ **Metrics parsing** - Membaca TIME dan MEM dari `/usr/bin/time`
6. ✅ **Error handling** - Try-except-finally pattern
7. ✅ **Dataclasses** - Clean data structure untuk results
8. ✅ **Shell scripts** - Bash scripting untuk entrypoint

### Yang Perlu Ditambahkan: 📝

1. 📝 **Compile step** untuk C/C++/Java
2. 📝 **Security limits** - Memory, CPU, network restrictions
3. 📝 **Multiple test cases** - Loop untuk beberapa test
4. 📝 **Verdict logic** - AC, WA, TLE, RTE, CE
5. 📝 **Integration** - Connect dengan FastAPI main.py

---

## 🚀 Quick Command untuk Next Step

```bash
# 1. Build all images
bash build_docker_images.sh

# 2. Test individual executor
python3 testing/executor.py

# 3. Run main application
python3 main.py

# 4. Test via API
curl -X POST http://localhost:8001/judge \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "code": "print(int(input()) + int(input()))",
    "test_input": "5\n3",
    "expected_output": "8"
  }'
```

---

**🎉 KERJA BAGUS!** Anda sudah memahami core concepts dengan sangat baik. Tinggal integrasi ke main project!
