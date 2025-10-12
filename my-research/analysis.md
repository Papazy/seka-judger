# SEKA Judger - Analisis Project & Rencana Migrasi Docker

**Tanggal Analisis**: 10 Oktober 2025  
**Status**: Production Ready untuk Development, **BELUM AMAN** untuk Production

---

## 📊 Executive Summary

SEKA Judger adalah sistem online judge berbasis FastAPI yang dapat menjalankan dan menguji kode dalam 4 bahasa pemrograman (C, C++, Java, Python). Saat ini sistem berjalan **langsung di host machine**, yang membuat sistem **SANGAT RENTAN** terhadap serangan keamanan.

### ⚠️ Critical Issues
1. **Keamanan**: Kode user dieksekusi langsung di host tanpa isolasi
2. **Resource Management**: Tidak ada batasan CPU/Memory per eksekusi
3. **File System**: User bisa mengakses file system host
4. **Network**: Tidak ada pembatasan akses network

---

## 🏗️ Arsitektur Saat Ini

### Komponen Utama

```
┌─────────────────────────────────────────────────────┐
│                   FastAPI Server                     │
│                   (Port 8000/8001)                   │
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  Web UI      │  │  Judge      │  │  Compiler  │ │
│  │  (Jinja2)    │  │  Engine     │  │  Factory   │ │
│  └──────────────┘  └─────────────┘  └────────────┘ │
│                           │                          │
│                           ▼                          │
│              ┌─────────────────────┐                │
│              │   Code Executor     │                │
│              │  (subprocess.run)   │                │
│              └─────────────────────┘                │
│                           │                          │
└───────────────────────────┼──────────────────────────┘
                            ▼
            ┌───────────────────────────────┐
            │    HOST FILE SYSTEM           │
            │  - temp/ directory            │
            │  - gcc/g++/javac/python       │
            │  - ALL HOST FILES ACCESSIBLE  │
            └───────────────────────────────┘
```

### Flow Eksekusi

1. **Request** → User submit kode + test cases via Web UI atau API
2. **Compilation** → Kode disimpan di `temp/{session_id}.ext`
3. **Execution** → Binary/script dijalankan dengan `subprocess.run()`
4. **Testing** → Output dibandingkan dengan expected output
5. **Cleanup** → Temporary files dihapus
6. **Response** → Hasil dikirim ke user

---

## 📁 Struktur Project

```
seka-judger/
│
├── main.py                     # FastAPI entry point + CORS config
├── requirements.txt            # Dependencies (fastapi, uvicorn, pydantic, pytest)
├── Dockerfile                  # Main Dockerfile (Python + all compilers)
├── README.md                   # Documentation (sudah lengkap)
│
├── core/                       # Core logic
│   ├── __init__.py
│   ├── models.py              # Pydantic models (JudgeRequest, TestCase)
│   ├── compiler.py            # Compiler abstraction (C/C++/Java/Python)
│   ├── executor.py            # Code execution dengan subprocess
│   ├── judge_engine.py        # Main judging logic + cleanup
│   └── config.py              # Empty (belum digunakan)
│
├── templates/                  # Jinja2 templates
│   └── index.html             # Web UI dengan Ace Editor
│
├── static/                     # Frontend assets
│   ├── css/style.css
│   └── js/script.js           # Editor logic + API calls
│
├── docker/                     # Dockerfiles per bahasa (KOSONG)
│   ├── c.dockerfile           # ❌ Empty
│   ├── cpp.dockerfile         # ❌ Empty
│   ├── java.dockerfile        # ❌ Empty
│   └── python.dockerfile      # ❌ Empty
│
├── experiments/                # Security testing
│   ├── security_demo.py       # Demonstrasi vulnerability
│   ├── malicious_code.py      # Kode berbahaya Python
│   ├── malicious_code.cpp     # Kode berbahaya C++
│   ├── create_test_files.py
│   └── test_security/         # Test files untuk demo
│
├── test_judge_endpoint.py     # Unit tests dengan pytest
├── example.test               # Example payloads
└── todo                       # Simple todo list
```

---

## 🔍 Analisis Detail Per Komponen

### 1. **main.py** - FastAPI Application
```python
✅ GOOD:
- FastAPI dengan CORS middleware
- Static files & templates mounting
- Error handling di /judge endpoint
- Health check endpoint

⚠️ ISSUES:
- Tidak ada rate limiting
- Tidak ada authentication
- Tidak ada request validation advanced
- Error details exposed ke client
```

