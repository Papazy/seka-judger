# 🚀 Quick Start Guide - SEKA Judger Docker Implementation

## ✅ Pre-requisites Checklist

- [ ] Docker installed dan running (`docker --version`)
- [ ] Python 3.12+ installed
- [ ] Git repository cloned
- [ ] Terminal access

---

## 📝 Step-by-Step Implementation

### 1️⃣ Install Dependencies
```bash
cd /Users/fajryariansyah/Documents/Kuliah/seka-judger
pip install docker
```

### 2️⃣ Make Scripts Executable
```bash
chmod +x build_docker_images.sh
chmod +x test_docker_containers.sh
```

### 3️⃣ Build Docker Images
```bash
./build_docker_images.sh
```

**Expected output:**
```
🚀 Building SEKA Judger Docker Images...
📦 Building seka-judger-c:latest...
✅ Successfully built seka-judger-c:latest
...
✅ All images built successfully!
```

### 4️⃣ Verify Images
```bash
docker images | grep seka-judger
```

**Should show 4 images:**
- seka-judger-c:latest
- seka-judger-cpp:latest
- seka-judger-java:latest
- seka-judger-python:latest

### 5️⃣ Test Containers Manually
```bash
./test_docker_containers.sh
```

**Expected output:**
```
🧪 Testing SEKA Judger Docker Containers
Testing C container...
✅ C test PASSED (output: 15)
...
🎉 All tests completed!
```

### 6️⃣ Backup Original Judge Engine
```bash
cp core/judge_engine.py core/judge_engine.py.backup
```

### 7️⃣ Update Judge Engine
```bash
cp core/judge_engine_docker.py core/judge_engine.py
```

### 8️⃣ Start Application
```bash
python -m uvicorn main:app --reload --port 8001
```

### 9️⃣ Test API

**Terminal 1 (server running):**
```bash
python -m uvicorn main:app --reload --port 8001
```

**Terminal 2 (test API):**
```bash
# Test C
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

**Expected response:**
```json
{
  "status": "finished",
  "total_case": 2,
  "total_case_benar": 2,
  "results": [
    {
      "test_case": 1,
      "input": "5 10",
      "expected_output": "15",
      "actual_output": "15",
      "passed": true,
      "status": "accepted",
      "execution_time": 0.02,
      "memory_used": 1234
    },
    ...
  ]
}
```

### 🔟 Test via Web Interface

1. Open browser: `http://localhost:8001`
2. Select language: `C`
3. Paste code:
```c
#include <stdio.h>
int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d", a + b);
    return 0;
}
```
4. Add test case:
   - Input: `5 10`
   - Expected: `15`
5. Click "Submit Code"
6. Check results ✅

---

## 🐛 Troubleshooting

### Problem: Docker not running
```bash
# MacOS
open -a Docker

# Linux
sudo systemctl start docker
```

### Problem: Permission denied
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Problem: Image not found
```bash
# Rebuild images
./build_docker_images.sh
```

### Problem: Container timeout
Edit `core/docker_executor.py`:
```python
self.timeout = 10  # Increase timeout
```

---

## 📊 Monitoring

### View Running Containers
```bash
docker ps
```

### View Container Logs
```bash
docker logs <container_id>
```

### Monitor Resources
```bash
docker stats
```

### Cleanup
```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -f
```

---

## ✅ Success Criteria

- [ ] All 4 Docker images built successfully
- [ ] All container tests pass
- [ ] API returns correct results
- [ ] Web interface works
- [ ] No permission errors
- [ ] Timeout works correctly
- [ ] Resource limits enforced

---

## 🎯 Next Steps After Implementation

1. **Security Audit**: Review container security settings
2. **Performance Testing**: Load test dengan multiple submissions
3. **Monitoring Setup**: Add logging and metrics
4. **Documentation**: Update API docs
5. **Deployment**: Deploy to production server

---

## 📚 Files Created/Modified

**New Files:**
- `implement.md` - Full implementation guide
- `QUICK_START.md` - This file
- `build_docker_images.sh` - Build script
- `test_docker_containers.sh` - Test script
- `core/docker_executor.py` - Docker executor
- `core/judge_engine_docker.py` - Updated judge engine

**Modified Files:**
- `requirements.txt` - Added docker SDK
- `core/judge_engine.py` - (backup created)

---

## 🆘 Need Help?

1. Check `implement.md` for detailed explanations
2. Check Docker logs: `docker logs <container_id>`
3. Check application logs
4. Verify all files are in correct locations
5. Ensure all scripts have execute permissions

---

**Last Updated:** 2025-10-11  
**Status:** Ready for Implementation ✅
