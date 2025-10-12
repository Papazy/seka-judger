# SEKA Judger - Analisis Lanjutan & Roadmap Implementasi Docker

**Tanggal**: 11 Oktober 2025  
**Versi**: 2.0  
**Status**: Ready untuk Implementasi Docker

---

## 📋 Executive Summary

Selamat! 🎉 Anda telah berhasil membuat foundation yang solid untuk migrasi ke Docker. Dockerfiles di folder `experiments/` sudah **BISA DIGUNAKAN** dan merupakan langkah besar menuju sistem judger yang aman. 

### ✅ Yang Sudah Anda Capai:

1. **4 Dockerfiles Terpisah**: C, C++, Java, dan Python - masing-masing dengan environment yang terisolasi
2. **Non-root User**: Semua container berjalan sebagai user `runner` (keamanan ✓)
3. **Shell Scripts**: Script untuk compile & run dengan metrics (waktu & memory)
4. **Resource Monitoring**: Menggunakan GNU `time` untuk tracking waktu dan memory

### 🎯 Next Step:

Integrasi Dockerfiles ini ke FastAPI judger engine agar:
- Setiap submission dijalankan dalam Docker container yang terisolasi
- Hasil output dikembalikan ke API
- Cleanup otomatis setelah eksekusi

---

## 🏗️ Arsitektur yang Akan Dibangun

### Before (Current - Unsafe ❌)
```
User Submit Code 
    ↓
FastAPI receives request
    ↓
Write code to temp/
    ↓
Compile & Execute DIRECTLY on Host Machine  ⚠️ DANGER
    ↓
Return results
```

### After (Target - Safe ✅)
```
User Submit Code 
    ↓
FastAPI receives request
    ↓
Create temporary workspace
    ↓
Start Docker Container (isolated environment)
    ├── Mount code files
    ├── Run with resource limits (CPU, Memory, Time)
    ├── Network disabled
    └── Read-only filesystem (except /code)
    ↓
Collect output from container
    ↓
Cleanup container & files
    ↓
Return results to API
```

---

## 📊 Analisis Dockerfiles Anda

### 1. **C Runner** (`c_runner.dockerfile`)

```dockerfile
FROM gcc:13.2.0
RUN apt-get update && apt-get install -y time bc && rm -rf /var/lib/apt/lists/*
RUN useradd -m runner
RUN mkdir /code && chown -R runner:runner /code
WORKDIR /code
COPY run_c_code.sh /run_c_code.sh
RUN chmod +x /run_c_code.sh
USER runner
ENTRYPOINT [ "/run_c_code.sh" ]
```

**✅ Kelebihan:**
- Base image official GCC (trusted)
- Non-root user `runner` (security best practice)
- GNU time untuk metrics
- `bc` untuk perhitungan matematis

**📝 Catatan:**
- Script `run_c_code.sh` melakukan compile + run dalam satu langkah
- Menggunakan `/code` sebagai workspace
- Output metrics ke file (time, memory)

---

### 2. **C++ Runner** (`cpp_runner.dockerfile`)

```dockerfile
FROM gcc:13.2.0
RUN apt-get update && apt-get install -y time bc && rm -rf /var/lib/apt/lists/*
RUN useradd -m runner
RUN mkdir /code && chown -R runner:runner /code
WORKDIR /code
COPY run_cpp_code.sh /run_cpp_code.sh
RUN chmod +x /run_cpp_code.sh
USER runner
ENTRYPOINT [ "/run_cpp_code.sh" ]
```

**✅ Identik dengan C Runner:**
- Keduanya menggunakan gcc:13.2.0 (g++ included)
- Perbedaan hanya di script yang di-copy

---

### 3. **Java Runner** (`java_runner.dockerfile`)

```dockerfile
FROM openjdk:17-slim
RUN apt-get update && apt-get install -y time && rm -rf /var/lib/apt/lists/*
RUN useradd -m runner
RUN mkdir /code && chown -R runner:runner /code
WORKDIR /code
COPY run_java_code.sh /run_java_code.sh
RUN chmod +x /run_java_code.sh
USER runner
ENTRYPOINT ["/run_java_code.sh"]
```