### 2. **core/compiler.py** - Compiler Factory
```python
✅ GOOD:
- Abstraction pattern untuk setiap compiler
- Java class name extraction dengan regex
- Error handling pada compilation

⚠️ ISSUES:
- Semua compiler jalan di HOST
- Tidak ada resource limits
- Tidak ada sandbox
- Python compiler tidak melakukan syntax check
- Temporary files di host file system
```

**Supported Compilers:**
- **CCompiler**: gcc/g++ dengan timeout 10s
- **JavaCompiler**: javac + java runtime
- **PythonCompiler**: Direct execution tanpa compile

### 3. **core/executor.py** - Code Executor
```python
✅ GOOD:
- Timeout protection (5 detik default)
- stdout/stderr capture
- Return code checking
- Execution time measurement

⚠️ CRITICAL ISSUES:
- subprocess.run() langsung di host
- Tidak ada memory limit
- Tidak ada CPU limit
- Tidak ada network isolation
- Tidak ada file system isolation
- User code bisa akses SEMUA file host
```

### 4. **core/judge_engine.py** - Judge Engine
```python
✅ GOOD:
- Session-based dengan UUID
- Comprehensive result structure
- Output normalization (CRLF handling)
- Automatic cleanup dengan glob pattern
- Test case validation

⚠️ ISSUES:
- Cleanup bisa gagal tanpa log
- Java .class files cleanup tidak sempurna
- Tidak ada retry mechanism
```

### 5. **Frontend (templates/index.html + static/js/script.js)**
```javascript
✅ GOOD:
- Modern UI dengan Tailwind CSS
- Ace Editor integration
- Dynamic test case management
- Language-specific syntax highlighting
- Real-time result display

⚠️ ISSUES:
- Tidak ada client-side code size limit
- Tidak ada input validation
- API error tidak di-handle dengan baik
```

### 6. **Dockerfile** (Main)
```dockerfile
✅ GOOD:
- Base image: python:3.12-slim
- Installs: gcc, g++, openjdk-17-jdk, python3
- FastAPI on port 8001

⚠️ ISSUES:
- SINGLE container untuk semua bahasa (security issue)
- Tidak ada USER directive (runs as root)
- Tidak ada resource limits
- Tidak ada network isolation
```

### 7. **docker/** (Per-language Dockerfiles)
```
❌ SEMUA EMPTY - Belum diimplementasikan
```

### 8. **experiments/security_demo.py**
```python
⚠️ DEMONSTRASI KERENTANAN:
- File deletion attack
- Directory traversal
- System information gathering
- Proof of concept bahwa sistem TIDAK AMAN
```

---

## 🔒 Security Analysis

### Current Vulnerabilities (CRITICAL)

| #  | Vulnerability | Impact | Severity |
|----|---------------|--------|----------|
| 1  | **Arbitrary Code Execution** | User bisa jalankan ANY code di host | 🔴 CRITICAL |
| 2  | **File System Access** | User bisa read/write/delete host files | 🔴 CRITICAL |
| 3  | **Network Access** | User bisa buat network connections | 🟠 HIGH |
| 4  | **Resource Exhaustion** | User bisa consume all CPU/Memory | 🟠 HIGH |
| 5  | **Process Spawning** | User bisa spawn unlimited processes | 🟠 HIGH |
| 6  | **Information Disclosure** | Error messages expose system info | 🟡 MEDIUM |
| 7  | **No Rate Limiting** | API bisa di-spam | 🟡 MEDIUM |

### Attack Scenarios

#### Scenario 1: File Deletion Attack
```python
# User submits malicious Python code
code = """
import os, shutil
shutil.rmtree('/app')  # Delete entire application
# or worse: os.system('rm -rf /')
"""
```

#### Scenario 2: Data Exfiltration
```python
code = """
import os
# Read sensitive files
with open('/etc/passwd', 'r') as f:
    print(f.read())
"""
```

#### Scenario 3: Cryptomining
```cpp
// Infinite CPU consumption
int main() {
    while(1) {
        // Computational heavy task
    }
}
```

---

## 🎯 Rencana Migrasi ke Docker Architecture

