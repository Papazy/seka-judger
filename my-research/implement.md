# 🚀 Panduan Implementasi Docker untuk SEKA Judger

## 📋 Overview
Panduan ini menjelaskan cara mengimplementasikan Docker containers untuk menjalankan code submission dengan aman menggunakan containerization. Setiap bahasa pemrograman (C, C++, Java, Python) akan berjalan di container terpisah dengan user non-root untuk keamanan.

---

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────┐
│      FastAPI Main Application           │
│         (main.py)                        │
└──────────────┬──────────────────────────┘
               │
               ├──> Judge Engine (judge_engine.py)
               │
               ├──> Compiler (compiler.py)
               │
               └──> Executor (executor.py)
                            │
                            ▼
               ┌────────────────────────┐
               │   Docker Containers    │
               ├────────────────────────┤
               │  • C Runner            │
               │  • C++ Runner          │
               │  • Java Runner         │
               │  • Python Runner       │
               └────────────────────────┘
```

---

## 📁 Struktur File

```
docker/
├── c_runner.dockerfile         # Docker image untuk C
├── cpp_runner.dockerfile       # Docker image untuk C++
├── java_runner.dockerfile      # Docker image untuk Java
├── python_runner.dockerfile    # Docker image untuk Python
└── bash/
    ├── run_c_code.sh          # Script eksekusi C
    ├── run_cpp_code.sh        # Script eksekusi C++
    ├── run_java_code.sh       # Script eksekusi Java
    └── run_code.sh            # Script eksekusi Python
```

---

## 🔧 Step 1: Build Docker Images

### 1.1 Build Image C Runner
```bash
cd /Users/fajryariansyah/Documents/Kuliah/seka-judger
docker build -f docker/c_runner.dockerfile -t seka-judger-c:latest .
```

**Penjelasan:**
- Base image: `gcc:13.2.0` (sudah include GCC compiler)
- Install: GNU `time` dan `bc` untuk monitoring resource
- User: `runner` (non-root untuk security)
- Script: `run_c_code.sh` untuk compile & execute

### 1.2 Build Image C++ Runner
```bash
docker build -f docker/cpp_runner.dockerfile -t seka-judger-cpp:latest .
```

**Penjelasan:**
- Base image: `gcc:13.2.0` (support C++ via g++)
- Similar dengan C runner tapi pakai g++ compiler
- Script: `run_cpp_code.sh`

### 1.3 Build Image Java Runner
```bash
docker build -f docker/java_runner.dockerfile -t seka-judger-java:latest .
```

**Penjelasan:**
- Base image: `openjdk:17-slim`
- Compile dengan `javac`, execute dengan `java`
- Script: `run_java_code.sh`

### 1.4 Build Image Python Runner
```bash
docker build -f docker/python_runner.dockerfile -t seka-judger-python:latest .
```

**Penjelasan:**
- Base image: `python:3.12-slim`
- Langsung execute, tidak perlu compile
- Script: `run_code.sh`

### 1.5 Verify All Images
```bash
docker images | grep seka-judger
```

Expected output:
```
seka-judger-c       latest    abc123...    2 minutes ago    500MB
seka-judger-cpp     latest    def456...    2 minutes ago    500MB
seka-judger-java    latest    ghi789...    1 minute ago     400MB
seka-judger-python  latest    jkl012...    1 minute ago     150MB
```

---

## 🔄 Step 2: Update Executor untuk Docker Integration

### 2.1 Backup File Lama
```bash
cp core/executor.py core/executor.py.backup
```

### 2.2 Buat Docker-Based Executor

Buat file baru: `core/docker_executor.py`

```python
import docker
import os
import tempfile
import shutil
from typing import Optional
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    output: str
    status: str
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None
    return_code: int = 0