**✅ Kelebihan:**
- Slim variant (ukuran lebih kecil)
- OpenJDK 17 (LTS version)

**⚠️ Perhatian:**
- Java butuh class name yang match dengan nama file
- Memory management Java berbeda (JVM heap)

---

### 4. **Python Runner** (`python_runner.dockerfile`)

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y time && rm -rf /var/lib/apt/lists/*
RUN useradd -m runner
RUN mkdir /code
RUN chown -R runner:runner /code
WORKDIR /code
COPY run_code.sh /run_code.sh
RUN chmod +x /run_code.sh
USER runner
ENTRYPOINT ["/run_code.sh"]
```

**✅ Kelebihan:**
- Python 3.12 (latest stable)
- Slim variant (ukuran kecil)
- Tanpa pip packages tambahan (pure Python)

---

## 🔍 Analisis Shell Scripts

### `run_c_code.sh`
```bash
#!/bin/bash
set -ex

start_time=$(date +%s%N)

# Compile
gcc /code/main.c -o /code/a.out 2> /code/compile_error.txt

# Run with metrics
/usr/bin/time -f "TIME:%e\nMEM:%M" -o /code/metrics.txt \
  /code/a.out < /code/input.txt > /code/output.txt 2> /code/runtime_error.txt

end_time=$(date +%s%N)
elapsed_time=$(((end_time - start_time)/1000000))

# Parse metrics
time_used=$(grep "TIME" /code/metrics.txt | cut -d':' -f2)
mem_used=$(grep "MEM" /code/metrics.txt | cut -d':' -f2)

echo "TIME: $time_used seconds"
echo "MEMORY: $mem_used KB"
echo "ELAPSED (manual): $elapsed_time ms"

cat /code/output.txt
```

**✅ Yang Bagus:**
- Compile error ditangkap ke file
- Runtime error terpisah
- Metrics time & memory
- Output terstruktur

**⚠️ Masalah Potensial:**
1. **Compilation Error Handling**: Script tidak berhenti jika compile gagal
2. **Exit Code**: Tidak mengembalikan exit code yang proper
3. **Timeout**: Belum ada timeout mechanism di level script

**💡 Perbaikan yang Diperlukan:**
```bash
#!/bin/bash
set -e  # Stop on error

# Compile
gcc /code/main.c -o /code/a.out 2> /code/compile_error.txt
if [ $? -ne 0 ]; then
    echo "COMPILE_ERROR"
    cat /code/compile_error.txt
    exit 1
fi

# Run with timeout (5 detik)
timeout 5 /usr/bin/time -f "TIME:%e\nMEM:%M" -o /code/metrics.txt \
  /code/a.out < /code/input.txt > /code/output.txt 2> /code/runtime_error.txt

exit_code=$?
if [ $exit_code -eq 124 ]; then
    echo "TIMEOUT"
    exit 124
elif [ $exit_code -ne 0 ]; then
    echo "RUNTIME_ERROR"
    cat /code/runtime_error.txt
    exit $exit_code
fi

# Success - output results
cat /code/output.txt
```

---

## 🚀 Roadmap Implementasi: 3 Fase

### **FASE 1: Build Docker Images** (30 menit)

**Goal**: Build semua images dan test manual

#### Step 1.1: Pindahkan Dockerfiles ke Lokasi Final
```bash
# Pindah ke root project
cd /Users/fajryariansyah/Documents/Kuliah/seka-judger

# Pindahkan dockerfiles
mv experiments/c_runner.dockerfile docker/c.dockerfile
mv experiments/cpp_runner.dockerfile docker/cpp.dockerfile
mv experiments/java_runner.dockerfile docker/java.dockerfile
mv experiments/python_runner.dockerfile docker/python.dockerfile

# Pindahkan scripts
mv experiments/run_c_code.sh docker/
mv experiments/run_cpp_code.sh docker/
mv experiments/run_java_code.sh docker/
mv experiments/run_code.sh docker/
```

#### Step 1.2: Build Images
```bash
cd docker

# Build C image
docker build -f c.dockerfile -t seka-judger-c:latest .

# Build C++ image
docker build -f cpp.dockerfile -t seka-judger-cpp:latest .

# Build Java image
docker build -f java.dockerfile -t seka-judger-java:latest .

# Build Python image
docker build -f python.dockerfile -t seka-judger-python:latest .

# Verify images
docker images | grep seka-judger
```

#### Step 1.3: Test Manual
```bash
# Test C
echo '#include <stdio.h>
int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d\n", a + b);
    return 0;
}' > /tmp/main.c

echo "5 3" > /tmp/input.txt

docker run --rm \
  -v /tmp/main.c:/code/main.c:ro \
  -v /tmp/input.txt:/code/input.txt:ro \
  --memory="128m" \
  --cpus="0.5" \
  --network none \
  seka-judger-c:latest

# Output yang diharapkan:
# TIME: 0.00 seconds
# MEMORY: 1234 KB
# 8
```

---

### **FASE 2: Buat Docker Executor Module** (2 jam)

**Goal**: Buat module Python untuk menjalankan Docker container

#### Step 2.1: Buat `core/docker_executor.py`

```python
import docker
import os
import tempfile
import uuid
from typing import Optional
from dataclasses import dataclass

@dataclass
class DockerExecutionResult:
    output: str
    status: str  # success, compile_error, runtime_error, timeout, system_error
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None
    exit_code: int = 0
    error_message: Optional[str] = None

class DockerExecutor:
    def __init__(self):
        self.client = docker.from_env()
        self.image_map = {
            'c': 'seka-judger-c:latest',
            'cpp': 'seka-judger-cpp:latest',
            'java': 'seka-judger-java:latest',
            'python': 'seka-judger-python:latest'
        }
        
    def execute_code(self, language: str, code: str, input_data: str, 
                     timeout: int = 5, memory_limit: str = "128m") -> DockerExecutionResult:
        """
        Execute code in Docker container
        
        Args:
            language: Programming language (c, cpp, java, python)
            code: Source code to execute
            input_data: Input test data
            timeout: Timeout in seconds
            memory_limit: Memory limit (e.g., "128m", "256m")
        """
        
        # Create temporary directory for this execution
        session_id = str(uuid.uuid4())
        temp_dir = tempfile.mkdtemp(prefix=f"judger_{session_id}_")
        
        try:
            # Determine file extension and filename
            file_map = {
                'c': 'main.c',
                'cpp': 'main.cpp',
                'java': 'Main.java',  # Akan perlu adjustment untuk class name
                'python': 'main.py'
            }
            
            filename = file_map.get(language)
            if not filename:
                return DockerExecutionResult(
                    output="",
                    status="system_error",
                    error_message=f"Unsupported language: {language}"
                )
            
            # Write source code
            code_path = os.path.join(temp_dir, filename)
            with open(code_path, 'w') as f:
                f.write(code)
            
            # Write input data
            input_path = os.path.join(temp_dir, 'input.txt')
            with open(input_path, 'w') as f:
                f.write(input_data)
            
            # Get image name
            image_name = self.image_map[language]
            
            # Run container
            container = self.client.containers.run(
                image=image_name,
                volumes={
                    temp_dir: {'bind': '/code', 'mode': 'rw'}
                },
                mem_limit=memory_limit,
                cpu_period=100000,
                cpu_quota=50000,  # 50% of 1 CPU
                network_disabled=True,
                detach=True,
                remove=False  # We'll remove manually after getting logs
            )
            
            # Wait for container with timeout
            try:
                result = container.wait(timeout=timeout)
                exit_code = result['StatusCode']
                
                # Get logs (stdout + stderr)
                logs = container.logs().decode('utf-8')
                
                # Parse output
                status, output, exec_time, memory = self._parse_output(logs, exit_code)
                
                return DockerExecutionResult(
                    output=output,
                    status=status,
                    execution_time=exec_time,
                    memory_used=memory,
                    exit_code=exit_code
                )
                
            except Exception as e:
                # Timeout or other error
                container.stop(timeout=1)
                return DockerExecutionResult(
                    output="",
                    status="timeout" if "timeout" in str(e).lower() else "system_error",
                    error_message=str(e)
                )
            finally:
                # Cleanup container
                try:
                    container.remove(force=True)
                except:
                    pass
                    
        except docker.errors.ImageNotFound:
            return DockerExecutionResult(
                output="",
                status="system_error",
                error_message=f"Docker image not found: {image_name}"
            )
        except Exception as e:
            return DockerExecutionResult(
                output="",
                status="system_error",
                error_message=f"Docker execution error: {str(e)}"
            )
        finally:
            # Cleanup temporary directory
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass
    
    def _parse_output(self, logs: str, exit_code: int):
        """Parse container output to extract status, output, time, and memory"""
        
        lines = logs.strip().split('\n')
        
        # Check for compile error
        if 'COMPILE_ERROR' in logs:
            return 'compile_error', logs, None, None
        
        # Check for runtime error
        if 'RUNTIME_ERROR' in logs or exit_code != 0:
            return 'runtime_error', logs, None, None
        
        # Check for timeout
        if 'TIMEOUT' in logs:
            return 'timeout', '', None, None
        
        # Parse metrics
        exec_time = None
        memory = None
        output_lines = []
        
        for line in lines:
            if line.startswith('TIME:'):
                try:
                    exec_time = float(line.split(':')[1].strip().split()[0])
                except:
                    pass
            elif line.startswith('MEMORY:'):
                try:
                    memory = int(line.split(':')[1].strip().split()[0])
                except:
                    pass
            elif not line.startswith('ELAPSED:') and not line.startswith('+'):
                # Skip debug lines from 'set -x'
                if not line.startswith('++') and not line.startswith('TIME:') and not line.startswith('MEMORY:'):
                    output_lines.append(line)
        
        output = '\n'.join(output_lines).strip()
        return 'success', output, exec_time, memory
```

#### Step 2.2: Update `requirements.txt`
```txt
fastapi
uvicorn[standard]
pydantic
pytest
docker  # <-- ADD THIS
```

#### Step 2.3: Install docker package
```bash
pip install docker
```

---

### **FASE 3: Integrasi ke Judge Engine** (1 jam)

**Goal**: Modifikasi `judge_engine.py` untuk menggunakan Docker

#### Step 3.1: Update `core/judge_engine.py`

```python
from .models import JudgeRequest, TestCase
from .docker_executor import DockerExecutor, DockerExecutionResult
from typing import Optional
from dataclasses import dataclass

@dataclass
class JudgeResult:
    status: str
    total_case: int = 0
    total_case_benar: int = 0
    result: dict = None
    error_message: Optional[str] = None

class JudgeEngine:
    def __init__(self):
        self.docker_executor = DockerExecutor()
        
    def judge_code(self, payload: JudgeRequest):
        """
        Judge code using Docker containers for isolation
        """
        
        results = []
        total_passed = 0
        
        # Execute each test case
        for idx, test_case in enumerate(payload.test_cases):
            try:
                # Execute in Docker container
                exec_result = self.docker_executor.execute_code(
                    language=payload.language,
                    code=payload.code,
                    input_data=test_case.input,
                    timeout=5,
                    memory_limit="128m"
                )
                
                # Handle different statuses
                if exec_result.status == "compile_error":
                    return {
                        "status": "compile_error",
                        "total_case": len(payload.test_cases),
                        "total_case_benar": 0,
                        "results": [],
                        "error_message": exec_result.output
                    }
                
                # Validate output
                is_passed = self._validate_output(
                    exec_result.output,
                    test_case.expected_output
                )
                
                if is_passed:
                    total_passed += 1
                
                # Determine final status
                if exec_result.status == "timeout":
                    final_status = "timeout"
                elif exec_result.status == "runtime_error":
                    final_status = "runtime_error"
                elif exec_result.status == "system_error":
                    final_status = "system_error"
                elif is_passed:
                    final_status = "accepted"
                else:
                    final_status = "wrong_answer"
                
                results.append({
                    "test_case": idx + 1,
                    "input": test_case.input,
                    "expected_output": test_case.expected_output,
                    "actual_output": exec_result.output,
                    "passed": is_passed,
                    "status": final_status,
                    "execution_time": exec_result.execution_time,
                    "memory_used": exec_result.memory_used
                })
                
            except Exception as e:
                results.append({
                    "test_case": idx + 1,
                    "input": test_case.input,
                    "expected_output": test_case.expected_output,
                    "actual_output": "",
                    "passed": False,
                    "status": "system_error",
                    "error_message": str(e)
                })
        
        return {
            "status": "finished",
            "total_case": len(payload.test_cases),
            "total_case_benar": total_passed,
            "results": results
        }
    
    def _validate_output(self, actual, expected):
        """Validate output with normalized line endings"""
        actual_normalized = actual.strip().replace("\r\n", "\n")
        expected_normalized = expected.strip().replace("\r\n", "\n")
        return actual_normalized == expected_normalized

def judge_code(payload: JudgeRequest):
    """Entry point for judging code"""
    engine = JudgeEngine()
    return engine.judge_code(payload)
```

---

## 🧪 Testing Strategy

### Test 1: Simple Addition (C)
```bash
curl -X POST http://localhost:8001/judge \
  -H "Content-Type: application/json" \
  -d '{
    "code": "#include <stdio.h>\nint main() {\n    int a, b;\n    scanf(\"%d %d\", &a, &b);\n    printf(\"%d\\n\", a + b);\n    return 0;\n}",
    "language": "c",
    "test_cases": [
      {"input": "5 3", "expected_output": "8"},
      {"input": "10 20", "expected_output": "30"}
    ]
  }'
```

### Test 2: Compile Error
```bash
curl -X POST http://localhost:8001/judge \
  -H "Content-Type: application/json" \
  -d '{
    "code": "#include <stdio.h>\nint main() {\n    printf(\"Hello\"\n    return 0;\n}",
    "language": "c",
    "test_cases": [
      {"input": "", "expected_output": "Hello"}
    ]
  }'
```

### Test 3: Timeout (Infinite Loop)
```bash
curl -X POST http://localhost:8001/judge \
  -H "Content-Type: application/json" \
  -d '{
    "code": "#include <stdio.h>\nint main() {\n    while(1) {}\n    return 0;\n}",
    "language": "c",
    "test_cases": [
      {"input": "", "expected_output": ""}
    ]
  }'
```

### Test 4: Python
```bash
curl -X POST http://localhost:8001/judge \
  -H "Content-Type: application/json" \
  -d '{
    "code": "a, b = map(int, input().split())\nprint(a + b)",
    "language": "python",
    "test_cases": [
      {"input": "5 3", "expected_output": "8"},
      {"input": "100 200", "expected_output": "300"}
    ]
  }'
```

---

## 🔒 Security Improvements

### Yang Sudah Ada (dari Dockerfiles Anda):
1. ✅ **Non-root user**: Semua container run sebagai `runner`
2. ✅ **Isolated filesystem**: `/code` directory terpisah
3. ✅ **Base images official**: gcc, openjdk, python dari Docker Hub official

### Yang Akan Ditambahkan (di FASE 2):
1. ✅ **Network disabled**: `network_disabled=True`
2. ✅ **Memory limit**: `mem_limit="128m"`
3. ✅ **CPU limit**: `cpu_quota=50000` (50% CPU)
4. ✅ **Timeout**: Container dihentikan paksa setelah timeout
5. ✅ **Auto cleanup**: Container dan temp files dihapus otomatis

### Additional Hardening (Optional - Future):
- **Read-only root filesystem**: `read_only=True` dengan tmpfs untuk /tmp
- **Drop capabilities**: `cap_drop=['ALL']`
- **Seccomp profile**: Batasi system calls yang diizinkan
- **AppArmor/SELinux**: OS-level security policies

---

## 📈 Performance Considerations

### Current Overhead:
- **Container startup**: ~100-500ms (first time), ~50-100ms (warm)
- **Volume mounting**: ~10-50ms
- **Cleanup**: ~50-100ms

### Total per Submission:
- **Tanpa Docker**: 10-100ms
- **Dengan Docker**: 200-500ms per test case

### Optimization Tips:
1. **Pre-warm images**: Pull semua images saat startup
2. **Keep images running**: Gunakan container pool (advanced)
3. **Parallel execution**: Run multiple test cases dalam parallel (hati-hati resource)
4. **SSD storage**: Docker performance sangat bergantung pada disk I/O

---

## 🐛 Troubleshooting Guide

### Problem 1: "Cannot connect to Docker daemon"
```bash
# Check Docker daemon
docker ps

# Fix: Start Docker Desktop atau Docker daemon
# macOS: Open Docker Desktop app
# Linux: sudo systemctl start docker
```

### Problem 2: "Image not found"
```bash
# List images
docker images

# Rebuild image
cd docker
docker build -f c.dockerfile -t seka-judger-c:latest .
```

### Problem 3: Container hangs
```bash
# List running containers
docker ps

# Force stop all judger containers
docker ps | grep seka-judger | awk '{print $1}' | xargs docker stop

# Remove all stopped containers
docker container prune -f
```

### Problem 4: "Permission denied" di macOS
```bash
# Check Docker Desktop settings
# Settings > Resources > File Sharing
# Make sure /tmp is shared
```

### Problem 5: Python module not found
```bash
# Install docker package
pip install docker

# Verify
python -c "import docker; print(docker.__version__)"
```

---

## 📝 Checklist Implementasi

### FASE 1: Docker Setup
- [ ] Pindahkan Dockerfiles ke folder `docker/`
- [ ] Build semua 4 images
- [ ] Test manual setiap image dengan sample code
- [ ] Verify non-root user works
- [ ] Verify metrics output

### FASE 2: Docker Executor
- [ ] Buat file `core/docker_executor.py`
- [ ] Install `docker` package
- [ ] Test DockerExecutor class standalone
- [ ] Handle compile errors
- [ ] Handle runtime errors
- [ ] Handle timeouts
- [ ] Parse metrics correctly

### FASE 3: Integration
- [ ] Backup `core/judge_engine.py` yang lama
- [ ] Update judge_engine.py untuk use Docker
- [ ] Remove old compiler.py dependencies
- [ ] Remove old executor.py dependencies
- [ ] Test via API endpoint
- [ ] Update frontend jika perlu
- [ ] Run full test suite

### FASE 4: Production Ready
- [ ] Add proper logging
- [ ] Add monitoring (Prometheus/Grafana)
- [ ] Setup CI/CD for building images
- [ ] Document API dengan OpenAPI/Swagger
- [ ] Setup rate limiting
- [ ] Add authentication
- [ ] Deploy to cloud (AWS/GCP/Azure)

---

## 🎓 Kesimpulan

### Apakah Dockerfiles Anda Bisa Dipakai?
**YA! 100%** 🎉

Dockerfiles yang Anda buat di `experiments/` sudah sangat bagus dan siap digunakan. Yang perlu dilakukan:

1. **Perbaiki shell scripts** untuk handle error dengan baik
2. **Buat Docker executor module** di Python untuk orchestrate containers
3. **Integrasi ke judge engine** menggantikan subprocess langsung
4. **Test thoroughly** dengan berbagai test cases

### Estimasi Waktu Total:
- **FASE 1**: 30 menit - 1 jam
- **FASE 2**: 2-3 jam
- **FASE 3**: 1-2 jam
- **Testing**: 1-2 jam
- **Total**: **5-8 jam** untuk MVP production-ready

### Next Immediate Steps:
1. Follow FASE 1 step by step
2. Test setiap image secara manual
3. Lanjut ke FASE 2 setelah semua images verified
4. Iterate dan improve

---

## 📚 Resources

### Docker Python SDK:
- Dokumentasi: https://docker-py.readthedocs.io/
- Examples: https://docker-py.readthedocs.io/en/stable/containers.html

### Security Best Practices:
- Docker Security: https://docs.docker.com/engine/security/
- Container Security Checklist: https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html

### Similar Projects:
- Judge0: https://github.com/judge0/judge0
- DMOJ: https://github.com/DMOJ/judge-server
- Piston: https://github.com/engineer-man/piston

---

**Good luck! 🚀 Kalau ada pertanyaan atau stuck di step manapun, let me know!**