### Target Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      FastAPI Server                          │
│                    (Orchestrator Container)                  │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Web UI    │  │ Judge Engine │  │ Docker Client│      │
│  └─────────────┘  └──────────────┘  └──────┬───────┘      │
│                                              │               │
└──────────────────────────────────────────────┼───────────────┘
                                               │
                    Docker Socket              │
                                               ▼
        ┌──────────────────────────────────────────────────┐
        │           Docker Engine                          │
        ├──────────────────────────────────────────────────┤
        │                                                  │
        │  ┌───────────┐  ┌───────────┐  ┌───────────┐  │
        │  │ C Runner  │  │ C++ Runner│  │ Java Runner│  │
        │  │ Container │  │ Container │  │ Container  │  │
        │  └───────────┘  └───────────┘  └───────────┘  │
        │                                                  │
        │  ┌─────────────┐                               │
        │  │Python Runner│                               │
        │  │  Container  │                               │
        │  └─────────────┘                               │
        │                                                  │
        │  🔒 Isolated                                    │
        │  🔒 Resource Limited                            │
        │  🔒 Network Disabled                            │
        │  🔒 Read-only Filesystem                        │
        └──────────────────────────────────────────────────┘
```

### Strategy: Ephemeral Containers

**Konsep:**
- Setiap submission code dijalankan di **container baru**
- Container di-**destroy** setelah eksekusi selesai
- Tidak ada persistent state di runner containers

---

## 📋 Implementation Plan

### Phase 1: Docker Client Integration (Week 1)

#### Task 1.1: Install Docker Python SDK
```bash
pip install docker
```

#### Task 1.2: Create Docker Executor
**File**: `core/docker_executor.py`
```python
import docker
from typing import Optional

class DockerExecutor:
    def __init__(self):
        self.client = docker.from_env()
    
    def execute_in_container(
        self,
        image: str,
        code: str,
        input_data: str,
        timeout: int = 5
    ) -> dict:
        """Execute code in isolated container"""
        
        container = self.client.containers.run(
            image=image,
            command=["python", "/code/main.py"],
            stdin_open=True,
            detach=True,
            mem_limit="128m",
            cpu_quota=50000,  # 50% CPU
            network_disabled=True,
            read_only=True,
            volumes={
                'code_volume': {'bind': '/code', 'mode': 'ro'}
            },
            remove=True  # Auto cleanup
        )
        
        # Execute and wait
        result = container.wait(timeout=timeout)
        output = container.logs().decode()
        
        return {
            'output': output,
            'exit_code': result['StatusCode']
        }
```

#### Task 1.3: Update Judge Engine
Modify `core/judge_engine.py` to use `DockerExecutor` instead of `CodeExecutor`

---

### Phase 2: Build Runner Images (Week 1-2)

#### Image 1: C Runner
**File**: `docker/c.dockerfile`
```dockerfile
FROM gcc:latest

# Create non-root user
RUN useradd -m -u 1000 runner && \
    mkdir -p /code /output && \
    chown -R runner:runner /code /output

WORKDIR /code
USER runner

# Copy entrypoint script
COPY docker/entrypoints/c_runner.sh /entrypoint.sh

# Resource limits via ulimit
RUN ulimit -t 5 -v 131072  # 5s CPU, 128MB memory

ENTRYPOINT ["/entrypoint.sh"]
```

**File**: `docker/entrypoints/c_runner.sh`
```bash
#!/bin/bash
set -e

# Compile
gcc /code/main.c -o /code/program

# Run with timeout
timeout 5s /code/program
```

#### Image 2: C++ Runner
**File**: `docker/cpp.dockerfile`
```dockerfile
FROM gcc:latest

RUN useradd -m -u 1000 runner && \
    mkdir -p /code /output && \
    chown -R runner:runner /code /output

WORKDIR /code
USER runner

COPY docker/entrypoints/cpp_runner.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

#### Image 3: Java Runner
**File**: `docker/java.dockerfile`
```dockerfile
FROM openjdk:17-slim

RUN useradd -m -u 1000 runner && \
    mkdir -p /code /output && \
    chown -R runner:runner /code /output

WORKDIR /code
USER runner

# Java-specific security policies
COPY docker/java.policy /etc/java.policy

ENV JAVA_TOOL_OPTIONS="-Djava.security.manager -Djava.security.policy=/etc/java.policy"

COPY docker/entrypoints/java_runner.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

**File**: `docker/java.policy`
```java
grant {
    permission java.io.FilePermission "/code/*", "read,write";
    permission java.io.FilePermission "/tmp/*", "read,write,delete";
    permission java.lang.RuntimePermission "exitVM";
};
```

#### Image 4: Python Runner
**File**: `docker/python.dockerfile`
```dockerfile
FROM python:3.12-slim