class DockerExecutor:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.client = docker.from_env()
        
        # Mapping bahasa ke image Docker
        self.image_map = {
            'c': 'seka-judger-c:latest',
            'cpp': 'seka-judger-cpp:latest',
            'java': 'seka-judger-java:latest',
            'python': 'seka-judger-python:latest'
        }
    
    def execute(self, language: str, code: str, input_data: str, session_id: str):
        """
        Execute code dalam Docker container
        
        Args:
            language: Bahasa pemrograman (c, cpp, java, python)
            code: Source code yang akan dieksekusi
            input_data: Input untuk program
            session_id: Unique session identifier
        
        Returns:
            ExecutionResult dengan output dan metrics
        """
        
        # Buat temporary directory untuk code dan data
        temp_dir = tempfile.mkdtemp(prefix=f"judger_{session_id}_")
        
        try:
            # Persiapan file berdasarkan bahasa
            self._prepare_files(temp_dir, language, code, input_data)
            
            # Dapatkan Docker image
            image_name = self.image_map.get(language)
            if not image_name:
                return ExecutionResult(
                    output="",
                    status="unsupported_language",
                    return_code=-1
                )
            
            # Jalankan container
            try:
                container = self.client.containers.run(
                    image=image_name,
                    volumes={temp_dir: {'bind': '/code', 'mode': 'rw'}},
                    network_mode='none',  # Isolasi network
                    mem_limit='256m',      # Limit memory
                    cpu_period=100000,
                    cpu_quota=50000,       # Limit CPU (50%)
                    detach=True,
                    remove=True,
                    user='runner'
                )
                
                # Tunggu execution selesai
                result = container.wait(timeout=self.timeout)
                
                # Baca output
                output = self._read_output(temp_dir)
                metrics = self._parse_metrics(temp_dir, language)
                
                return ExecutionResult(
                    output=output,
                    status='completed',
                    execution_time=metrics.get('time'),
                    memory_used=metrics.get('memory'),
                    return_code=result['StatusCode']
                )
                
            except docker.errors.ContainerError as e:
                error_output = self._read_error(temp_dir)
                return ExecutionResult(
                    output=error_output,
                    status='runtime_error',
                    return_code=e.exit_status
                )
            
            except Exception as e:
                return ExecutionResult(
                    output=str(e),
                    status='timeout' if 'timeout' in str(e).lower() else 'execution_error',
                    return_code=-1
                )
                
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _prepare_files(self, temp_dir: str, language: str, code: str, input_data: str):
        """Siapkan file code dan input"""
        
        # Tulis input data
        with open(os.path.join(temp_dir, 'input.txt'), 'w') as f:
            f.write(input_data)
        
        # Tulis source code
        if language == 'c':
            filename = 'main.c'
        elif language == 'cpp':
            filename = 'main.cpp'
        elif language == 'java':
            # Extract class name dari Java code
            import re
            match = re.search(r'public\s+class\s+(\w+)', code)
            class_name = match.group(1) if match else 'Main'
            filename = f'{class_name}.java'
        else:  # python
            filename = 'main.py'
        
        with open(os.path.join(temp_dir, filename), 'w') as f:
            f.write(code)
    
    def _read_output(self, temp_dir: str) -> str:
        """Baca output file"""
        output_file = os.path.join(temp_dir, 'output.txt')
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                return f.read().strip()
        return ""
    
    def _read_error(self, temp_dir: str) -> str:
        """Baca error file"""
        # Cek compile error
        compile_error = os.path.join(temp_dir, 'compile_error.txt')
        if os.path.exists(compile_error):
            with open(compile_error, 'r') as f:
                content = f.read().strip()
                if content:
                    return content
        
        # Cek runtime error
        runtime_error = os.path.join(temp_dir, 'runtime_error.txt')
        if os.path.exists(runtime_error):
            with open(runtime_error, 'r') as f:
                return f.read().strip()
        
        error_file = os.path.join(temp_dir, 'error.txt')
        if os.path.exists(error_file):
            with open(error_file, 'r') as f:
                return f.read().strip()
        
        return ""
    
    def _parse_metrics(self, temp_dir: str, language: str) -> dict:
        """Parse execution metrics dari file"""
        metrics = {}
        
        # Tentukan file metrics berdasarkan bahasa
        if language == 'java':
            metrics_file = os.path.join(temp_dir, 'metrics_java.txt')
        else:
            metrics_file = os.path.join(temp_dir, 'metrics.txt')
        
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r') as f:
                content = f.read()
                
                # Parse TIME
                import re
                time_match = re.search(r'TIME:(\d+\.\d+)', content)
                if time_match:
                    metrics['time'] = float(time_match.group(1))
                
                # Parse MEM
                mem_match = re.search(r'MEM:(\d+)', content)
                if mem_match:
                    metrics['memory'] = int(mem_match.group(1))
        
        return metrics
```

---

## 🔄 Step 3: Update Judge Engine

Update `core/judge_engine.py` untuk menggunakan `DockerExecutor`:

```python
from .docker_executor import DockerExecutor

