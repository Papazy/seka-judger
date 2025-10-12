# 🚀 Langkah Implementasi Docker Executor

Berdasarkan pembelajaran Anda di folder `testing/`, berikut langkah implementasi ke main project.

---

## 📋 Checklist Implementasi

- [ ] **Step 1**: Build semua Docker images
- [ ] **Step 2**: Buat `core/docker_executor.py`
- [ ] **Step 3**: Test executor secara terpisah
- [ ] **Step 4**: Update `main.py` untuk menggunakan Docker
- [ ] **Step 5**: Test via Web UI
- [ ] **Step 6**: Test dengan multiple test cases

---

## Step 1: Build Docker Images

### 1.1 Verifikasi File Docker Ada

```bash
ls -la docker/
# Harus ada:
# - c_runner.dockerfile
# - cpp_runner.dockerfile
# - java_runner.dockerfile
# - python_runner.dockerfile
# - bash/run_*.sh
```

### 1.2 Build Python Runner

```bash
cd /Users/fajryariansyah/Documents/Kuliah/seka-judger
docker build -f docker/python_runner.dockerfile -t judger-python docker/
```

**Expected Output:**
```
[+] Building 5.2s (10/10) FINISHED
 => [1/5] FROM docker.io/library/python:3.12-slim
 => [2/5] RUN apt-get update && apt-get install -y time
 => [3/5] RUN useradd -m runner
 => [4/5] WORKDIR /code
 => [5/5] COPY bash/run_python_code.sh /run_python_code.sh
 => exporting to image
 => => naming to docker.io/library/judger-python
```

### 1.3 Build C Runner

```bash
docker build -f docker/c_runner.dockerfile -t judger-c docker/
```

### 1.4 Build C++ Runner

```bash
docker build -f docker/cpp_runner.dockerfile -t judger-cpp docker/
```

### 1.5 Build Java Runner

```bash
docker build -f docker/java_runner.dockerfile -t judger-java docker/
```

### 1.6 Verify All Images

```bash
docker images | grep judger
```

**Expected Output:**
```
judger-python   latest   abc123   5 minutes ago   150MB
judger-c        latest   def456   4 minutes ago   200MB
judger-cpp      latest   ghi789   3 minutes ago   250MB
judger-java     latest   jkl012   2 minutes ago   300MB
```

---

## Step 2: Buat `core/docker_executor.py`

Saya akan buatkan file ini berdasarkan `testing/executor.py` Anda:

```bash
# File akan dibuat di: core/docker_executor.py
```

File ini akan include:
- ✅ Class `DockerExecutor` dari testing/executor.py
- ✅ Parsing metrics dari `metrics.txt`
- ✅ Error handling dari `runtime_error.txt`
- ✅ Timeout protection
- ✅ Resource limits (memory, cpu)

---

## Step 3: Test Executor Secara Terpisah

### 3.1 Test Python

```bash
cd /Users/fajryariansyah/Documents/Kuliah/seka-judger
python3 -c "
from core.docker_executor import DockerExecutor

executor = DockerExecutor()
code = '''
a = int(input())
b = int(input())
print(a + b)
'''
result = executor.execute('python', code, '5\n3')
print('Output:', result.output)
print('Status:', result.status)
print('Time:', result.time_used)
print('Memory:', result.mem_used)
"
```

**Expected Output:**
```
Output: 8
Status: completed
Time: 0.02
Memory: 8344.0
```

### 3.2 Test C

```bash
python3 -c "
from core.docker_executor import DockerExecutor

executor = DockerExecutor()
code = '''
#include <stdio.h>
int main() {
    int a, b;
    scanf(\"%d %d\", &a, &b);
    printf(\"%d\", a + b);
    return 0;
}
'''
result = executor.execute('c', code, '5 3')
print('Output:', result.output)
print('Status:', result.status)
"
```

### 3.3 Test Java

```bash
python3 -c "
from core.docker_executor import DockerExecutor

executor = DockerExecutor()
code = '''
import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.print(a + b);
    }
}
'''
result = executor.execute('java', code, '5\n3')
print('Output:', result.output)
print('Status:', result.status)
"
```

---

## Step 4: Update `main.py`

### 4.1 Import Docker Executor

Di `main.py`, tambahkan:

```python
from core.docker_executor import DockerExecutor

# Initialize executor
executor = DockerExecutor(timeout=5)
```

### 4.2 Update `/judge` Endpoint

Ganti implementasi lama dengan Docker executor:

```python
@app.post("/judge")
async def judge(request: JudgeRequest):
    """Judge code submission"""
    
    # Execute code in Docker
    result = executor.execute(
        language=request.language,
        code=request.code,
        input_data=request.test_input
    )
    
    # Determine verdict
    if result.status == "completed":
        actual = result.output.strip()
        expected = request.expected_output.strip()
        
        if actual == expected:
            verdict = "accepted"
        else:
            verdict = "wrong_answer"
    elif result.status == "timeout":
        verdict = "time_limit_exceeded"
    elif result.status == "runtime_error":
        verdict = "runtime_error"
    else:
        verdict = "error"
    
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

## Step 5: Test via Web UI

### 5.1 Start Server

```bash
cd /Users/fajryariansyah/Documents/Kuliah/seka-judger
python3 main.py
```

### 5.2 Open Browser

```
http://localhost:8001
```

### 5.3 Test Python Code

**Code:**
```python
a = int(input())
b = int(input())
print(a + b)
```

**Input:**
```
5
3
```

**Expected Output:**
```
8
```

**Click "Judge"** → Should get "Accepted" ✅

### 5.4 Test Java Code

**Code:**
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

**Input:**
```
5 3
```

**Expected:**
```
8
```

### 5.5 Test C Code

**Code:**
```c
#include <stdio.h>
int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d", a + b);
    return 0;
}
```

---

## Step 6: Test Edge Cases

### 6.1 Test Timeout (Infinite Loop)

**Python Code:**
```python
while True:
    pass
```

**Expected:** "Time Limit Exceeded" ⏱️

### 6.2 Test Runtime Error

**Python Code:**
```python
print(1 / 0)
```

**Expected:** "Runtime Error" ❌

### 6.3 Test Wrong Answer

**Python Code:**
```python
print(999)
```

**Input:** `5\n3`
**Expected:** `8`

**Expected:** "Wrong Answer" ❌

### 6.4 Test Compilation Error (C)

**C Code:**
```c
#include <stdio.h>
int main() {
    printf("Hello"  // Missing semicolon and closing parenthesis
}
```

**Expected:** "Compilation Error" ⚠️

---

## 🔧 Troubleshooting

### Error: "docker: command not found"

**Solution:**
```bash
# Install Docker Desktop for macOS
brew install --cask docker
```

### Error: "Cannot connect to Docker daemon"

**Solution:**
```bash
# Start Docker Desktop application
open -a Docker
```

### Error: "Image not found: judger-python"

**Solution:**
```bash
# Rebuild images
cd /Users/fajryariansyah/Documents/Kuliah/seka-judger
bash build_docker_images.sh
```

### Error: "Permission denied: /code/main.py"

**Solution:**
```bash
# Check run scripts are executable
chmod +x docker/bash/*.sh
```

### Error: "Timeout after 5 seconds"

**Solution:**
```python
# Increase timeout in main.py
executor = DockerExecutor(timeout=10)  # 10 seconds
```

---

## 📊 Expected Results Summary

| Test Case | Language | Verdict | Time | Memory |
|-----------|----------|---------|------|--------|
| A+B | Python | ✅ AC | ~0.02s | ~8MB |
| A+B | C | ✅ AC | ~0.01s | ~2MB |
| A+B | C++ | ✅ AC | ~0.01s | ~3MB |
| A+B | Java | ✅ AC | ~0.3s | ~30MB |
| Infinite Loop | Python | ⏱️ TLE | 5.0s | ~8MB |
| Division by Zero | Python | ❌ RTE | ~0.02s | ~8MB |
| Wrong Output | Python | ❌ WA | ~0.02s | ~8MB |
| Syntax Error | C | ⚠️ CE | N/A | N/A |

---

## 🎉 Completion Checklist

Setelah semua step selesai, verifikasi:

- [ ] ✅ Semua 4 Docker images ter-build
- [ ] ✅ `docker images | grep judger` menunjukkan 4 images
- [ ] ✅ `core/docker_executor.py` exists
- [ ] ✅ Test Python code works
- [ ] ✅ Test C code works
- [ ] ✅ Test Java code works
- [ ] ✅ Web UI accessible di http://localhost:8001
- [ ] ✅ Accepted verdict works
- [ ] ✅ Wrong Answer detection works
- [ ] ✅ Timeout detection works
- [ ] ✅ Runtime Error detection works
- [ ] ✅ Time dan Memory metrics terukur

---

## 📚 File Structure After Implementation

```
seka-judger/
├── core/
│   ├── docker_executor.py    ← NEW! (from testing/executor.py)
│   ├── models.py
│   └── config.py
├── docker/
│   ├── c_runner.dockerfile
│   ├── cpp_runner.dockerfile
│   ├── java_runner.dockerfile
│   ├── python_runner.dockerfile
│   └── bash/
│       ├── run_c_code.sh
│       ├── run_cpp_code.sh
│       ├── run_java_code.sh
│       └── run_python_code.sh
├── main.py                    ← UPDATED!
├── build_docker_images.sh     ← NEW!
├── test_executor.py           ← NEW! (for testing)
└── IMPLEMENT_STEPS.md         ← This file
```

---

## 🚀 Quick Start Command

Jika ingin langsung jalankan semua:

```bash
# 1. Build all images
bash build_docker_images.sh

# 2. Test executor
python3 test_executor.py

# 3. Run server
python3 main.py

# 4. Open browser
open http://localhost:8001
```

---

**Selamat mengimplementasikan! 🎉**

Jika ada error, lihat section Troubleshooting di atas.