RUN useradd -m -u 1000 runner && \
    mkdir -p /code /output && \
    chown -R runner:runner /code /output

WORKDIR /code
USER runner

COPY docker/entrypoints/python_runner.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

---

### Phase 3: Security Hardening (Week 2)

#### 3.1 Container Security Config
```python
# core/docker_config.py

CONTAINER_CONFIG = {
    'mem_limit': '128m',
    'memswap_limit': '128m',
    'cpu_quota': 50000,  # 50% of one core
    'cpu_period': 100000,
    'pids_limit': 10,  # Max 10 processes
    'network_disabled': True,
    'read_only': True,
    'security_opt': ['no-new-privileges'],
    'cap_drop': ['ALL'],  # Drop all capabilities
    'tmpfs': {
        '/tmp': 'size=10m,mode=1777'  # 10MB temp space
    }
}
```

#### 3.2 Resource Monitoring
```python
# core/monitor.py

class ResourceMonitor:
    def monitor_container(self, container_id):
        stats = container.stats(stream=False)
        
        return {
            'memory_usage': stats['memory_stats']['usage'],
            'cpu_percent': self.calculate_cpu_percent(stats),
            'network_rx': stats['networks']['eth0']['rx_bytes'],
            'network_tx': stats['networks']['eth0']['tx_bytes']
        }
```

#### 3.3 Input Validation
```python
# core/validators.py

MAX_CODE_SIZE = 50 * 1024  # 50KB
MAX_INPUT_SIZE = 10 * 1024  # 10KB
MAX_TEST_CASES = 20

def validate_request(request: JudgeRequest):
    if len(request.code) > MAX_CODE_SIZE:
        raise ValueError("Code too large")
    
    if len(request.test_cases) > MAX_TEST_CASES:
        raise ValueError("Too many test cases")
    
    for tc in request.test_cases:
        if len(tc.input) > MAX_INPUT_SIZE:
            raise ValueError("Input too large")
```

---

### Phase 4: Testing & Deployment (Week 3)

#### 4.1 Build All Images
```bash
# Build script
docker build -f docker/c.dockerfile -t seka-judge-c:latest .
docker build -f docker/cpp.dockerfile -t seka-judge-cpp:latest .
docker build -f docker/java.dockerfile -t seka-judge-java:latest .
docker build -f docker/python.dockerfile -t seka-judge-python:latest .
```

#### 4.2 Docker Compose Setup
**File**: `docker-compose.yml`
```yaml
version: '3.8'

services:
  judge-api:
    build: .
    ports:
      - "8001:8001"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - DOCKER_MODE=enabled
      - RUNNER_IMAGE_PREFIX=seka-judge-
    depends_on:
      - redis
    restart: unless-stopped
  
  redis:
    image: redis:alpine
    restart: unless-stopped
    
  # Pre-build runner images
  c-runner:
    build:
      context: .
      dockerfile: docker/c.dockerfile
    image: seka-judge-c:latest
    command: "true"  # Just build, don't run
    
  cpp-runner:
    build:
      context: .
      dockerfile: docker/cpp.dockerfile
    image: seka-judge-cpp:latest
    command: "true"
    
  java-runner:
    build:
      context: .
      dockerfile: docker/java.dockerfile
    image: seka-judge-java:latest
    command: "true"
    
  python-runner:
    build:
      context: .
      dockerfile: docker/python.dockerfile
    image: seka-judge-python:latest
    command: "true"
```

#### 4.3 Integration Tests
```python
# test_docker_integration.py

class TestDockerIntegration:
    def test_secure_execution(self):
        """Test that malicious code is contained"""
        malicious_code = """
import os
try:
    os.system('rm -rf /')
    print("EXPLOITED")
except:
    print("BLOCKED")
"""
        result = docker_executor.execute(malicious_code)
        assert "BLOCKED" in result['output']
```

---

## 📊 Performance Considerations

### Current Performance
- **Compile Time**: 0.1-0.5s (C/C++), 0.5-1s (Java)
- **Execution Time**: <0.1s per test case
- **Total**: ~1-2s per submission

### Docker Performance Impact
- **Container Startup**: +0.3-0.5s
- **Image Pull**: One-time (cached)
- **Volume Mount**: Minimal overhead
- **Network Isolation**: No impact (disabled)

### Optimization Strategies
1. **Pre-warm Containers**: Keep pool of ready containers
2. **Image Caching**: Use local registry
3. **Concurrent Execution**: Run test cases in parallel
4. **Resource Pooling**: Reuse containers when safe