class JudgeEngine:
    def __init__(self):
        self.executor = DockerExecutor(timeout=5)  # Ganti dengan DockerExecutor
        self.compiler_factory = CompilerFactory()
    
    def judge_code(self, payload: JudgeRequest):
        session_id = str(uuid.uuid4())
        
        # Direct execution dengan Docker (compile + run dalam container)
        results = []
        total_passed = 0
        
        for test_case in payload.test_cases:
            execution_result = self.executor.execute(
                language=payload.language,
                code=payload.code,
                input_data=test_case.input,
                session_id=session_id
            )
            
            is_passed = self._validate_output(
                execution_result.output,
                test_case.expected_output
            )
            
            if is_passed:
                total_passed += 1
            
            # Determine status
            if execution_result.status == "timeout":
                final_status = "timeout"
            elif execution_result.status == "runtime_error":
                final_status = "runtime_error"
            elif execution_result.status == "execution_error":
                final_status = "execution_error"
            elif is_passed:
                final_status = "accepted"
            else:
                final_status = "wrong_answer"
            
            results.append({
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
```

---

## 📦 Step 4: Update Dependencies

Tambahkan Docker SDK ke `requirements.txt`:

```bash
echo "docker>=7.0.0" >> requirements.txt
pip install docker
```

---

## 🧪 Step 5: Testing

### 5.1 Test Manual Docker Container

#### Test C:
```bash
# Buat test directory
mkdir -p /tmp/test_c
cd /tmp/test_c

# Buat file code
cat > main.c << 'EOF'
#include <stdio.h>
int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d", a + b);
    return 0;
}
EOF

# Buat input
echo "5 10" > input.txt

# Run container
docker run --rm \
  -v $(pwd):/code \
  --network none \
  --memory=256m \
  seka-judger-c:latest

# Check output
cat output.txt  # Should show: 15
```

#### Test Java:
```bash
mkdir -p /tmp/test_java
cd /tmp/test_java

cat > Main.java << 'EOF'
import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.print(a + b);
    }
}
EOF

echo "7 3" > input.txt

docker run --rm \
  -v $(pwd):/code \
  --network none \
  --memory=256m \
  seka-judger-java:latest

cat output.txt  # Should show: 10
```

### 5.2 Test via API

```bash
# Start application
python -m uvicorn main:app --reload --port 8001

# Test dengan curl
curl -X POST http://localhost:8001/judge \
  -H "Content-Type: application/json" \
  -d '{
    "code": "#include <stdio.h>\nint main() { int a, b; scanf(\"%d %d\", &a, &b); printf(\"%d\", a+b); return 0; }",
    "language": "c",
    "test_cases": [
      {"input": "5 10", "expected_output": "15"},
      {"input": "3 7", "expected_output": "10"}
    ]
  }'
```

---

## 🔒 Step 6: Security Checklist

- ✅ **Non-root user**: Semua container run sebagai user `runner`
- ✅ **Network isolation**: `--network none` (no internet access)
- ✅ **Memory limit**: 256MB per container
- ✅ **CPU limit**: 50% CPU quota
- ✅ **Timeout**: 5 detik max execution
- ✅ **Read-only filesystem**: (optional) tambahkan `--read-only` flag
- ✅ **No privileged mode**: Container tidak punya akses privileged

---

## 📊 Step 7: Monitoring & Logging

### 7.1 View Container Logs
```bash
docker ps -a  # Lihat containers
docker logs <container_id>
```

### 7.2 Monitor Resource Usage
```bash
docker stats
```

### 7.3 Cleanup Old Containers
```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -a -f
```

---

## 🐛 Troubleshooting

### Problem: "Cannot connect to Docker daemon"
**Solution:**
```bash
# MacOS/Linux
sudo systemctl start docker

# Check Docker status
docker info
```

### Problem: "Permission denied" saat build
**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Problem: Container timeout terlalu cepat
**Solution:**
Edit timeout di `DockerExecutor`:
```python
self.executor = DockerExecutor(timeout=10)  # Increase to 10 seconds
```

### Problem: Output tidak muncul
**Solution:**
Check bash script harus flush output:
```bash
cat /code/output.txt  # Pastikan ini ada di akhir script
```

---

## 📈 Performance Tips

1. **Build images sekali**: Jangan rebuild setiap request
2. **Use volume mounts**: Lebih cepat dari COPY
3. **Prune regularly**: Cleanup unused containers/images
4. **Use slim images**: Reduce image size
5. **Set resource limits**: Prevent resource exhaustion

---

## 🎯 Next Steps

1. ✅ Build semua Docker images
2. ✅ Install Docker SDK: `pip install docker`
3. ✅ Buat `core/docker_executor.py`
4. ✅ Update `core/judge_engine.py`
5. ✅ Test manual containers
6. ✅ Test via API
7. ✅ Deploy to production

---

## 📚 References

- [Docker Python SDK](https://docker-py.readthedocs.io/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Resource Constraints](https://docs.docker.com/config/containers/resource_constraints/)

---

**Last Updated:** 2025-10-11  
**Author:** SEKA Judger Team