---

## 💰 Resource Requirements

### Current (Host-based)
- **CPU**: Unbounded
- **Memory**: Unbounded
- **Disk**: temp/ folder only
- **Network**: Full access

### After Docker Migration
Per Container:
- **CPU**: 0.5 cores (50%)
- **Memory**: 128MB
- **Disk**: 10MB tmpfs
- **Network**: Disabled

Server Requirements:
- **CPU**: 4+ cores (untuk concurrent execution)
- **Memory**: 4GB+ (32 containers = 4GB)
- **Disk**: 10GB (images + logs)
- **Docker**: 20.10+

---

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] Build all runner images
- [ ] Test security with malicious code
- [ ] Performance benchmarking
- [ ] Load testing (concurrent requests)
- [ ] Documentation update

### Deployment
- [ ] Deploy with docker-compose
- [ ] Configure reverse proxy (nginx)
- [ ] Setup SSL certificates
- [ ] Configure monitoring (Prometheus/Grafana)
- [ ] Setup logging (ELK stack)

### Post-deployment
- [ ] Monitor resource usage
- [ ] Check security logs
- [ ] Performance monitoring
- [ ] User feedback collection

---

## 📈 Monitoring & Logging

### Metrics to Track
```
- Container creation rate
- Container failure rate
- Average execution time
- Memory usage per container
- CPU usage per container
- Queue depth
- API response time
```

### Logging Strategy
```python
import logging

logger = logging.getLogger('seka-judge')

# Log every execution
logger.info(f"Executing code", extra={
    'session_id': session_id,
    'language': language,
    'container_id': container.id,
    'user_ip': request.client.host
})
```

---

## 🎓 Migration Steps (Summary)

### Step-by-Step Guide

1. **Install Docker Python SDK**
   ```bash
   pip install docker
   ```

2. **Create Dockerfiles** (c, cpp, java, python)
   - See Phase 2 above

3. **Build Images**
   ```bash
   ./scripts/build_images.sh
   ```

4. **Implement DockerExecutor**
   - Create `core/docker_executor.py`
   - Update `core/judge_engine.py`

5. **Add Security Configs**
   - Create `core/docker_config.py`
   - Add resource limits

6. **Test Security**
   ```bash
   python experiments/security_demo.py
   ```

7. **Deploy**
   ```bash
   docker-compose up -d
   ```

---

## 🔮 Future Enhancements

### Short-term (1-2 months)
- [ ] Rate limiting (per IP/user)
- [ ] User authentication & JWT
- [ ] Queue system (Redis + Celery)
- [ ] WebSocket for real-time results
- [ ] Code plagiarism detection

### Medium-term (3-6 months)
- [ ] More languages (Go, Rust, JavaScript)
- [ ] Custom judge (special checker)
- [ ] Contest mode
- [ ] Leaderboard system
- [ ] Problem database

### Long-term (6-12 months)
- [ ] Kubernetes deployment
- [ ] Auto-scaling
- [ ] Multi-region deployment
- [ ] CDN for static assets
- [ ] Machine learning for difficulty rating

---

## 📝 Conclusion

### Current State
✅ **Working**: Basic judge functionality  
❌ **Security**: CRITICAL vulnerabilities  
⚠️ **Production**: NOT READY

### After Docker Migration
✅ **Security**: Isolated execution  
✅ **Resource Management**: Controlled limits  
✅ **Production**: READY (with monitoring)

### Recommendation
**IMMEDIATE ACTION REQUIRED**: Implement Docker isolation before any production use.

### Estimated Timeline
- **Phase 1-2**: 1-2 weeks (Docker integration)
- **Phase 3**: 1 week (Security hardening)
- **Phase 4**: 1 week (Testing & deployment)
- **Total**: 3-4 weeks for production-ready system

---

## 📞 Support & References

### Documentation
- Docker SDK: https://docker-py.readthedocs.io/
- FastAPI: https://fastapi.tiangolo.com/
- Security Best Practices: https://cheatsheetseries.owasp.org/

### Similar Projects
- Judge0: https://github.com/judge0/judge0
- DMOJ: https://github.com/DMOJ/online-judge
- Codeforces Polygon: https://polygon.codeforces.com/

---

**Document Version**: 1.0  
**Last Updated**: 10 Oktober 2025  
**Author**: Analysis by GitHub Copilot  
**Status**: FINAL - Ready for Implementation
